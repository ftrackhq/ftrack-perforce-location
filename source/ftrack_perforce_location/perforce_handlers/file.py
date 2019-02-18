# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import re
import logging

from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import PerforceFileHandlerException
from ftrack_perforce_location.validate_workspace import WorkspaceValidator


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
    '''Handle perforce files.'''

    @property
    def root(self):
        '''Return the workspace root.'''
        return self._change_handler._connection_handler._workspace_root

    @property
    def change(self):
        '''Return perforce change handler instance.'''
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

    def __init__(self, perforce_change_handler, one_depot_per_project=False):
        '''
        Initialise perforce file handler.

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
        self._one_depot_per_project = one_depot_per_project

    def file_to_depot(self, filepath, project_name=None):
        '''Publish **filepath** to server.'''
        if project_name is not None and self._one_depot_per_project:
            if not self.project_has_own_depot(project_name):
                error_message = ('Not checking in {}.'
                                 ' Project {} requires its own depot.'.format(
                                     filepath,
                                     project_name
                                 ))
                raise Exception(error_message)
        self.logger.debug('moving file {} to depot'.format(filepath))
        if not filepath.startswith(self.root):
            raise IOError('File is not in {}'.format(self.root))
        stats = []

        try:
            stats = self.connection.run_fstat(filepath)
        except P4Exception as error:
            pass

        # no stats file has to be added to the depot
        if not stats:
            client = self.connection.fetch_client('-t', self.connection.client)
            # As of ftrack_api 1.7, filename must be a string
            client._root = str(self.root)
            self.connection.save_client(client)
            self.connection.run_add(filepath)
        else:
            # 'p4 edit' requires that the file exists in the client
            if not os.path.exists(filepath):
                basedir = os.path.dirname(filepath)
                if not os.path.exists(basedir):
                    os.makedirs(basedir)
                open(filepath, 'a').close()
            self.connection.run_edit(filepath)

    def project_has_own_depot(self, project_name):
        project_list = [{'name': project_name}]
        validator = WorkspaceValidator(self.connection, project_list)

        return validator.validate_one_depot_per_project()
