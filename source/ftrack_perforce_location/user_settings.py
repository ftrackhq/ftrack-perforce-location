# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import sys
from ftrack_action_handler.action import BaseAction
from QtExt import QtCore, QtGui, QtWidgets


class ConfigureUserSettingsWidget(QtWidgets.QtWidget):

    def __init__(self, parent=None):
        super(ConfigureUserSettingsWidget, self).__init__(parent=parent)

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)




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
        app = QtGui.QApplication(sys.argv)
        window = ConfigureUserSettingsWidget()
        window.show()
        sys.exit(app.exec_())
