# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import functools
import json
import logging
import os
import sys

from ftrack_api.symbol import COMPONENT_ADDED_TO_LOCATION_TOPIC
import ftrack_api

from ftrack_perforce_location.constants import SCENARIO_ID
from ftrack_perforce_location.perforce_handlers.errors import (
    PerforceValidationError
)
from ftrack_perforce_location.validate_workspace import WorkspaceValidator


logger = logging.getLogger(
    'ftrack_perforce_location.post_publish_hook'
)


def post_publish_callback(session, event):
    '''Event callback to publish the result file in Perforce depot.'''
    location_id = event['data'].get('location_id')
    perforce_location = session.get('Location', location_id)

    component_id = event['data'].get('component_id')
    component = session.get('Component', component_id)
    component_is_in_container = bool(component['container'])
    component_is_container = isinstance(
        component, session.types['SequenceComponent']
    )

    # either get the container of the component itself
    root_component = component['container'] or component

    # get the change number
    change = root_component['metadata'].get('change')

    # get the version comment
    comment = root_component['version'].get('comment', 'Published with ftrack')

    # extract project id from root_component
    project_id = root_component['version']['link'][0]['id']

    logger.debug(
        'post publish for: {0},'
        ' iscontainer: {1} ,'
        ' isincontainer: {2}, '
        'has change: {3}'.format(
            component, component_is_container, component_is_in_container, change
        )
    )

    file_path = None
    if not component_is_container:
        file_path = perforce_location.get_filesystem_path(component)

    if _require_one_depot_per_project(session):
        project = session.query(
            'select id, name from Project where id is "{0}"'.format(project_id)
        ).one()
        try:
            _validate_depot_for_project(session, project, perforce_location)
        except PerforceValidationError:
            error_message = (
                'Cannot checkin {0}.\n'
                'Project {1} requires its own depot.'.format(
                    file_path, project['name']
                )
            )
            raise PerforceValidationError(error_message)

    if file_path:
        change = perforce_location.accessor.perforce_file_handler.change.add(
            change, file_path, comment,
        )

    # We should only get here with a SequenceComponent with no
    # FileComponent members
    if not change:
        return

    if component_is_in_container:
        # Add change to current container temporarily
        logger.debug('Adding change {0} as metadata to {1}'.format(
            change, root_component)
        )
        root_component['metadata']['change'] = change

    # If there's a valid change and the component has no container (single file)
    # or is the container itself, submit the changes to Perforce
    if component_is_container or not component_is_in_container:
        perforce_location.accessor.perforce_file_handler.change.submit(change)
        if component_is_container:
            # Once we submit the change remove the pending change from metadata
            logger.debug(
                'removing change: {0} from {1} metadata'.format(
                    change, component)
            )
            component['metadata'].pop('change', None)


def _require_one_depot_per_project(session):
    '''Determine whether this Project requires its own depot.'''
    storage_scenario = session.query(
        'select value from Setting '
        'where name is "storage_scenario" and group is "STORAGE"'
    ).one()

    # Check whether require one depot per project
    configuration = json.loads(storage_scenario['value'])
    location_data = configuration.get('data', {})
    require_one_depot_per_project = location_data.get(
        'one_depot_per_project', False
    )
    return require_one_depot_per_project


def _validate_depot_for_project(session, project, perforce_location):
    '''Setup and run workspace validation.

       With a combination of server-wide and project-specific settings,
       we can require that a particular Project has its own Perforce
       depot, so that it may be split out and archived later.
    '''

    # Avoid stale cached values
    del project['custom_attributes']
    session.populate(project, 'custom_attributes')

    if project['custom_attributes'].get('own_perforce_depot', False):
        connection = (
            perforce_location.resource_identifier_transformer.connection
        )
        try:
            sanitise_function = (
                perforce_location.structure.sanitise_for_filesystem
            )
        except AttributeError:
            sanitise_function = None
        validator = WorkspaceValidator(
            connection, [project], sanitise_function
        )
        try:
            validator.validate_one_depot_per_project()
        except PerforceValidationError as error:
            logger.warning(
                'Workspace validation failed for project {}:\n{}'.format(
                    project['name'], error)
            )
            raise


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
    logger.debug('Registering post publish hook for location {}'.format(
        SCENARIO_ID)
    )

    session.event_hub.subscribe(
        'topic={0} and data.location_id="{1}"'.format(
            COMPONENT_ADDED_TO_LOCATION_TOPIC, location_id
        ),
        event_handler
    )
