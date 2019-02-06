# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import sys
import logging

import ftrack_api
import ftrack_connect.application

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)


logger = logging.getLogger('ftrack_perforce_location.connect_plugin_hook')


def modify_application_launch(event):
    '''Modify the application environment to include our location plugin.'''

    if 'options' not in event['data']:
        event['data']['options'] = {'env': {}}

    environment = event['data']['options']['env']

    ftrack_connect.application.appendPath(
        os.path.dirname(__file__),
        'FTRACK_EVENT_PLUGIN_PATH',
        environment

    )

    ftrack_connect.application.appendPath(
        dependencies_directory,
        'PYTHONPATH',
        environment
    )


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    # Location will be available from within the dcc applications.
    api_object.event_hub.subscribe(
        'topic=ftrack.connect.application.launch',
        modify_application_launch
    )

    # Location will be available from actions
    api_object.event_hub.subscribe(
        'topic=ftrack.action.launch',
        modify_application_launch
    )


