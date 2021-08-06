# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import ftrack_api
import logging
from Qt import QtWidgets, QtCore

import ftrack_connect.ui.application
import ftrack_connect.ui.widget.overlay
import ftrack_connect.ui.widget.actions
from ftrack_perforce_location import user_settings
from ftrack_perforce_location.perforce_handlers.settings import (
    PerforceSettingsHandler, P4Exception
)

logger = logging.getLogger('ftrack_perforce_location.connect-widget')


class PerforceUserSettings(ftrack_connect.ui.application.ConnectWidget):
    def __init__(self, session, parent=None):
        '''Instantiate the actions widget.'''
        super(PerforceUserSettings, self).__init__(session, parent=parent)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        perforce_settings = PerforceSettingsHandler(session)
        self.settings_widget = user_settings.ConfigureUserSettingsWidget(perforce_settings)
        layout.addWidget(self.settings_widget)


def register(session, **kw):
    '''Register plugin. Called when used as an plugin.'''
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an old or incompatible API and
    # return without doing anything.
    if not isinstance(session, ftrack_api.session.Session):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack_api.Session instance.'.format(session)
        )
        return

    plugin = ftrack_connect.ui.application.ConnectWidgetPlugin(PerforceUserSettings)
    plugin.register(session, priority=100)