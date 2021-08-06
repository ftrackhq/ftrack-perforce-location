# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import functools
import logging
import os
import sys

import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

logger = logging.getLogger(
    'ftrack_perforce_location.post_publish_hook'
)
from ftrack_perforce_location import post_publish


def register(api_object, **kw):
    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.

    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('Discovering post publish hook from {}'.format(__file__))

    api_object.event_hub.subscribe(
        'topic=ftrack.api.session.ready',
        functools.partial(post_publish._register, session=api_object)
    )
