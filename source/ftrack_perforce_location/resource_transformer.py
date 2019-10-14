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
        self.logger.info('encoding: {}'.format(resource_identifier))
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
        decoded_path = None

        self.logger.info('decoding : {}'.format(resource_identifier))

        depot_pat, version = resource_identifier.split('#')
        depot_path_name = os.path.basename(depot_pat)

        # depot_pat , _ = to_file_list(depot_pat)
        self.logger.info('Sync {}'.format(resource_identifier))

        try:
            self.connection.run_sync(resource_identifier)
        except P4Exception as error:
            pass

        stats = self.connection.run_fstat(depot_pat)
        for stat in stats:
            self.logger.info('checking for {} in {}'.format(depot_path_name, stat['clientFile']))
            if depot_path_name in stat['clientFile']:
                decoded_path = stat['clientFile']
                self.logger.debug('decode {0} as {1}'.format(
                    resource_identifier, decoded_path)
                )
                break
        decoded_path = decoded_path or os.path.join(os.path.dirname(stats[0]['clientFile']), depot_path_name)
        self.logger.info('returing decoded path for {} as {}'.format(resource_identifier, decoded_path))
        return decoded_path
