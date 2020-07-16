# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os

import ftrack_api
import ftrack_connect.application


dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)

logger = logging.getLogger('ftrack_perforce_location.connect_plugin_hook')


def modify_application_launch(event):
    '''Modify the application environment to include our location plugin.'''

    print event

    try:
        environment = event['data']['options']['env']
    except KeyError:
        environment = {}

    location = os.path.join(os.path.dirname(__file__), '..', 'location')

    ftrack_connect.application.appendPath(
        location,
        'FTRACK_EVENT_PLUGIN_PATH',
        environment
    )

    ftrack_connect.application.appendPath(
        dependencies_directory,
        'PYTHONPATH',
        environment
    )

    logger.debug('Adding {} to app start environment. '.format(location))


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.debug('Discovering connect plugin hook')

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


