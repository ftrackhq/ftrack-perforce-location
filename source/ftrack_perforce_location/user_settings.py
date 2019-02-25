# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import sys
from ftrack_action_handler.action import BaseAction
from QtExt import QtCore, QtGui, QtWidgets
import ftrack_connect


class ConfigureUserSettingsWidget(ftrack_connect.ui.application.ApplicationPlugin):

    def __init__(self,  *args, **kwargs):
        super(ConfigureUserSettingsWidget, self).__init__( *args, **kwargs)
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

    def getName(self):
        '''Return name of widget.'''
        return 'Perforce Settings'


def register_plugin(connect):
        '''Register publish plugin to ftrack connect.'''
        config = ConfigureUserSettingsWidget()
        connect.addPlugin(config)


class ConfigureUserSettingsAction(BaseAction):
    label = 'Configure Perforce User Settings'
    identifier = 'com.ftrack.perforce.configure_user_settings'
    description = 'Configure Perforce User Settings'

    def validate_selection(self, entities):
        '''Return True if the selection is valid.

        Utility method to check *entities* validity.

        '''
        if not entities: # show only if nothing is selected.
            return True

        return False

    def discover(self, session, entities, event):
        '''Return True if the action can be discovered.

        Check if the current selection can discover this action.

        '''
        return self.validate_selection(entities)

    def launch(self, session, entities, event):
        application_instance = QtGui.QApplication.instance()
        widgets = application_instance.topLevelWidgets()
        connect = None
        for widget in widgets:
            if widget.objectName() == 'ftrack-connect-window':
                connect = widget
                break

        register_plugin(connect)
        return True