# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import functools
import logging

import ftrack_api
import ftrack_api.accessor.disk

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import scenario
from ftrack_perforce_location import structure

from ftrack_perforce_location.perforce_handlers.connection import PerforceConnectionHandler
from ftrack_perforce_location.perforce_handlers.file import PerforceFileHandler
from ftrack_perforce_location.perforce_handlers.change import PerforceChangeHandler
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler
from ftrack_perforce_location.scenario import SCENARIO_ID, SCENARIO_DESCRIPTION, SCENARIO_NAME
from ftrack_perforce_location.perforce_handlers.errors import PerforceSettingsHandlerException


logger = logging.getLogger(
    __name__
)


def configure_location(session, event):
    '''Configure perforce location.'''

    location = session.ensure(
        'Location',
        {
            'name': SCENARIO_ID,
            'label': SCENARIO_NAME,
            'description': SCENARIO_DESCRIPTION
        },
        identifying_keys=['name']
    )
    try:
        perforce_settings = PerforceSettingsHandler(session, SCENARIO_ID)
        perforce_settings_data = perforce_settings.read()

    except PerforceSettingsHandlerException as error:
        logger.debug(error)
        return

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
