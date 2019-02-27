# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import json
import appdirs
import logging

from P4 import P4, P4Exception

from ftrack_perforce_location.perforce_handlers.errors import PerforceSettingsHandlerException


class PerforceSettingsHandler(object):
    '''Handles perforce connection settings.'''
    def __init__(self):
        super(PerforceSettingsHandler, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.p4 = P4()

    @property
    def _templated_default(self):
        '''Return a default, empty config to be setup.'''

        return dict(
            user=None,
            using_workspace=None,
            workspace_root=None
        )

    def _get_config_path(self):
        '''Return the current perforce config file path.'''

        config_file_path = os.path.join(
            appdirs.user_data_dir(
                'ftrack-connect', 'ftrack'
            ),
            'perforce_config.json'
        )

        return config_file_path

    def _update_config_from_perforce(self, config):
        config = dict(config)
        config['user'] = self.p4.user
        config['using_workspace'] = self.p4.client
        try:
            p4.connect()
            config['workspace_root'] = self.p4.run_info()[0]['clientRoot']
        except P4Exception as error:
            self.logger.debug('Error while querying client root: {0}'.format(
                error.message))
        return config

    def write(self, config):
        '''Write **config** data to file.'''

        config_file = self._get_config_path()
        # Create folder if it does not exist.
        folder = os.path.dirname(config_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        with open(config_file, 'w') as file:
            json.dump(config, file)

    def read(self):
        '''Read config data to file.'''

        config_file = self._get_config_path()
        config = None

        if not os.path.exists(config_file):
            self.logger.debug('Creating default config settings')
            updated_default_config = self._update_config_from_perforce(
                self._templated_default)
            self.write(updated_default_config)

        if os.path.isfile(config_file):
            self.logger.info(u'Reading config from {0}'.format(config_file))

            with open(config_file, 'r') as file:
                config = json.load(file)

        return config
