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

    def __init__(self, session):
        super(PerforceSettingsHandler, self).__init__()
        self._session = session
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    @property
    def session(self):
        return self._session

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

    @staticmethod
    def _sanitize_username(name, illegal_character_substitute='_'):
        '''Convert a *name* to a valid Perforce username.

        We split username at the first @ sign, if present, then replace
        every other prohibited character sequence ('...', '*', '%%',
        and '#') with '_' or *illegal_character_substitute* if given.

        Note that many of these characters are a bad idea in an ftrack
        username anyway.
        '''
        name = name.split('@')[0]
        for illegal_sequence in ('...', '*', '%%', '#'):
            name = name.replace(illegal_sequence, illegal_character_substitute)
        if name.isdigit():
            name = '{}_'.format(name)
        return str(name)

    def _update_config_from_perforce(self, config):
        '''Return a copy of *config* with values pulled from Perforce.

        *config* is a dictionary used to initialize a
        PerforceConnectionHandler.
        '''
        config = dict(config)
        p4 = P4()
        config['user'] = self._sanitize_username(self.session.api_user)
        config['using_workspace'] = p4.client
        p4.port = config['port']
        try:
            p4.connect()
            if p4.port.startswith('ssl'):
                p4.run_trust('-y')
                config['workspace_root'] = p4.fetch_client(p4.client)['Root']
                if config['workspace_root'] == 'None':
                    config['workspace_root'] = None
        except P4Exception as error:
            self.logger.debug('Error while querying client root: {0}'.format(
                error.message)
            )

        self.logger.debug('updated config from perforce with: {}'.format(config))

        return config

    def write(self, config):
        '''Write **config** data to file.'''

        self.logger.debug('saving settings:{}'.format(config))

        config_file = self._get_config_path()
        # Create folder if it does not exist.
        folder = os.path.dirname(config_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        with open(config_file, 'w') as file:
            json.dump(config, file)

    def read(self):
        '''Read config data from file, returns a dictioary.'''

        config_file = self._get_config_path()
        config = None

        if not os.path.exists(config_file):
            self.logger.debug('Creating default config settings in :{}'.format(config_file))

            new_config = self._templated_default
            self.update_port_from_scenario(new_config)
            new_config = self._update_config_from_perforce(new_config)
            self.write(new_config)

        if os.path.isfile(config_file):
            self.logger.info(u'Reading config from {0}'.format(config_file))

            with open(config_file, 'r') as file:
                config = json.load(file)
            if any((key not in config) for key in self._templated_default):
                new_config = self._templated_default
                new_config = self._update_config_from_perforce(
                    new_config
                )
                new_config.update(config)
                self.write(new_config)
                config = new_config

        config = self.update_port_from_scenario(config)
        self.logger.info('Returning config data :{}'.format(config))
        return config

    def update_port_from_scenario(self, config, scenario_data=None):
        '''Update the port setting of *config*.

        *config* is a dictionary used to initialize a
        PerforceConnectionHandler.

        *scenario_data* is a dictionary of user settings stored on the ftrack
        server by the Perforce storage scenario. If not passed, it will be
        read from the server.
        '''
        scenario_data = scenario_data or self._get_scenario_settings()

        self.logger.info('Updating port from scenario: {}'.format(scenario_data))
        self._apply_scenario_settings(config, scenario_data)

        try:
            config['port']
        except KeyError:
            self.logger.warning(
                'Cannot update p4.port.'
                ' Is the storage scenario configured correctly?')
            return

        return config

    def _get_scenario_settings(self):
        '''Returns the settings stored by the Perforce storage scenario.

        Spins up a short-lived ftrack_api.Session to query the ftrack server
        for settings.
        '''
        with ftrack_api.Session(auto_connect_event_hub=False,
                                plugin_paths=list()) as session:
            setting = session.query(
                'select value from Setting where name is storage_scenario'
            ).one()
        location_data = json.loads(setting['value'])['data']
        self.logger.debug('scenario data :{}'.format(location_data))
        return location_data

    def scenario_is_configured(self):
        '''Validate that the storage scenario data has all expected keys.'''
        data = self._get_scenario_settings()
        existing_keys = set(data.keys())
        required_keys = set(
            ('server', 'port_number', 'use_ssl', 'one_depot_per_project')
        )
        missing_keys = required_keys.difference(existing_keys)

        if not missing_keys:
            return True

        self.logger.warning('Missing keys in server settings:\n{0}'.format(
            ', '.join(missing_keys)))
        return False

    def _apply_scenario_settings(self, config, location_data):
        '''Sets Perforce server address, or "port", in the *config* dictionary.

        *config* is a dictionary used to initialize a
        PerforceConnectionHandler.

        *location_data* is a dictionary of user settings stored on the ftrack
        server by the Perforce storage scenario.
        '''
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
