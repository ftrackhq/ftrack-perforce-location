# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import sys
import functools
import logging

import ftrack_api
from ftrack_api.symbol import COMPONENT_ADDED_TO_LOCATION_TOPIC

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location.constants import SCENARIO_ID
from ftrack_perforce_location.perforce_handlers.errors import (
    PerforceValidationError)
from ftrack_perforce_location.validate_workspace import WorkspaceValidator

logger = logging.getLogger(
    'ftrack_perforce_location.post_publish_hook'
)


def post_publish_callback(session, event):
    '''Event callback to publish the result file in perforce depot.'''

    location_id = event['data'].get('location_id')
    perforce_location = session.get('Location', location_id)
    connection = perforce_location.resource_identifier_transformer.connection

    component_id = event['data'].get('component_id')
    perforce_component = session.get('Component', component_id)

    perforce_path = perforce_location.get_filesystem_path(perforce_component)
    logger.info('Publishing {} to perforce'.format(perforce_path))

    project_name = [link for link
                    in perforce_component['version']['link']
                    if link['type'] == 'Project'][0]['name']

    storage_scenario = session.query(
        'select value from Setting '
        'where name is "storage_scenario" and group is "STORAGE"'
    ).one()
    require_one_depot_per_project = storage_scenario.get(
        'one_depot_per_project', False
    )
    if require_one_depot_per_project:
        project_list = storage_scenario.get('one_depot_per_project', [])
        if ((len(project_list) == 0 or project_name in project_list) and
                not project_has_own_depot(connection, project_name)):
            error_message = (
                'Cannot checkin {}. Project {} requires its own depot.'.format(
                    perforce_path, project_name
                )
            )
            raise PerforceValidationError(error_message)

    # PUBLISH RESULT FILE IN PERFORCE
    perforce_location.accessor.perforce_file_handler.change.submit(
        perforce_path, 'published with ftrack'
    )


def project_has_own_depot(connection, project_name):
    # TODO Sanitise project_name for filesystem.
    project_list = [{'name': project_name}]
    validator = WorkspaceValidator(connection, project_list)
    try:
        validator.validate_one_depot_per_project()
    except PerforceValidationError as error:
        logger.warning(
            'Workspace validation failed for project {}:\n{}'.format(
                project_name, error)
        )
        return False

    return True


def _register(event, session=None):
    '''Register plugin to api_object.'''

    event_handler = functools.partial(
        post_publish_callback, session
    )

    location = session.query(
        'Location where name is "{}"'.format(SCENARIO_ID)
    ).first()

    if not location:
        logger.debug('Location {} not found'.format(SCENARIO_ID))
        return

    location_id = location['id']
    logger.debug('registering post publish hook for location {}'.format(SCENARIO_ID))

    session.event_hub.subscribe(
        'topic={0} and data.location_id="{1}"'.format(
            COMPONENT_ADDED_TO_LOCATION_TOPIC, location_id
        ),
        event_handler
    )


def register(api_object, **kw):
    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.

    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    api_object.event_hub.subscribe(
        'topic=ftrack.api.session.ready',
        functools.partial(_register, session=api_object)
    )
