# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import sys
import json
import logging

import ftrack_api
from ftrack_api.logging import LazyLogMessage as L

from ftrack_perforce_location.perforce_handlers.connection import PerforceConnectionHandler
from ftrack_perforce_location.perforce_handlers.file import PerforceFileHandler
from ftrack_perforce_location.perforce_handlers.change import PerforceChangeHandler
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler
from ftrack_perforce_location.constants import SCENARIO_ID, SCENARIO_DESCRIPTION, SCENARIO_LABEL
from ftrack_perforce_location.perforce_handlers import errors

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import structure


class ConfigurePerforceStorageScenario(object):
    '''Configure a storage scenario using Perforce.'''

    def __init__(self):
        '''Instansiate Perforce storage scenario.'''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
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

        if 'configuration' in values:
            configuration = values.pop('configuration')
        else:
            configuration = {}

        if values:
            # Update configuration with values from the previous step.
            configuration[previous_step] = values

        if next_step == 'review_configuration' and not values['server']:
            # validate server is set
            next_step = 'select_options'

        if next_step == 'select_options':

            perforce_server = self.existing_perforce_storage_configuration.get(
                'server', '127.0.0.1')

            perforce_port = self.existing_perforce_storage_configuration.get(
                'port_number', '1666')

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
                'label': 'Perforce server name or address.',
                'name': 'server',
                'value': perforce_server
            }, {
                'type': 'number',
                'label': 'Perforce server port number.',
                'name': 'port_number',
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
                    '* **Server**: {0} \n* **Port**: {1} \n* Use **SSL** : {2}').format(
                        configuration['select_options']['server'],
                        configuration['select_options']['port_number'],
                        configuration['select_options']['use_ssl']
                )
            }]
            state = 'confirm'

        elif next_step == 'save_configuration':
            setting_value = json.dumps({
                'scenario': SCENARIO_ID,
                'data': {
                    'server': configuration['select_options']['server'],
                    'port_number': configuration['select_options']['port_number'],
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


class ActivatePerforceStorageScenario(object):
    '''Activate a storage scenario using Perforce.'''

    def __init__(self):
        '''Instansiate Perforce storage scenario.'''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def _connect_to_perforce(self, event):
        '''Create a new perforce connection and raise any issue.'''
        storage_scenario = event['data']['storage_scenario']

        try:
            location_data = storage_scenario['data']

        except KeyError:
            error_message = (
                'Unable to read storage scenario data.'
            )
            self.logger.error(L(error_message))
            raise errors.PerforceConnectionHandlerException(
                'Unable to configure location based on scenario.'
            )

        else:
            perforce_settings = PerforceSettingsHandler()
            perforce_settings_data = perforce_settings.read()

            if location_data['use_ssl']:
                perforce_settings_data['port'] = 'ssl:{}:{}'.format(
                    location_data['server'],
                    location_data['port_number']
                )
            else:
                perforce_settings_data['port'] = 'tcp:{}:{}'.format(
                    location_data['server'],
                    location_data['port_number']
                )

            try:
                perforce_connection_handler = PerforceConnectionHandler(
                    **perforce_settings_data
                )
            except Exception as error:
                self.logger.error(L(str(error)))
                error = str(error).split('[Error]:')[-1]
                error = 'Perforce Error: {}'.format(error)
                raise errors.PerforceConnectionHandlerException(error)

            return perforce_connection_handler

    def _verify_startup(self, event):
        '''Verify the storage scenario configuration.'''
        # TODO(spetterborg) One place to check the workspace mappings.
        # Called by Connect
        try:
            self._connect_to_perforce(event)
        except errors.PerforceConnectionHandlerException as error:
            return unicode(error)

    def activate(self, event):

            location = self.session.ensure(
                'Location',
                {
                    'name': SCENARIO_ID,
                    'label': SCENARIO_LABEL,
                    'description': SCENARIO_DESCRIPTION
                },
                identifying_keys=['name']
            )

            perforce_connection_handler = self._connect_to_perforce(event)

            perforce_change_handler = PerforceChangeHandler(
                perforce_connection_handler
            )

            perforce_file_handler = PerforceFileHandler(
                perforce_change_handler=perforce_change_handler
            )

            location.accessor = accessor.PerforceAccessor(
                perforce_file_handler=perforce_file_handler
            )
            location.structure = structure.PerforceStructure(
                perforce_file_handler=perforce_file_handler,
            )

            location.resource_identifier_transformer = resource_transformer.PerforceResourceIdentifierTransformer(
               self.session, perforce_file_handler=perforce_file_handler
            )

            location.priority = 0

            self.logger.info(L(
                u'Storage scenario activated. Configured {0!r}',
                location['name']
            ))

    def register(self, session):
        '''Subscribe to events on *session*.'''
        self.session = session

        session.event_hub.subscribe(
            (
                'topic=ftrack.storage-scenario.activate '
                'and data.storage_scenario.scenario="{0}"'.format(
                    SCENARIO_ID
                )
            ),
            self.activate
        )

        # Listen to verify startup event from ftrack connect to allow
        # responding with a message if something is not working correctly with
        # this scenario that the user should be notified about.
        self.session.event_hub.subscribe(
            (
                'topic=ftrack.connect.verify-startup '
                'and data.storage_scenario.scenario="{0}"'.format(
                    SCENARIO_ID
                )
            ),
            self._verify_startup
        )
