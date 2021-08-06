# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import os
import logging

import ftrack_api.accessor.disk


class PerforceAccessor(ftrack_api.accessor.disk.DiskAccessor):
    '''Extends the DiskAccessor to ensure target file is writable and/or the
    correct version.
    '''

    def __init__(self, perforce_file_handler, typemap, **kw):
        '''Store root directory and file handling help.

        *perforce_file_handler*. is an instance of
        ftrack_perforce_location.perforce_handlers.file.PerforceFileHandler.
        '''
        self._typemap = typemap
        self.perforce_file_handler = perforce_file_handler
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.prefix = perforce_file_handler.root

    def open(self, resource_identifier, mode='rb'):
        '''
        Return :class:`~ftrack_api.Data` for *resource_identifier*.

        ..note::

            This will add, create, edit, and fetch the file as needed.
        '''

        _, ext = os.path.splitext(resource_identifier)
        perforce_filemode = self._typemap.get(ext.lower(), 'binary')  # If is unknown let's piggy back on binary format.
        filesystem_path = self.get_filesystem_path(resource_identifier)
        self.perforce_file_handler.file_to_depot(filesystem_path, perforce_filemode)
        return super(PerforceAccessor, self).open(
            resource_identifier, mode=mode)

    def exists(self, resource_identifier):
        '''
        Return if *resource_identifier* is valid and exists in location.

        .. note::

               Always return False since Perforce versions in place, so it is
               required to overwrite the file.
        '''

        # self.logger.debug('exists : {}'.format(resource_identifier))
        return False
