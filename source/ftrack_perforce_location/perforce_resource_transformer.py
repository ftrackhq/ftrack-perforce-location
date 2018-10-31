# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import logging

import ftrack_api.resource_identifier_transformer.base as base_transformer

from P4 import P4Exception

from ftrack_perforce_location.perforce_handlers.file import seq_to_glob


class PerforceResourceIdentifierTransformer(base_transformer.ResourceIdentifierTransformer):
    def __init__(self, session, perforce_file_handler):
        super(PerforceResourceIdentifierTransformer, self).__init__(session)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._perforce_file_handler = perforce_file_handler

    @property
    def connection(self):
        '''Return connection to perforce server.'''
        return self._perforce_file_handler.connection

    def encode(self, resource_identifier, context=None):
        '''
        Return encoded *resource_identifier* for storing centrally.

        .. note::

            We transform here from /file/path to //depot/file/path#version

        '''

        root =  self._perforce_file_handler.root
        fullpath = os.path.join(root, resource_identifier)
        fullpath = seq_to_glob(fullpath)
        stats = self.connection.run_fstat(fullpath)
        # format result path as: //depot/,,,,#<revision>
        encoded_path = '{0}#{1}'.format(
            stats[0].get('depotFile'),
            int(stats[0].get('headRev', 0)) + 1
        )
        self.logger.debug('encode {0} as {1}'.format(
            resource_identifier, encoded_path)
        )
        return encoded_path

    def decode(self, resource_identifier, context=None):
        '''
        Return decoded *resource_identifier* for storing centrally.

        .. note::

            We transform here from //depot/file/path#version to /file/path

        '''
        depot_pat, version = resource_identifier.split('#')
        depot_pat = seq_to_glob(depot_pat)

        self.logger.info('Sync {}'.format(resource_identifier))

        try:
            self.connection.run_sync(resource_identifier)
        except P4Exception as error:
            self.logger.debug(error)
            pass

        stats = self.connection.run_fstat(depot_pat)
        decoded_path = stats[0].get('clientFile')
        self.logger.debug('decode {0} as {1}'.format(
            resource_identifier, decoded_path)

        )
        return decoded_path
