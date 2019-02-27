# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

from QtExt import QtCore, QtGui, QtWidgets
import ftrack_connect.ui.theme

from ftrack_action_handler.action import BaseAction

from ftrack_perforce_location.perforce_handlers import errors
from ftrack_perforce_location.perforce_handlers.settings import PerforceSettingsHandler



class ConfigureUserSettingsWidget(QtWidgets.QDialog):

    def __init__(self, settings):
        super(ConfigureUserSettingsWidget, self).__init__()
        self.settings = settings
        self.setTheme()
        self.build()
        self.post_build()

    def build(self):
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        self.greetings = QtWidgets.QLabel(
            'Hi, looks like there are some settings missing!'
        )
        self.layout().addWidget(self.greetings)

        settings_data = self.settings.read() or self.settings._templated_default

        for item, value in settings_data.items():
            print item, value

        self.button = QtWidgets.QPushButton('Save Settings')
        self.layout().addWidget(self.button)

    def post_build(self):
        pass

    def setTheme(self):
        '''Set *theme*.'''
        self.setWindowTitle('Perforce User Settings.')
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        ftrack_connect.ui.theme.applyFont()
        ftrack_connect.ui.theme.applyTheme(self, 'light', 'cleanlooks')


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