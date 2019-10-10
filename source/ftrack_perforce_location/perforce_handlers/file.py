# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os
import re
import glob
import clique
from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import (
    PerforceFileHandlerException
)


seq_match = re.compile('(?<=\.)((%+\d+d)|(#+)|(%d)|(\d+))(?=\.)')


def to_file_list(filepath):
    '''
    Search for file sequence signatures in **filepath**
    and return a list of files.
    '''
    found = seq_match.search(filepath)
    if found:
        match = found.group()
        filepath = filepath.replace(match, '*')

    return filepath, glob.glob(filepath)


class PerforceFileHandler(object):
    '''Handle Perforce files.'''

    @property
    def root(self):
        '''Return the workspace root.'''
        return self._change_handler._connection_handler._workspace_root

    @property
    def change(self):
        '''Return Perforce change handler instance.'''
        return self._change_handler

    @property
    def connection(self):
        '''Return server connection.'''
        return self._change_handler.connection

    def _ensure_folder(self, folder):
        '''Create **folder** if does not exists.'''
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except IOError as error:
                raise PerforceFileHandlerException(error)

    def __init__(self, perforce_change_handler):
        '''
        Initialise Perforce file handler.

        ** perforce_change_handler ** should be an instance
        of PerforceChangeHandler.

        '''

        if not perforce_change_handler.connection.connected():
            raise Exception('Not Connected')

        self._change_handler = perforce_change_handler

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self._ensure_folder(self.root)

    def file_to_depot(self, filepaths, perforce_filemode='binary'):
        '''Publish **filepath** to server.'''

        self.logger.info('adding {} to depot'.format(filepaths))

        for filepath in filepaths:
            if not filepath.startswith(self.root):
                raise IOError('File is not in {}'.format(self.root))
        stats = []

        self.logger.debug('moving file {} to depot with mode {}'.format(filepaths, perforce_filemode))

        try:
            stats = self.connection.run_fstat(filepaths)
        except P4Exception as error:
            pass

        # no stats file has to be added to the depot
        if not stats:
            client = self.connection.fetch_client('-t', self.connection.client)
            # As of ftrack_api 1.7, filename must be a string
            client._root = str(self.root)
            try:
                self.connection.save_client(client)
                for filepath in filepaths:
                    self.connection.run_add('-t', perforce_filemode, filepath)
            except Exception as error:
                self.logger.exception(error)

        else:
            for filepath in filepaths:
                # 'p4 edit' requires that the file exists in the client
                if not os.path.exists(filepath):
                    basedir = os.path.dirname(filepath)
                    if not os.path.exists(basedir):
                        os.makedirs(basedir)
                    open(filepath, 'a').close()
                self.connection.run_edit(filepath)
