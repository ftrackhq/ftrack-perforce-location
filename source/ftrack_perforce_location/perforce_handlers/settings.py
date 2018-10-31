# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import json
import appdirs
import logging

from ftrack_perforce_location.perforce_handlers.errors import PerforceSettingsHandlerException


class PerforceSettingsHandler(object):

    def __init__(self):
        super(PerforceSettingsHandler, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    @property
    def templated_default(self):
        return dict(
            server=None,
            port = None,
            user = None,
            password = None,
            using_workspace = None,
            workspace_root= None
        )

    def get_config_path(self):
        config_file_path = os.path.join(
            appdirs.user_data_dir(
                'ftrack-connect', 'ftrack'
            ),
            'perforce_config.json'
        )

        return config_file_path

    def write(self, config):
        config_file = self.get_config_path()
        # Create folder if it does not exist.
        folder = os.path.dirname(config_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        with open(config_file, 'w') as file:
            json.dump(config, file)

    def read(self):
        config_file = self.get_config_path()
        config = None

        if not os.path.exists(config_file):
            self.logger.debug('Creating default config settings')
            self.write(self.templated_default)

        if os.path.isfile(config_file):
            self.logger.info(u'Reading config from {0}'.format(config_file))

            with open(config_file, 'r') as file:
                try:
                    config = json.load(file)
                except Exception:
                    raise PerforceSettingsHandlerException(
                        u'Exception reading json config in {0}.'.format(
                            config_file
                        )
                    )

        # if settings exists but is not filled up...
        if not all(config.values()):
            raise PerforceSettingsHandlerException(
                'Please configure : {}'.format(
                    self.get_config_path()
            ))

        return config

