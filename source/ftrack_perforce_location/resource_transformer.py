# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import os
import re

import ftrack_api.resource_identifier_transformer.base as base_transformer

from P4 import P4Exception
from ftrack_perforce_location.perforce_handlers.file import seq_to_glob
from pathlib import Path


class PerforceResourceIdentifierTransformer(
    base_transformer.ResourceIdentifierTransformer
):
    def __init__(self, session, perforce_file_handler):
        super(PerforceResourceIdentifierTransformer, self).__init__(session)

        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

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
        mangled_path = seq_to_glob(fullpath)
        
        stats = self.connection.run_fstat(str(Path(mangled_path)))
        rx = re.compile('%+\d+d|%d')
        found = rx.search(resource_identifier)
        original_resource = resource_identifier

        if found:
            replace = found.group()
            resource_identifier = resource_identifier.replace(replace, '*')

        # format result path as: //depot/,,,,#<revision>
        encoded_path = '//{0}#{1}'.format(
            resource_identifier, int(stats[0].get('headRev', 0)) + 1
        )

        # Don't return the depot encoded path if the file isn't in the depot
        # P4 doesn't handle that very well, fstat shouldn't fail if the file isn't in the depot
        returned_path = encoded_path
        try:
            self.connection.run_fstat(returned_path)
        except P4Exception:
            returned_path = original_resource

        self.logger.debug('Encode {0} as {1}'.format(original_resource, encoded_path))
        return returned_path

    def decode(self, resource_identifier, context=None):
        '''
        Return decoded *resource_identifier* for storing centrally.

        .. note::

            This transforms //depot/file/path#version to /file/path

        '''
        decoded_path = ''
        decoded_sequence_path = ''

        if '#' in resource_identifier:
            depot_path, version = resource_identifier.split('#')
            depot_path_name = os.path.basename(depot_path)

            try:
                self.logger.debug('Sync {0}'.format(resource_identifier))
                self.connection.run_sync(resource_identifier)
            except P4Exception:
                pass

            stats = None
            try:
                stats = self.connection.run_fstat(depot_path)
            except:
                pass

            if '*' not in depot_path_name:
                if stats:
                    for stat in stats:
                        self.logger.debug(
                            'Checking for {0} in {1}'.format(
                                depot_path_name, stat['clientFile']
                            )
                        )
                        if depot_path_name in stat['clientFile']:
                            decoded_path = stat['clientFile']
                            self.logger.debug(
                                'Decode {0} as {1}'.format(resource_identifier, decoded_path)
                            )
                            break

                    decoded_sequence_path = os.path.join(
                        os.path.dirname(stats[0]['clientFile']), depot_path_name
                    )
            decoded_path = decoded_path or decoded_sequence_path
            if '*' in decoded_path:
                decoded_path = decoded_path.replace('*', '%d')

            self.logger.debug(
                'Returning decoded path for {0} as {1}'.format(
                    resource_identifier, decoded_path
                )
            )

            return Path(decoded_path)
        else:
            # assume file isn't in depot because resource_identifier is a local path
            return Path(resource_identifier)
