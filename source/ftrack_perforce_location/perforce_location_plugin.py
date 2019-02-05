# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import functools
import logging

import ftrack_api
import ftrack_api.accessor.disk

from ftrack_perforce_location import perforce_accessor
from ftrack_perforce_location import perforce_resource_transformer
from ftrack_perforce_location import perforce_scenario
from ftrack_perforce_location import perforce_structure

from ftrack_perforce_location.perforce_handlers.connection import PerforceConnectionHandler
from ftrack_perforce_location.perforce_handlers.file import PerforceFileHandler
from ftrack_perforce_location.perforce_handlers.change import PerforceChangeHandler
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler

logger = logging.getLogger(
    'ftrack_perforce_location.perforce_location_plugin'
)

# Name of the location plugin.
LOCATION_NAME = 'perforce_local_workspace'
LOCATION_LABEL = 'Perforce'
LOCATION_DESCRIPTION = ('Perforce allows ftrack to publish to and import from '
                        'a Perforce depot through a user\'s local workspace.')

perforce_settings = PerforceSettingsHandler()
perforce_settings_data = perforce_settings.read()


def configure_location(session, event):
    '''Configure perforce location.'''

    location = session.ensure(
        'Location',
        {
            'name': LOCATION_NAME,
            'label': LOCATION_LABEL,
            'description': LOCATION_DESCRIPTION
        },
        identifying_keys=['name']
    )

    perforce_connection_handler = PerforceConnectionHandler(
        **perforce_settings_data
    )

    perforce_change_handler = PerforceChangeHandler(
        perforce_connection_handler
    )

    perforce_file_handler = PerforceFileHandler(
        perforce_change_handler=perforce_change_handler
    )

    location.accessor = perforce_accessor.PerforceAccessor(
        perforce_file_handler=perforce_file_handler
    )
    location.structure = perforce_structure.PerforceStructure(
        perforce_file_handler=perforce_file_handler,
    )

    location.resource_identifier_transformer = perforce_resource_transformer.PerforceResourceIdentifierTransformer(
        session, perforce_file_handler=perforce_file_handler
    )

    location.priority = 1


def register(api_object, **kw):
    '''Register location with *session*.'''

    if not isinstance(api_object, ftrack_api.Session):
        return

    api_object.event_hub.subscribe(
        'topic=ftrack.api.session.configure-location',
        functools.partial(configure_location, api_object)
    )
