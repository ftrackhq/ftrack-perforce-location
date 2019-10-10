# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import os

import clique

from P4 import P4Exception
import ftrack_api.resource_identifier_transformer.base as base_transformer

from ftrack_perforce_location.perforce_handlers.file import to_file_list


class PerforceResourceIdentifierTransformer(
        base_transformer.ResourceIdentifierTransformer):
    def __init__(self, session, perforce_file_handler):
        super(PerforceResourceIdentifierTransformer, self).__init__(session)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._perforce_file_handler = perforce_file_handler

    @property
    def connection(self):
        '''Return connection to Perforce server.'''
        return self._perforce_file_handler.connection

    def encode(self, resource_identifier, context=None):
        '''
        Return encoded *resource_identifier* for storing centrally.

        .. note::

            This transforms /file/path to //depot/file/path#version

        '''

        root = self._perforce_file_handler.root
        fullpath = os.path.join(root, resource_identifier)
        mangled_path, files = to_file_list(fullpath)
        stats = self.connection.run_fstat(mangled_path)

        if '%d' in resource_identifier:
            resource_identifier = resource_identifier.replace('%d', '*')

        # # format result path as: //depot/,,,,#<revision>
        encoded_path = '//{0}#{1}'.format(
            resource_identifier,
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

            This transforms //depot/file/path#version to /file/path

        '''
        depot_pat, version = resource_identifier.split('#')
        mangled_path, files = to_file_list(depot_pat)

        decoded_path = None

        for file in files:
            try:
                self.logger.info('Sync {}'.format(file))
                self.connection.run_sync(file)
            except P4Exception as error:
                self.logger.debug(error)
                pass

        stats = self.connection.run_fstat(mangled_path)
        for stat in stats:
            if os.path.basename(depot_pat) in stat['clientFile']:
                decoded_path= stat['clientFile']
                self.logger.debug('decode {0} as {1}'.format(
                    resource_identifier, decoded_path)
                )
                break

        return decoded_path
