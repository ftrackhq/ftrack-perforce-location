# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import functools
import json
import logging
import os
import sys

from ftrack_api.symbol import COMPONENT_ADDED_TO_LOCATION_TOPIC
import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

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
    try:
        # collect location
        location_id = event['data'].get('location_id')
        perforce_location = session.get('Location', location_id)

        # collect component
        component_id = event['data'].get('component_id')
        component = session.get('Component', component_id)

        # store initial states
        change = None
        file_path = None

        # check components we are about to publish
        component_is_in_container = component['container']
        component_is_container = isinstance(
            component, session.types['SequenceComponent']
        )

        # get the project id,and potentially a change
        if component_is_in_container:
            project_id = component['container']['version']['link'][0]['id']

            # if the component is in a container
            # check the container for the current change set
            try:
                change = component['container']['metadata'].get('change')
            except ValueError as error:
                logger.error(error)
                pass
        else:
            change = component['metadata'].get('change')
            project_id = component['version']['link'][0]['id']

        logger.info('post publish for :{}, iscontainer :{} , isincontainer: {}, has change: {}'.format(
            component, component_is_container, component_is_in_container, change))

        project = session.query(
            'select id, name from Project where id is "{0}"'.format(project_id)
        ).one()

        storage_scenario = session.query(
            'select value from Setting '
            'where name is "storage_scenario" and group is "STORAGE"'
        ).one()

        # check if we require one depot per project
        configuration = json.loads(storage_scenario['value'])
        location_data = configuration.get('data', {})
        require_one_depot_per_project = location_data.get(
            'one_depot_per_project', False
        )

        if require_one_depot_per_project:
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
                    error_message = (
                        'Cannot checkin {}.\n'
                        'Project {} requires its own depot.'.format(
                            file_path, project['name']
                        )
                    )
                    raise PerforceValidationError(error_message)

        # we don't want to publish the sequence representation itself
        if not component_is_container:
            file_path = perforce_location.get_filesystem_path(component)

        if file_path:
            change = perforce_location.accessor.perforce_file_handler.change.add(
                change, file_path, 'published with ftrack',
            )

            logger.info(
                'Added  {} to change {}'.format(
                    file_path, change
                )
            )

        if component_is_in_container and change:
            # add change to current container, so can later be retrieved
            logger.info('adding change {} as metadata to {}'.format(
                change, component['container'])
            )
            component['container']['metadata']['change'] = change
            session.commit()

        # If there's a valid change and the component is either without container (single file)
        # or is the container itself, submit the changes to perforce
        if (
            change and (component_is_container or not component_is_in_container)
        ):
            logger.info('Submitting change {}'.format(change))
            perforce_location.accessor.perforce_file_handler.change.submit(change)


    except Exception as error:
        logger.error(error)


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
    logger.debug('registering post publish hook for location {}'.format(
        SCENARIO_ID)
    )

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
