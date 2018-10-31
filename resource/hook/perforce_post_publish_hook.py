import ftrack_api
from ftrack_api.symbol import (
    ORIGIN_LOCATION_ID,
    UNMANAGED_LOCATION_ID,
    REVIEW_LOCATION_ID,
    CONNECT_LOCATION_ID,
    SERVER_LOCATION_ID,
    COMPONENT_ADDED_TO_LOCATION_TOPIC
)
import functools
import logging

logger = logging.getLogger(
    'ftrack_perforce_location.perforce_post_publish_hook'
)

excluded_location_ids = [
    ORIGIN_LOCATION_ID,
    UNMANAGED_LOCATION_ID,
    REVIEW_LOCATION_ID,
    CONNECT_LOCATION_ID,
    SERVER_LOCATION_ID
]


def my_callback(session, event):
    '''Event callback printing all new or updated entities.'''

    location_id = event['data'].get('location_id')
    if not location_id or location_id in excluded_location_ids:
        return

    component_id = event['data'].get('component_id')
    perforce_location = session.get('Location', location_id)
    perforce_component = session.get('Component', component_id)

    perforce_path = perforce_location.get_filesystem_path(perforce_component)
    logger.info('Publishing {} to perforce'.format(perforce_path))

    # PUBLISH RESULT FILE IN PERFORCE
    perforce_location.accessor.perforce_file_handler.change.submit(
        perforce_path, 'published with ftrack'
    )


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return


    event_handler = functools.partial(
        my_callback, api_object
    )

    api_object.event_hub.subscribe(
        'topic={}'.format(COMPONENT_ADDED_TO_LOCATION_TOPIC),
        event_handler
    )