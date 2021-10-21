# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging

import ftrack_api.structure.standard
import ftrack_api.symbol


class PerforceStructure(ftrack_api.structure.standard.StandardStructure):
    '''This structure plugin generates a path based on the project hierarchy
    above a particular entity. It differs from the StandardStructure because
    it uses Perforce for versioning, rather than separate version folders.
    '''

    def __init__(self, perforce_file_handler):
        super(PerforceStructure, self).__init__(
            project_versions_prefix=None, illegal_character_substitute='_'
        )
        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

        self._perforce_file_handler = perforce_file_handler

    def _get_parts(self, entity):
        '''
        Return resource identifier parts from *entity*.

        .. note::

                Modified to remove version folder since files are versioned in
                place.

        '''

        # self.logger.debug('Get parts from entity : {}'.format(entity))

        session = entity.session

        version = entity['version']

        if version is ftrack_api.symbol.NOT_SET and entity['version_id']:
            version = session.get('AssetVersion', entity['version_id'])

        error_message = (
            'Component {0!r} must be attached to a committed '
            'version and a committed asset with a parent context.'.format(entity)
        )

        if version is ftrack_api.symbol.NOT_SET or version in session.created:
            raise ftrack_api.exception.StructureError(error_message)

        link = version['link']

        if not link:
            raise ftrack_api.exception.StructureError(error_message)

        structure_names = [item['name'] for item in link[1:-1]]

        project_id = link[0]['id']
        project = session.get('Project', project_id)
        asset = version['asset']

        parts = []
        parts.append(project['name'])

        if structure_names:
            parts.extend(structure_names)

        parts.append(asset['name'])

        # self.logger.debug('Get parts result : {}'.format(parts))

        return [self.sanitise_for_filesystem(part) for part in parts]
