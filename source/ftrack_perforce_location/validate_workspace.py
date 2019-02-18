import logging
import os
import re

import P4


class WorkspaceValidator(object):
    def __init__(self, p4=None, projects=None, settings=None):
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        if p4 is None:
            p4 = self.setup_perforce()
        self._p4 = p4
        if projects is None:
            projects = []
        self._projects = projects
        self._client_info = self._p4.run_client('-o')[0]
        self._prefix = self._client_info['Root']
        self._ws_map = self._get_ws_mapping()
        self._case_insensitive = (
            self._p4.run_info()[0]['clientCase'] == 'insensitive'
        )

    def setup_perforce(self):
        '''Returns a connected, logged in, P4 instance.'''
        p4 = P4.P4()

        p4.connect()
        p4.run_login()

        return p4

    def _get_ws_mapping(self):
        client_map = P4.Map(self._client_info['View'])
        root_map = P4.Map('//{0}/... {1}/...'.format(
            self._client_info['Client'], self._client_info['Root']))
        return P4.Map.join(client_map, root_map)

    def _positive_mappings(self, mapping=None):
        if mapping is None:
            mapping = self._ws_map
        return (line for
                line in mapping.as_array()
                if not line.startswith('-'))

    def _get_project_dir(self, project_name, prefix=None):
        if prefix is None:
            prefix = self._prefix
        return os.path.join(prefix, project_name, '...')

    def _mapped_depots(self, mapping=None):
        if mapping is None:
            mapping = self._ws_map
        depots = set(re.match(r'^//(.*)/.*\.\.\.', line).group(1)
                     for line in self._positive_mappings(mapping))
        return list(depots)

    def _proj_has_own_depot(self, project, mapping=None):
        if mapping is None:
            mapping = self._ws_map
        if not self._proj_in_mapping(project['name'], mapping):
            self.logger.warning('Project directory {0} not in mapping.'.format(
                self._prefix)
            )
            return False
        potential_depots = []
        for lhs, rhs in zip(mapping.lhs(), mapping.rhs()):
            if lhs.startswith('-'):
                continue
            proj_dir = os.path.join(
                os.path.dirname(self._get_project_dir(project['name'])), '')
            if self._case_insensitive:
                rhs = rhs.lower()
                proj_dir = proj_dir.lower()
            if rhs.startswith(proj_dir):
                potential_depots.append(lhs)
        if len(potential_depots) != 1:
            return False
        return True

    def _proj_in_mapping(self, project_name, mapping=None):
        if mapping is None:
            mapping = self._ws_map
        proj_dir_as_string = str(self._get_project_dir(project_name))
        return mapping.reverse().includes(proj_dir_as_string)

    def validate_one_depot_per_project(self, projects=None):
        if projects is None:
            projects = self._projects

        if not os.path.exists(self._prefix):
            self.logger.warning('Workspace root {0}, does not exist'.format(
                self._prefix))
            return False

        workspace_mappings = self._client_info.get('View')
        if not workspace_mappings:
            self.logger.warning(
                'Workspace {0} has no views configured.'.format(
                    self._client_info['Client']))
            return False

        if len(list(self._positive_mappings())) == 1:
            self.logger.warning(
                'Workspace only configured for a single depot.')
            if len(projects) > 1:
                return False

        for project in projects:
            if not self._proj_has_own_depot(project):
                self.logger.warning('Project {0} shares a depot.'.format(
                    project['name']))
                return False

        return True
