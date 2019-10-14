# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os
from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import (
    PerforceChangeHanderException
)
from ftrack_perforce_location.perforce_handlers.file import to_file_list


class PerforceChangeHandler(object):
    '''Handles commit changes.'''

    def __init__(self, connection_handler):
        self._connection_handler = connection_handler

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    @property
    def connection(self):
        '''Return current connection to the server.'''
        return self._connection_handler.connection

    def create(self, description):
        '''Create a new change with the given **description**.'''
        change = None
        try:
            change_spec = self.connection.fetch_change()
            change_spec._description = str(description)
            change_spec._files = []
            saved_change = self.connection.save_change(change_spec)
            if saved_change:
                self.logger.debug('saved_change {}'.format(saved_change))
                try:
                    new_change_id = int(saved_change[0].split()[1])
                    change = str(new_change_id)
                except P4Exception as error:
                    raise PerforceChangeHanderException(error)

        except P4Exception as error:
            self.logger.exception('error on save changes')
            raise PerforceChangeHanderException(error)

        self.logger.debug('created change : {}'.format(change))

        return change

    def add(self, change, filepaths):
        '''Add **filepath** to *change*.'''

        try:
            for filepath in filepaths:
                file_exists = os.path.exists(filepath)

                self.logger.debug(
                    'adding file {0} to change: {1}, file exists: {2}'.format(filepath, change, file_exists)
                )
                self.connection.run_reopen('-c', str(change), filepath)
        except P4Exception as error:
            self.logger.exception('error on reopen')
            raise PerforceChangeHanderException(error)

    def submit(self, filepath, description, change=None):
        '''Submit **filepath** with **description** to server.'''

        mangled_path, files = to_file_list(filepath)
        change = change or self.create(description)
        self.logger.debug(
            'submitting change : {0} for path {1}'.format(change, filepath)
        )
        self.add(change, files)

        try:
            change_specs = self.connection.fetch_change('-o', str(change))
            self.connection.run_submit(change_specs)
        except P4Exception as error:
            self.logger.exception('error on fetch changes')

            raise PerforceChangeHanderException(error)

        return change
