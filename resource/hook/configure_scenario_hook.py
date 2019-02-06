# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import sys
import json
import logging

import ftrack_api
from ftrack_api.logging import LazyLogMessage as L

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location.perforce_handlers.connection import PerforceConnectionHandler
from ftrack_perforce_location.perforce_handlers.file import PerforceFileHandler
from ftrack_perforce_location.perforce_handlers.change import PerforceChangeHandler
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler
from ftrack_perforce_location.constants import SCENARIO_ID, SCENARIO_DESCRIPTION, SCENARIO_LABEL

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import structure



logger = logging.getLogger(
    'ftrack_perforce_location.configure_scenario_hook'
)


class ConfigurePerforceStorageScenario(object):
    '''Configure a storage scenario using Perforce.'''

    def __init__(self):
        '''Instansiate Perforce storage scenario.'''
        self.logger = logging.getLogger(
            'ftrack_perforce_location.' + self.__class__.__name__
        )

    @property
    def storage_scenario(self):
        '''Return storage scenario setting.'''
        return self.session.query(
            'select value from Setting '
            'where name is "storage_scenario" and group is "STORAGE"'
        ).one()

    # TODO(spetterborg) What is this used for?
    # and is it named appropriately?
    @property
    def existing_perforce_storage_configuration(self):
        '''Return existing centralized storage configuration.'''
        storage_scenario = self.storage_scenario

        try:
            configuration = json.loads(storage_scenario['value'])
        except (ValueError, TypeError):
            return {}

        if not isinstance(configuration, dict):
            return {}

        if configuration.get('scenario') != SCENARIO_ID:
            return {}

        return configuration.get('data', {})

    def configure_scenario(self, event):
        '''Configure scenario based on *event* and return form items.'''

        steps = (
            'select_scenario',
            'select_options',
            'review_configuration',
            'save_configuration'
        )

        values = event['data'].get('values', {})

        # Get last step from the event or assume we have just started.
        previous_step = values.get('step', 'select_scenario')
        next_step = steps[steps.index(previous_step) + 1]
        state = 'configuring'

        self.logger.info(L(
            u'Configuring scenario, previous step: {0}, next step: {1}. '
            u'Values {2!r}.',
            previous_step, next_step, values
        ))

        if 'configuration' in values:
            configuration = values.pop('configuration')
        else:
            configuration = {}

        if values:
            # Update configuration with values from the previous step.
            configuration[previous_step] = values

        if next_step == 'review_configuration' and not values['host']:
            # validate host is set
            next_step = 'select_options'

        if next_step == 'select_options':

            perforce_server = self.existing_perforce_storage_configuration.get(
                'host', None)

            perforce_port = self.existing_perforce_storage_configuration.get(
                'port', '1666')

            perforce_ssl = self.existing_perforce_storage_configuration.get(
                'use_ssl', True)

            items = [
            {
                'type': 'label',
                'value': (
                    'Please provide settings for accessing the peforce server.'
                )
            }, {
                'type': 'text',
                'label': 'Perforce server name or address (P4HOST).',
                'name': 'host',
                'value': perforce_server
            }, {
                'type': 'number',
                'label': 'Perforce server port number.',
                'name': 'port',
                'value': perforce_port
            }, {
                'type': 'boolean',
                'label': 'Perforce connection uses SSL.',
                'name': 'use_ssl',
                'value': perforce_ssl
            }]

        elif next_step == 'review_configuration':
            items = [{
                'type': 'label',
                'value': (
                    '# Perforce storage is now configured with the following settings:\n\n'
                    '* **Host**: {0} \n* **Port**: {1} \n* Use **SSL** : {2}').format(
                        configuration['select_options']['host'],
                        configuration['select_options']['port'],
                        configuration['select_options']['use_ssl']
                )
            }]
            state = 'confirm'

        elif next_step == 'save_configuration':
            setting_value = json.dumps({
                'scenario': SCENARIO_ID,
                'data': {
                    'host': configuration['select_options']['host'],
                    'port': configuration['select_options']['port'],
                    'use_ssl': configuration['select_options']['use_ssl']
                }
            })

            self.storage_scenario['value'] = setting_value
            self.session.commit()

            # Broadcast an event that storage scenario has been configured.
            event = ftrack_api.event.base.Event(
                topic='ftrack.storage-scenario.configure-done'
            )
            self.session.event_hub.publish(event)

            items = [{
                'type': 'label',
                'value': (
                    '#Done!#\n'
                    'Your Perforce storage scenario is now configured and ready '
                    'to use.\n **Note that you may have to restart Connect and '
                    'other applications to start using it.**'
                )
            }]
            state = 'done'

        items.extend(({
            'type': 'hidden',
            'value': configuration,
            'name': 'configuration'
        }, {
            'type': 'hidden',
            'value': next_step,
            'name': 'step'
        }))

        return {
            'items': items,
            'state': state
        }

    def discover(self, event):
        '''Return action discover dictionary for *event*.'''
        return {
            'id': SCENARIO_ID,
            'name': SCENARIO_LABEL,
            'description': SCENARIO_DESCRIPTION
        }

    def register(self, session):
        '''Subscribe to events on *session*.'''
        self.session = session

        session.event_hub.subscribe(
            (
                u'topic=ftrack.storage-scenario.discover '
                'and source.user.username="{0}"'
            ).format(
                session.api_user
            ),
            # taking a stand against naming. To the future!
            self.discover
        )
        session.event_hub.subscribe(
            (
                u'topic=ftrack.storage-scenario.configure '
                'and data.scenario_id="{0}" '
                'and source.user.username="{1}"'
            ).format(
                SCENARIO_ID,
                session.api_user
            ),
            self.configure_scenario
        )


def register(session):
    '''Register storage scenario.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('discovering configure storage scenario')
    scenario = ConfigurePerforceStorageScenario()
    scenario.register(session)
