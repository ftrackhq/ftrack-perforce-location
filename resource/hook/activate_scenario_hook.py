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
from ftrack_perforce_location.constants import SCENARIO_ID, SCENARIO_DESCRIPTION

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import structure


logger = logging.getLogger(
    'ftrack_perforce_location.activate_scenario_hook'
)


class ActivatePerforceStorageScenario(object):
    '''Activate a storage scenario using Perforce.'''

    def __init__(self):
        '''Instansiate Perforce storage scenario.'''
        self.logger = logging.getLogger(
           'ftrack_perforce_location.' + self.__class__.__name__
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
                    name=SCENARIO_ID,
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
                location['name'], perforce_settings_data
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
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    '''Register storage scenario.'''
    logger.info('discovering activate storage scenario')
    scenario = ActivatePerforceStorageScenario()
    scenario.register(session)
