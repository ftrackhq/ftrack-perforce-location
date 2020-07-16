# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import logging
import os
import pprint
import sys

import ftrack_api
import ftrack_connect.application

dependencies_directory = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'dependencies')
)
sys.path.append(dependencies_directory)

from ftrack_perforce_location.constants import ICON_URL
import ftrack_perforce_location

logger = logging.getLogger(
    'ftrack_perforce_location.configure_user_setting'
)


class LaunchApplicationAction(object):
    '''Discover and launch Qt app.'''
    description = 'Configure Perforce User Settings'
    identifier = 'ftrack-perforce-location-user-settings'

    def __init__(self, session, application_store, launcher):
        '''Initialise action with *applicationStore* and *launcher*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        '''
        super(LaunchApplicationAction, self).__init__()

        self.logger = logging.getLogger(
            'ftrack_perforce_location' + '.' + self.__class__.__name__
        )

        self.application_store = application_store
        self.launcher = launcher
        self._session = session

    @property
    def session(self):
        '''Return current session.'''
        return self._session

    def is_valid_selection(self, selection):
        '''Return True if the selection is valid (in this case, empty).'''

        return len(selection) == 0

    def register(self):
        '''Register discover actions on logged in user.'''
        self.session.event_hub.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                self.session.api_user),
            self.discover
        )

        self.session.event_hub.subscribe(
            'topic=ftrack.action.launch and source.user.username={0}'
            ' and data.actionIdentifier={1}'.format(
                self.session.api_user, self.identifier),
            self.launch
        )

        self.session.event_hub.subscribe(
            'topic=ftrack.connect.plugin.debug-information',
            self.get_version_information
        )

    def discover(self, event):
        '''Return discovered applications.'''
        if not self.is_valid_selection(
            event['data'].get('selection', [])
        ):
            return

        items = []
        applications = self.application_store.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            application_identifier = application['identifier']
            items.append({
                'actionIdentifier': self.identifier,
                'label': self.description,
                'icon': application.get('icon', 'default'),
                'variant': application.get('variant', None),
                'applicationIdentifier': application_identifier
            })

        return {
            'items': items
        }

    def launch(self, event):
        '''Handle *event*.

        event['data'] should contain:

            *applicationIdentifier* to identify which application to start.

        '''
        # Prevent further processing by other listeners.
        event.stop()

        if not self.is_valid_selection(
            event['data'].get('selection', [])
        ):
            return

        application_identifier = (
            event['data']['applicationIdentifier']
        )

        context = event['data'].copy()
        context['source'] = event['source']

        application_identifier = event['data']['applicationIdentifier']
        context = event['data'].copy()
        context['source'] = event['source']

        return self.launcher.launch(
            application_identifier, context
        )

    def get_version_information(self, event):
        '''Return version information.'''
        return dict(
            name=self.description,
            version=ftrack_perforce_location.__version__
        )


class ApplicationStore(ftrack_connect.application.ApplicationStore):

    def _discoverApplications(self):
        '''Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                'identifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'Version of the application',
                'icon': 'URL or name of predefined icon'
            )

        '''
        applications = []
        path_parts = []

        # build path
        if sys.platform != 'win32':
            path_parts.append(os.path.sep)
            path_parts.extend(dependencies_directory.split(os.path.sep)[1:])

        else:
            path_parts.extend(dependencies_directory.split(os.path.sep))

        path_parts.extend(
            [
                'ftrack_perforce_location',
                'user_settings.py$'
            ]
        )

        applications.extend(self._searchFilesystem(
            expression=path_parts,
            label='settings',  # Overridden later
            applicationIdentifier=(
                'com.ftrack.perforce.configure_user_settings'
            ),
            icon=ICON_URL,
        ))

        self.logger.debug(
            'Discovered applications:\n{0}'.format(
                pprint.pformat(applications)
            )
        )

        return applications


class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
    '''Custom launcher to modify environment before launch.'''

    def __init__(self, application_store):
        '''.'''
        super(ApplicationLauncher, self).__init__(application_store)
        self.logger.setLevel(logging.DEBUG)

    def _getApplicationLaunchCommand(self, application, context=None):

        command = [sys.executable, application['path']]

        # Add any extra launch arguments if specified.
        launchArguments = application.get('launchArguments')
        if launchArguments:
            command.extend(launchArguments)

        return command

    def _getApplicationEnvironment(
        self, application, context=None
    ):
        '''Return mapping of environment for *application* using *context*.

        *application* should be a mapping describing the application, as in the
        :class:`ApplicationStore`.

        *context* should provide additional information about how the
        application should be launched.

        '''
        environment = super(
            ApplicationLauncher, self
        )._getApplicationEnvironment(application, context)

        environment = ftrack_connect.application.prependPath(
            dependencies_directory,
            'PYTHONPATH',
            environment
        )

        return environment


def register(session):
    '''Register storage scenario.'''
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    logger.info('Discovering configure user settings')

    application_store = ApplicationStore()
    launcher = ApplicationLauncher(application_store)
    action = LaunchApplicationAction(session, application_store, launcher)
    action.register()
