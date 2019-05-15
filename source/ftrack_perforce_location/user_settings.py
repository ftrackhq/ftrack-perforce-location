#! /usr/bin/env python
# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os
import sys

# from ftrack_connect.ui.widget.data_drop_zone.riffle import browser
from QtExt import QtCore, QtGui, QtWidgets
import ftrack_connect.ui.theme

logger = logging.getLogger(
    'ftrack_perforce_location.configure_user_setting'
)

# There is a chance this is being run as a script passed to Connect
# which, due to cx_freeze, does not ordinarily respect PYTHONPATH
extra_paths = os.environ.get('PYTHONPATH', '').split(os.pathsep)
for path in extra_paths:
    sys.path.append(path)

from ftrack_perforce_location.perforce_handlers.connection import (
    PerforceConnectionHandler
)
from ftrack_perforce_location.perforce_handlers import errors
from ftrack_perforce_location.perforce_handlers.settings import (
    PerforceSettingsHandler, P4Exception
)


class ConfigureUserSettingsWidget(QtWidgets.QDialog):
    def __init__(self, settings):
        super(ConfigureUserSettingsWidget, self).__init__()
        self.settings = settings
        self.ws_clients = []
        self.ws_roots = []
        self.setTheme()
        if not self.verify_scenario():
            self.reject()
            return
        self.build()
        self.post_build()

    def build(self):
        '''Build interface layout and widgets.'''
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.p4_handler = self.create_connection()
        settings_data = self.settings.read()
        user = settings_data['user']
        available_worskpaces = self.get_user_workspaces(user)
        self.ws_clients = [w['client'] for w in available_worskpaces]
        self.ws_roots = [w['Root'] for w in available_worskpaces]

        using_workspace = settings_data['using_workspace']
        if using_workspace not in self.ws_clients:
            using_workspace = self.ws_clients[0]
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

    def raise_warning_box(self, text):
        '''Display a warning dialog box with *text*.'''
        messageBox = QtWidgets.QMessageBox(parent=self)
        messageBox.setIcon(QtWidgets.QMessageBox.Warning)
        messageBox.setText(text)
        messageBox.exec_()

    def demand_input(self, label_text, mode=QtWidgets.QLineEdit.Normal):
        '''Ask the user for input via QInputDialog.'''
        title = 'Input required'
        result, ok = QtWidgets.QInputDialog.getText(self, title, label_text, mode)
        if ok:
            return result

    def create_connection(self, perforce_settings_data=None):
        perforce_settings_data = perforce_settings_data or self.settings.read()
        self.settings.update_port_from_scenario(perforce_settings_data)
        logger.debug('perforce_settings_data: {}'.format(perforce_settings_data))

        try:
            connection = PerforceConnectionHandler(**perforce_settings_data)
        except (errors.PerforceInvalidPasswordException,
                errors.PerforceSessionExpiredException) as e:
            logger.debug('exception: {}'.format(str(e)))
            perforce_error_message = e.args[0].errors[0]
            text = 'Please re-enter password for {0}\n\n{1}\n'.format(
                perforce_settings_data['user'], perforce_error_message
            )
            perforce_settings_data['password'] = self.demand_input(
                text,
                mode=QtWidgets.QLineEdit.Password
            )
            connection = self.create_connection(perforce_settings_data)
        except errors.PerforceWorkspaceException as e:
            logger.debug('exception: {}'.format(str(e)))
            root_dir = self.select_root_dir()
            perforce_settings_data['workspace_root'] = root_dir
            # There's likely a conflict with the selected workspace, so force
            # the creation of a new one.
            perforce_settings_data['using_workspace'] = None
            connection = self.create_connection(perforce_settings_data)

        self.settings.write(perforce_settings_data)
        return connection

    def get_user_workspaces(self, user, ensure=True):
        '''Return list of workspaces belonging to *user*.

        Since this is likely to be the first serious interaction with the
        Perforce server from this script, prompt the user for additional
        information as needed.
        '''
        unsuccessful = True
        while unsuccessful:
            try:
                user_worskpaces = (
                    self.p4_handler.connection.run_workspaces('-u', user)
                )
            except P4Exception as e:
                if (len(e.errors) == 1 and
                        e.errors[0] == errors.invalid_or_unset_password_message):
                    text = 'Logging in as {0}\n\n{1}'.format(
                        self.p4_handler.user, e.errors[0]
                    )
                    password = self.demand_input(
                        text,
                        mode=QtWidgets.QLineEdit.Password
                    )
                    if password:
                        self.p4_handler.connection.password = str(password)
                        self.p4_handler._login()
            else:
                unsuccessful = False
        if ensure and not user_worskpaces:
            root_dir = self.select_root_dir()
            self.p4_handler.create_workspace(root_dir)
            user_worskpaces = self.p4_handler.run_workspaces('-u', user)
        return user_worskpaces

    def select_root_dir(self):
        # dialog = browser.FilesystemBrowser(parent=self)
        warning_text = (
            'No workspaces found for user. Choose root directory to continue.'
        )
        self.raise_warning_box(warning_text)
        # Doesn't seem to show up under OSX
        caption = 'Choose workspace root directory'
        root_dir = QtGui.QFileDialog().getExistingDirectory(
            self, caption=caption, directory='~'
        )
        return root_dir

    def verify_scenario(self):
        '''Check whether required settings exist and suggest remediation.'''
        if self.settings.scenario_is_configured():
            return True
        warning_text = (
            'Please ensure that Perforce Storage Scenario is configured before'
            ' running this tool.\n\nWhile Connect is running, the scenario may'
            ' be configured by an admin logged into ftrack, under System'
            ' Settings > Media Management > Storage scenario.'
        )
        try:
            warning_text = '{0} Also accessible at:\n{1}{2}'.format(
                warning_text,
                os.environ['FTRACK_SERVER'],
                '/#view=configure_storage_scenario&itemId=newconfigure'
            )
        except Exception:
            pass
        self.raise_warning_box(warning_text)


if __name__ == '__main__':
    perforce_settings = PerforceSettingsHandler()
    app = QtGui.QApplication(sys.argv)
    window = ConfigureUserSettingsWidget(perforce_settings)
    window.exec_()
    # TODO exit after closing verification warning.
    sys.exit(app.exec_())
