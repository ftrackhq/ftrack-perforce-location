# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging

import ftrack_api.accessor.disk

from ftrack_perforce_location.perforce_handlers.file import seq_to_glob


class PerforceAccessor(ftrack_api.accessor.disk.DiskAccessor):
    ''''''
    def __init__(self, perforce_file_handler, **kw):
        self.perforce_file_handler = perforce_file_handler
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.prefix = perforce_file_handler.root

    def open(self, resource_identifier, mode='rb'):
        '''

        Return :class:`~ftrack_api.Data` for *resource_identifier*.

        ..note::

            We insert the file in the perforce depot.

        '''

        self.logger.debug('opening : {}'.format(resource_identifier))
        filesystem_path = self.get_filesystem_path(resource_identifier)
        filesystem_path = seq_to_glob(filesystem_path)
        self.perforce_file_handler.file_to_depot(filesystem_path)
        return super(PerforceAccessor, self).open(
            resource_identifier, mode=mode)

    def exists(self, resource_identifier):
        '''
        Return if *resource_identifier* is valid and exists in location.

        .. note::

               Always return False as we work on the same file.

        '''

        self.logger.debug('exists : {}'.format(resource_identifier))
        return False
