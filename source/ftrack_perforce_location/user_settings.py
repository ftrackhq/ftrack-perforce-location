# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

from QtExt import QtCore, QtGui, QtWidgets
import ftrack_connect.ui.theme

from ftrack_action_handler.action import BaseAction
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler


class ConfigureUserSettingsWidget(QtWidgets.QDialog):

    def __init__(self, settings):
        super(ConfigureUserSettingsWidget, self).__init__()
        self.settings = settings
        self.ws_clients = []
        self.ws_roots = []
        self.setTheme()
        self.build()
        self.post_build()

    def build(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        settings_data = self.settings.read()
        user = settings_data['user']
        self.settings.p4.connect()
        available_worskpaces = self.settings.p4.run_workspaces('-u', user)
        self.ws_clients = [w['client'] for w in available_worskpaces]
        self.ws_roots = [w['Root'] for w in available_worskpaces]

        using_workspace = settings_data['using_workspace']
        workspace_root = settings_data['workspace_root']

        grid = QtWidgets.QGridLayout()
        self.layout().addLayout(grid)

        user_label = QtWidgets.QLabel('User')
        self.user_value = QtWidgets.QLineEdit(user)

        grid.addWidget(user_label, 0, 0)
        grid.addWidget(self.user_value, 0, 1)

        ws_label = QtWidgets.QLabel('Workspace')
        self.ws_value = QtWidgets.QComboBox()
        self.ws_value.addItems(self.ws_clients)

        if self.ws_clients and using_workspace:
            index = self.ws_value.findText(
                using_workspace, QtCore.Qt.MatchFixedString
            )
            self.ws_value.setCurrentIndex(index)

        grid.addWidget(ws_label, 1, 0)
        grid.addWidget(self.ws_value, 1, 1)

        root_label = QtWidgets.QLabel('Workspace Root')
        self.root_value = QtWidgets.QLineEdit(workspace_root)

        grid.addWidget(root_label, 2, 0)
        grid.addWidget(self.root_value, 2, 1)

        self.button = QtWidgets.QPushButton('Save Settings')
        self.layout().addWidget(self.button)

    def post_build(self):
        self.button.clicked.connect(self.on_save_settings)
        self.ws_value.currentIndexChanged.connect(self.on_workspace_change)

    def setTheme(self):
        '''Set *theme*.'''
        self.setWindowTitle('Perforce User Settings.')
        self.resize(600, 200)
        ftrack_connect.ui.theme.applyFont()
        ftrack_connect.ui.theme.applyTheme(self, 'light', 'cleanlooks')

    def on_workspace_change(self):
        ws_root = self.ws_roots[self.ws_value.currentIndex()]
        self.root_value.setText(ws_root)

    def on_save_settings(self):
        config_data = {}
        config_data['user'] = self.user_value.text()
        config_data['using_workspace'] = self.ws_value.itemData(self.ws_value.currentIndex())
        config_data['workspace_root'] = self.root_value.text()
        self.settings.write(config_data)


class ConfigureUserSettingsAction(BaseAction):
    label = 'Configure Perforce User Settings'
    identifier = 'com.ftrack.perforce.configure_user_settings'
    description = 'Configure Perforce User Settings'

    def __init__(self, *args, **kwargs):
        super(ConfigureUserSettingsAction, self).__init__(*args, **kwargs)
        perforce_settings = PerforceSettingsHandler()
        self.settings = ConfigureUserSettingsWidget(perforce_settings)

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
        self.settings.show()
        return True