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

logger = logging.getLogger(
    'ftrack_perforce_location.post_publish_hook'
)


def post_publish_callback(session, event):
    '''Event callback to publish the result file in perforce depot.'''

    location_id = event['data'].get('location_id')
    perforce_location = session.get('Location', location_id)

    component_id = event['data'].get('component_id')
    perforce_component = session.get('Component', component_id)

    perforce_path = perforce_location.get_filesystem_path(perforce_component)
    logger.info('Publishing {} to perforce'.format(perforce_path))

    # PUBLISH RESULT FILE IN PERFORCE
    perforce_location.accessor.perforce_file_handler.change.submit(
        perforce_path, 'published with ftrack'
    )


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
