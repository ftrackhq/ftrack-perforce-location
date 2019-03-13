# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import appdirs
import json
import logging
import os

from P4 import P4, P4Exception
import ftrack_api


class PerforceSettingsHandler(object):
    '''Handles Perforce connection settings.'''
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
        '''Return the current Perforce config file path.'''

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
            self.p4.connect()
            config['workspace_root'] = self.p4.run_info()[0]['clientRoot']
        except P4Exception as error:
            self.logger.debug('Error while querying client root: {0}'.format(
                error.message)
            )
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
                self._templated_default
            )
            self.write(updated_default_config)

        if os.path.isfile(config_file):
            self.logger.info(u'Reading config from {0}'.format(config_file))

            with open(config_file, 'r') as file:
                config = json.load(file)
            if any((key not in config) for key in self._templated_default):
                updated_default_config = self._update_config_from_perforce(
                    self._templated_default
                )
                updated_default_config.update(config)
                self.write(updated_default_config)
                config = updated_default_config

        return config

    def update_port_from_scenario(self, config, scenario_data=None):
        if scenario_data is None:
            scenario_data = self._get_scenario_settings()
        self._apply_scenario_settings(config, scenario_data)

    def _get_scenario_settings(self):
        with ftrack_api.Session(auto_connect_event_hub=False,
                                plugin_paths=list()) as session:
            setting = session.query(
                'select value from Setting where name is storage_scenario'
            ).one()
        location_data = json.loads(setting['value'])['data']
        return location_data

    def _apply_scenario_settings(self, config, location_data):
        try:
            if location_data['use_ssl']:
                protocol = 'ssl'
            else:
                protocol = 'tcp'
            p4_port = '{}:{}:{}'.format(
                protocol,
                location_data['server'],
                location_data['port_number']
            )
            config['port'] = p4_port
        except Exception as e:
            self.logger.warning('Could not read Perforce server settings from'
                                ' ftrack. Caught exception:\n{}'.format(e))
