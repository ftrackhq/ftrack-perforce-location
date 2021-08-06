# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import os

import ftrack_api
# import ftrack_connect.application


dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)

logger = logging.getLogger('ftrack_perforce_location.connect_plugin_hook')


def modify_application_launch(event):
    '''Modify the application environment to include our location plugin.'''

    try:
        environment = event['data']['options']['env']
    except KeyError:
        environment = {}

    location = os.path.join(os.path.dirname(__file__), '..', 'location')

    environment['FTRACK_EVENT_PLUGIN_PATH'] = os.pathsep.join([environment.get('FTRACK_EVENT_PLUGIN_PATH', ''), location])
    environment['PYTHONPATH'] =  os.pathsep.join([environment.get('PYTHONPATH', ''), dependencies_directory])

    logger.debug('Updating environments.')


def register(api_object, **kw):
    '''Register plugin to api_object.'''

    # Validate that api_object is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(api_object, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.debug('Discovering connect plugin hook from {}'.format(__file__))

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


