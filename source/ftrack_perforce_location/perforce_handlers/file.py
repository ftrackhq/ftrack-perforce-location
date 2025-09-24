# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import os
import re
import contextlib

import P4
from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import (
    PerforceFileHandlerException,
)


seq_match = re.compile('(%+\d+d)|(#+)|(%d)')


def seq_to_glob(filepath):
    '''
    Search for file sequence signatures in **filepath**
    and replace it with wildcard *.
    '''
    found = seq_match.search(filepath)
    if found:
        match = found.group()
        filepath = filepath.replace(match, '*')

    return filepath


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

    def update_workspace_map(self, project_name):
        workspace = self.connection.fetch_client('-o')
        new_mapping = '//depot/{1}... "//{0}/{1}..."'.format(workspace['Client'], project_name)
        self.logger.debug('Updating workspace map with : {}'.format(new_mapping))

        mappings = P4.Map(workspace['View']).as_array()
        if new_mapping in mappings:
            self.logger.info(
                'Depot already in client view. Not adding: {0}'.format(new_mapping)
            )
            return

        mappings.append(new_mapping)
        workspace['View'] = mappings
        self.connection.save_client(workspace)

    def __init__(self, perforce_change_handler):
        '''
        Initialise Perforce file handler.

        ** perforce_change_handler ** should be an instance
        of PerforceChangeHandler.

        '''

        if not perforce_change_handler.connection.connected():
            raise Exception('Not Connected')

        self._change_handler = perforce_change_handler

        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        self.logger.info(f'Using client: {self.connection.client}')
        self._ensure_folder(self.root)

    def is_file_in_depot(self, filepath):

        stats = []

        with contextlib.suppress(P4Exception):

            stats = self.connection.run_fstat(str(filepath))
            self.logger.debug(f'file is in depot  : {stats}')

        return True if stats else False


    def delete(self, filepath):
        self.connection.run_delete(filepath)

    def file_to_depot(self, filepath, perforce_filemode='binary'):
        '''Publish **filepath** to server.'''

        if self.root not in filepath:            
            msg = f'File {filepath} is not in {self.root}'
            self.logger.error(msg)
            raise IOError(msg)

        self.logger.info(
            'Moving file {} to depot with mode {}'.format(filepath, perforce_filemode)
        )
        
        is_in_depot = self.is_file_in_depot(str(filepath))

        # no stats file has to be added to the depot
        if not is_in_depot:
            client = self.connection.fetch_client('-t', self.connection.client)
            self.logger.info(f'saving client {client} with root {self.root} ')
            # As of ftrack_api 1.7, filename must be a string
            client._root = str(self.root)
            try:
                self.connection.save_client(client)
                self.connection.run_add('-t', perforce_filemode, str(filepath))
            except Exception as error:
                self.logger.exception(error)

        else:
            # 'p4 edit' requires that the file exists in the client
            if not os.path.exists(filepath):
                basedir = os.path.dirname(str(filepath))
                if not os.path.exists(str(basedir)):
                    os.makedirs(str(basedir))
                open(str(filepath), 'a').close()
            self.connection.run_edit(str(filepath))
