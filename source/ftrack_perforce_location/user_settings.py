# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os
import sys

from QtExt import QtCore, QtGui, QtWidgets
import ftrack_connect.ui.theme

logger = logging.getLogger(
    'ftrack_perforce_location.configure_user_setting'
)

# There is a chance this is being run as a script passed to Connect
# which, do to cx_freeze, does not ordinarily respect PYTHONPATH
extra_paths = os.environ.get('PYTHONPATH', '').split(os.pathsep)
for path in extra_paths:
    sys.path.append(path)

from ftrack_perforce_location.perforce_handlers.settings import (
    PerforceSettingsHandler
)


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
        '''Build interface layout and widgets.'''
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        settings_data = self.settings.read()
        # Update the Perforce server now that those settings are available.
        self.settings.update_port_from_scenario(settings_data)
        if self.settings.p4.port != settings_data['port']:
            if self.settings.p4.connected():
                self.settings.p4.disconnect()
            self.settings.p4.port = settings_data['port']
        self.settings.p4.connect()
        user = settings_data['user']
        available_worskpaces = self.settings.p4.run_workspaces('-u', user)
        self.ws_clients = [w['client'] for w in available_worskpaces]
        self.ws_roots = [w['Root'] for w in available_worskpaces]

        using_workspace = settings_data['using_workspace']
        workspace_root = settings_data['workspace_root']

        grid = QtWidgets.QGridLayout()
        self.layout().addLayout(grid)

        user_label = QtWidgets.QLabel('User')
        self.user_value = QtWidgets.QLineEdit(user)
        self.user_value.setReadOnly(True)

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
        self.root_value.setReadOnly(True)
        if not workspace_root:
            self.on_workspace_change()

        grid.addWidget(root_label, 2, 0)
        grid.addWidget(self.root_value, 2, 1)

        self.button = QtWidgets.QPushButton('Save Settings')
        self.layout().addWidget(self.button)

    def post_build(self):
        '''Connect events.'''
        self.button.clicked.connect(self.on_save_settings)
        self.ws_value.currentIndexChanged.connect(self.on_workspace_change)

    def setTheme(self):
        '''Set theme to match connect one.'''
        self.setWindowTitle('Perforce User Settings')
        self.resize(600, 200)
        ftrack_connect.ui.theme.applyFont()
        ftrack_connect.ui.theme.applyTheme(self, 'light', 'cleanlooks')

    def on_workspace_change(self):
        '''Qt slot for workspace combobox changes.'''
        ws_root = self.ws_roots[self.ws_value.currentIndex()]
        self.root_value.setText(ws_root)

    def on_save_settings(self):
        '''Qt slot for save button.'''
        config_data = {}
        config_data['user'] = self.user_value.text()
        config_data['using_workspace'] = self.ws_clients[
            self.ws_value.currentIndex()
        ]
        config_data['workspace_root'] = self.root_value.text()
        self.settings.write(config_data)
        self.close()


if __name__ == '__main__':
    perforce_settings = PerforceSettingsHandler()
    app = QtGui.QApplication(sys.argv)
    window = ConfigureUserSettingsWidget(perforce_settings)
    window.show()
    sys.exit(app.exec_())
