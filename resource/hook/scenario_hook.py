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
from ftrack_perforce_location.constants import SCENARIO_ID, SCENARIO_NAME, SCENARIO_DESCRIPTION

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import structure


logger = logging.getLogger(
    __name__
)


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
            'name': SCENARIO_NAME,
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

# Settings we might want: server, depot/workspace (root?), whether to create
# new depots,


# TODO(spetterborg) Session registers Central storage with itself, then sends
# activate to configured scenario in another function. The Activate call causes
# the location (still running in the API, so, local) to create the location in
# the session, but with the reconstructing option, which is weird. Some
# settings are set.
class ActivatePerforceStorageScenario(object):
    '''Activate a storage scenario using Perforce.'''

    def __init__(self):
        '''Instansiate Perforce storage scenario.'''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def _verify_startup(self, event):
        '''Verify the storage scenario configuration.'''
        # TODO(spetterborg) One place to check the workspace mappings.
        # Called by Connect
        pass

    def activate(self, event):
        # Called by ftrack_api, but no response needed.
        storage_scenario = event['data']['storage_scenario']

        try:
            location_data = storage_scenario['data']

        except KeyError:
            error_message = (
                'Unable to read storage scenario data.'
            )
            self.logger.error(L(error_message))
            raise ftrack_api.exception.LocationError(
                'Unable to configure location based on scenario.'
            )

        else:

            location = self.session.create(
                'Location',
                data=dict(
                    name=SCENARIO_NAME,
                    id=SCENARIO_ID
                ),
                reconstructing=True
            )
            perforce_settings = PerforceSettingsHandler()
            perforce_settings_data = perforce_settings.read()

            server_settings = {
                'host': location_data['host'],
                'port': location_data['port']
            }

            if location_data['use_ssl']:
                server_settings['port'] = 'ssl:{}'.format(
                    location_data['port'])

            perforce_settings_data.update(server_settings)

            perforce_connection_handler = PerforceConnectionHandler(
                **perforce_settings_data
            )

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
                u'Storage scenario activated. Configured {0!r} from '
                u'{1!r}',
                location, perforce_settings_data
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


def register(session):
    '''Register storage scenario.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    # TODO(spetterborg) Probably remove logging in release version
    logger.info('Registering activate listener')
    scenario = ActivatePerforceStorageScenario()
    scenario.register(session)

    register_configuration(session)


def register_configuration(session):
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    '''Register storage scenario.'''
    logger.info('Registering config listener')
    scenario = ConfigurePerforceStorageScenario()
    scenario.register(session)
