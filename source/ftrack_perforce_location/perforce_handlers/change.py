# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging

from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import PerforceChangeHanderException
from ftrack_perforce_location.perforce_handlers.file import seq_to_glob


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
            raise PerforceChangeHanderException(error)

        self.logger.debug('created change : {}'.format(change))

        return change

    def add(self, change, filepath):
        '''Add **filepath** to *change*.'''

        self.logger.debug(
            'adding file {0} to change: {1}'.format(filepath, change)
        )

        try:
            self.connection.run_reopen('-c', str(change), filepath)
        except P4Exception as error:
            raise PerforceChangeHanderException(error)

    def submit(self, filepath, description):
        '''Submit **filepath** with **description** to server.'''

        filepath = seq_to_glob(filepath)
        change = self.create(description)
        self.logger.debug(
            'submitting change : {0} for path {1}'.format(change, filepath)
        )
        self.add(change, filepath)

        try:
            change_specs = self.connection.fetch_change('-o', str(change))
            self.connection.run_submit(change_specs)
        except P4Exception as error:
            raise PerforceChangeHanderException(error)

        # if is a depot file.... sync it
        if filepath.startswith('//depot'):
            self.logger.info(
                '{} is depot path, sync with version to fs'.format(filepath)
            )
            try:
                self.run_sync(filepath)
            except P4Exception as error:
                raise PerforceChangeHanderException(error)
