
import os
import sys
import functools
import logging
import platform
import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location import accessor
from ftrack_perforce_location import resource_transformer
from ftrack_perforce_location import structure
from ftrack_perforce_location.constants import (
    SCENARIO_ID,
    SCENARIO_DESCRIPTION,
    SCENARIO_LABEL,
)
from ftrack_perforce_location.perforce_handlers import errors
from ftrack_perforce_location.perforce_handlers.change import PerforceChangeHandler
from ftrack_perforce_location.perforce_handlers.connection import (
    PerforceConnectionHandler,
)
from ftrack_perforce_location.perforce_handlers.errors import PerforceValidationError
from ftrack_perforce_location.perforce_handlers.file import PerforceFileHandler
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler

logger = logging.getLogger('ftrack_perforce_location.configure_location')

location_data = {}


def configure_location(session, event):
    '''Listen.'''
    logger.info('Configuring Perforce Location')
    perforce_settings = PerforceSettingsHandler(session)
    perforce_settings_data = perforce_settings.read()
    user_settings_values = list(perforce_settings_data.values())

    logger.info(user_settings_values)
    perforce_settings.update_port_from_scenario(
        perforce_settings_data, location_data
    )

    stored_pass =  os.getenv('P4PASSWD')
    if stored_pass:
        logger.info('Setting password from Environments.')
        perforce_settings_data['password'] = stored_pass

    perforce_connection_handler = PerforceConnectionHandler(
        **perforce_settings_data
    )


    perforce_change_handler = PerforceChangeHandler(perforce_connection_handler)

    perforce_file_handler = PerforceFileHandler(
        perforce_change_handler=perforce_change_handler
    )

    location = session.ensure(
        'Location',
        {
            'name': SCENARIO_ID,
            'label': SCENARIO_LABEL,
            'description': SCENARIO_DESCRIPTION,
        },
        identifying_keys=['name'],
    )

    typemaps = session.event_hub.publish(
        ftrack_api.event.base.Event(topic="ftrack.perforce.typemap.register"),
        synchronous=True,
    )
    typemap = {k: v for d in typemaps if d for k, v in list(d.items())}

    location.accessor = accessor.PerforceAccessor(
        perforce_file_handler=perforce_file_handler, typemap=typemap
    )
    location.structure = structure.PerforceStructure(
        perforce_file_handler=perforce_file_handler,
    )

    location.resource_identifier_transformer = (
        resource_transformer.PerforceResourceIdentifierTransformer(
            session, perforce_file_handler=perforce_file_handler
        )
    )

    location.priority = 0


def register(api_object, **kw):
    '''Register location with *session*.'''

    if not isinstance(api_object, ftrack_api.Session):
        return

    api_object.event_hub.subscribe(
        'topic=ftrack.api.session.configure-location',
        functools.partial(configure_location, api_object)
    )