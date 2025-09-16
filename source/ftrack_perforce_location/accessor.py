# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import os
import logging

import ftrack_api.accessor.disk
from ftrack_api.exception import AccessorError


class PerforceAccessorError(AccessorError):
    
    default_message="Could not determine access path for resource_identifier {resource_identifier} outside of configured prefix: {prefix}."

    
    def __init__(self, resource_identifier, prefix, **kw):
        kw.setdefault("details", {}).update(
            dict(resource_identifier=resource_identifier, prefix=prefix)
        )
        super(PerforceAccessorError, self).__init__(**kw)
        


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
        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)
        self.logger.debug(f'Initializing prefix accessor with : {perforce_file_handler.root}')
        self.prefix = perforce_file_handler.root

    def open(self, resource_identifier, mode='rb'):
        '''
        Return :class:`~ftrack_api.Data` for *resource_identifier*.

        ..note::

            This will add, create, edit, and fetch the file as needed.
        '''
        self.logger.debug(f'Opening {resource_identifier} in Binary mode.')
        
        _, ext = os.path.splitext(resource_identifier)
        perforce_filemode = self._typemap.get(
            ext.lower(), 'binary'
        )  # If is unknown let's piggy back on binary format.

        project = resource_identifier.split('/')[0]
        self.perforce_file_handler.update_workspace_map(project)
        filesystem_path = self.get_filesystem_path(resource_identifier)
        self.logger.info(f'Retrieving {filesystem_path}.')

        self.perforce_file_handler.file_to_depot(filesystem_path, perforce_filemode)
        return super(PerforceAccessor, self).open(resource_identifier, mode=mode)

    def exists(self, resource_identifier):
        '''
        Return if *resource_identifier* is valid and exists in location.

        .. note::

               Always return False since Perforce versions in place, so it is
               required to overwrite the file.
        '''

        return False

    def get_filesystem_path(self, resource_identifier):
        """Return filesystem path for *resource_identifier*.

        For example::

            >>> accessor = DiskAccessor('my.location', '/mountpoint')
            >>> print accessor.get_filesystem_path('test.txt')
            /mountpoint/test.txt
            >>> print accessor.get_filesystem_path('/mountpoint/test.txt')
            /mountpoint/test.txt

        Raise :exc:`ftrack_api.exception.AccessorFilesystemPathError` if filesystem
        path could not be determined from *resource_identifier*.

        """
        filesystem_path = resource_identifier
        if filesystem_path:
            filesystem_path = os.path.normpath(filesystem_path)

        if self.prefix:
            if not os.path.isabs(filesystem_path):
                filesystem_path = os.path.normpath(
                    os.path.join(self.prefix, filesystem_path)
                )

            if not filesystem_path.startswith(self.prefix):
                raise PerforceAccessorError(
                    prefix=self.prefix,
                    resource_identifier=filesystem_path
                )

        return filesystem_path