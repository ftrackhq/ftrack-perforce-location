# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import logging
import os

import P4

from perforce_handlers.errors import PerforceValidationError


class WorkspaceValidator(object):
    '''Check a Perforce client workspace for various criteria.'''

    def __init__(self, p4, projects=None, sanitise=None):
        '''Initialize validator.

        *p4* should be a connected P4 instance.

        *projects* is an optional list of ftrack Projects, or similar
        dictionary-like objects. For convenience, this list can be overridden
        later.

        *sanitise* is an optional function to sanitise the project names'
        before writing them to the filesystem.
        '''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._p4 = p4
        if projects is None:
            projects = []
        self._projects = projects
        self._sanitise = sanitise

        self._client_info = self._p4.fetch_client()
        self._prefix = os.path.normpath(self._client_info['Root'])
        self._ws_map = self._get_ws_mapping()
        self._case_insensitive = (
            self._p4.run_info()[0]['clientCase'] == 'insensitive'
        )

    def validate_one_depot_per_project(self, projects=None):
        '''Tests the Perforce configuration for a list of projects.

        Returns True if all projects pass all tests, raises exception
        otherwise.

        *projects* is an optional list of Project or dictionary-like objects.
        By default, the list passed in to the constructor will be used.

        '''
        if projects is None:
            projects = self._projects

        if not os.path.exists(self._prefix):
            raise PerforceValidationError(
                'Workspace root, {0}, does not exist'.format(self._prefix)
            )

        workspace_mappings = self._client_info.get('View')
        if not workspace_mappings:
            raise PerforceValidationError(
                'Workspace {0} has no views configured.'.format(
                    self._client_info['Client'])
            )

        if len(list(self._positive_mappings())) == 1:
            self.logger.warning(
                'Workspace only configured for a single depot.'
            )
            if len(projects) > 1:
                raise PerforceValidationError(
                    'Multiple projects specified, but workspace mapping'
                    ' contains only one depot.'
                )

        for project in projects:
            if not self._proj_has_own_depot(project):
                raise PerforceValidationError(
                    'Project {0} shares a depot.'.format(project['name'])
                )

        return True

    def _get_filesystem_name(self, project):
        '''Return the filesystem folder name of a *project*.

        With a StandardStructure, the first part of a project's resource id
        will be the 'name' attribute. Each part is individually sanitised to
        ensure its characters are suitable for directory naming.

        *project* is an ftrack Project object or dictionary-like object.

        '''
        name = project['name']
        if self._case_insensitive:
            name = name.lower()
        if self._sanitise is not None:
            name = self._sanitise(name)
        return name

    def _get_ws_mapping(self):
        '''Returns a P4.Map which resolves depot paths to filesystem paths.'''
        self.logger.debug('Creating workspace map for {0}.'.format(
            self._p4.client)
        )
        client_map = P4.Map(self._client_info['View'])
        root_map = P4.Map('//{0}/... {1}/...'.format(
            self._client_info['Client'], self._prefix)
        )
        result = P4.Map.join(client_map, root_map)

        self.logger.debug('Client map:\n{0}'.format(client_map))
        self.logger.debug('Client root map:\n{0}'.format(root_map))
        self.logger.debug('Result:\n{0}'.format(result))

        #  Avoid the weird mix of (back)slashes on Windows.
        result = P4.Map([
            os.path.normpath(row)
            for row in result.as_array()
        ])

        self.logger.debug('Normalized Result:\n{0}'.format(result))

        return result

    def _positive_mappings(self, mapping=None):
        '''Return workspace mapping entries which do not start with a '-'.

        Perforce uses that syntax to indicate a path which is excluded from
        a particular depot. Sometimes these are created implicitly by P4.Map.

        *mapping* is an optional P4.Map. If none is provided, the mapping
        constructed during the constructor is used.
        '''
        if mapping is None:
            mapping = self._ws_map
        return (line for
                line in mapping.as_array()
                if not line.startswith('-'))

    def _get_project_dir(self, project, prefix=None):
        '''For a given *project_name* and optional *prefix*, return the right
        hand path in a resolved workspace mapping.
        '''
        if prefix is None:
            prefix = self._prefix
        proj_dir = os.path.join(prefix, self._get_filesystem_name(project), '...')
        return proj_dir

    def _proj_has_own_depot(self, project, mapping=None):
        '''Check that the given *project* will be written to a depot which no
        other project is configured to use.

        *mapping* is an optional P4.Map. If none is provided, the mapping
        constructed during the constructor is used.
        '''
        if mapping is None:
            mapping = self._ws_map
        if not self._proj_in_mapping(project, mapping):
            raise PerforceValidationError(
                'Failed to validate project: {0}\n'
                'Project directory {1} not in mapping.'.format(
                    project['name'], self._get_project_dir(project))
            )
        project_depots = []
        other_project_depots = []
        # So that it matches only the specific directory later, ensure it has
        # the correct trailing slash here
        proj_dir = os.path.join(
            os.path.dirname(self._get_project_dir(project)), ''
        )

        for lhs, rhs in zip(mapping.lhs(), mapping.rhs()):
            if lhs.startswith('-'):
                continue
            if self._case_insensitive:
                rhs = rhs.lower()
                proj_dir = proj_dir.lower()
            if rhs.startswith(proj_dir):
                project_depots.append(lhs.split(os.sep)[2])
            else:
                other_project_depots.append(lhs.split(os.sep)[2])
        for depot in project_depots:
            if depot in other_project_depots:
                return False
        return True

    def _proj_in_mapping(self, project, mapping=None):
        '''Return True if a *project* exists on the right hand side of a
        mapping.

        *mapping* is an optional P4.Map. If none is provided, the mapping
        constructed during the constructor is used.
        '''
        if mapping is None:
            mapping = self._ws_map
        proj_dir_as_string = str(self._get_project_dir(project))
        # Setting the second argument to False translates in the backwards
        # direction, converting filesystem paths to depot paths, if valid.
        included = mapping.translate(proj_dir_as_string, False) is not None
        return included
