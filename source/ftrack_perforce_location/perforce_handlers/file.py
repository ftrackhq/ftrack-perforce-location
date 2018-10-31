# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import re
import logging

from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.errors import PerforceFileHandlerException


seq_match = re.compile('(%+\d+d)|(#+)|(%d)')


def seq_to_glob(filepath):
    found = seq_match.search(filepath)
    if found:
        match = found.group()
        filepath = filepath.replace(match, '*')

    return filepath


class PerforceFileHandler(object):

    @property
    def root(self):
        return self._change_handler._connection_handler._workspace_root

    @property
    def change(self):
        return self._change_handler

    @property
    def connection(self):
        return self._change_handler.connection

    def ensure_folder(self, folder):
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except IOError as error:
                raise PerforceFileHandlerException(error)

    def __init__(self, perforce_change_handler, root=None):
        if not perforce_change_handler.connection.connected():
            raise Exception('Not Connected')

        self._change_handler = perforce_change_handler

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.ensure_folder(self.root)

    def list(self):
        files_data = self.connection.run_files(
            '//{}/...'.format(
                self.connection.client
            )
        )
        return [data.get('depotFile') for data in files_data]

    def file_to_depot(self, filepath):
        self.logger.debug('moving file {} to depot'.format(filepath))
        if not filepath.startswith(self._root):
            raise IOError('File is not in {}'.format(self._root))
        stats = []

        try:
            stats = self.connection.run_fstat(filepath)
        except P4Exception as error:
            pass

        # no stats file has to be added to the depot
        if not stats:
            client = self.connection.fetch_client('-t', self.connection.client)
            client._root = self._root
            self.connection.save_client(client)
            self.connection.run_add(filepath)
        else:
            self.connection.run_edit(filepath)
