# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import os
import sys

import ftrack_api

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location.depot_attribute_action import (
    PerforceAttributeAction
)

logger = logging.getLogger(
    'ftrack_perforce_location.perforce_attribute_action_hook'
)


def register(session):
    '''Register Perforce attribute action with an ftrack_api *session*.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again in the old API.
        return

    logger.info('Discovering perforce attribute action')
    action = PerforceAttributeAction(session)
    action.register()
