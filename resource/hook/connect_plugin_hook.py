# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import sys
import logging
import functools

import ftrack_api
import ftrack_connect.application
from ftrack_perforce_location.scenario import (
    register as register_perforce,
    register_configuration as register_perforce_configuration
)

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)


logger = logging.getLogger('ftrack_perforce_location.connect_plugin_hook')


def modify_application_launch(event, session=None):
    '''Modify the application environment to include our location plugin.'''

    register_perforce_configuration(session)

    if 'options' not in event['data']:
        event['data']['options'] = {'env': {}}

    environment = event['data']['options']['env']

    ftrack_connect.application.appendPath(
        dependencies_directory,
        'PYTHONPATH',
        environment
    )

    logger.info(
        'Connect plugin modified launch hook to register location plugin.'
    )


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('Connect plugin discovered.')

    # Location will be available from within the dcc applications.
    api_object.event_hub.subscribe(
        'topic=ftrack.connect.application.launch',
        functools.partial(modify_application_launch, session=api_object)
    )

    # Location will be available from actions
    api_object.event_hub.subscribe(
        'topic=ftrack.action.launch',
        functools.partial(modify_application_launch, session=api_object)
    )
    register_perforce(api_object)


