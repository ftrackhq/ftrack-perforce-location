# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import logging
import json
from ftrack_action_handler.action import AdvancedBaseAction
from ftrack_api.structure.standard import StandardStructure

import P4
from P4 import P4Exception


from ftrack_perforce_location.constants import SCENARIO_ID, ICON_URL
from ftrack_perforce_location.perforce_handlers import connection
from ftrack_perforce_location.perforce_handlers import settings


class PerforceAttributeAction(AdvancedBaseAction):
    label = 'Configure Project Perforce'
    identifier = 'com.ftrack.ftrack_perforce_location.perforce_attribute'
    description = 'Configure various Perforce options for the current project'
    
    run_as_user = True
    limit_to_user = True

    def __init__(self, session):
        super(PerforceAttributeAction, self).__init__(session)
        self.logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

    def _discover(self, event):
        '''Inject Perforce icon into the attribute dictionary.'''
        my_dict = super(PerforceAttributeAction, self)._discover(event)
        if my_dict is None:
            return my_dict

        my_dict['items'][0].update({'icon': ICON_URL})
        return my_dict

    def discover(self, session, entities, event):
        '''Return True to be discovered when *entities* is a single Project.'''
        if not entities or len(entities) != 1:
            return False

        entity_type, entity_id = entities[0]
        #if not self._user_is_admin(
        #    username=event['source']['user']['username'], project_id=entity_id
        #):
        return False

        #return entity_type == 'Project'

    def launch(self, session, entities, event):
        # It is possible but unlikely that someone has launched the event
        # directly, so ensure the source a valid user.
        if not self.discover(session, entities, event):
            return False

        entity_type, entity_id = entities[0]
        values = event['data'].get('values', {})
        project = self.session.get(entity_type, entity_id)

        self.session.commit()

        return True

    @property
    def connection(self):
        '''Return connection to Perforce server.'''
        perforce_location = self.session.query(
            'Location where name is "{0}"'.format(SCENARIO_ID)
        ).one()
        return perforce_location.resource_identifier_transformer.connection

    def _create_depot(self, depot_name):
        self.logger.debug('Creating new depot : {}'.format(depot_name))
        try:
            self.connection.save_depot(
                {
                    'Depot': depot_name,
                    'Map': '{0}/...'.format(depot_name),
                    'Description': 'Created by ftrack.',
                    'Type': 'local',
                }
            )
        except P4Exception as error:
            self.logger.exception(error)

    def _sanitise(self, name):
        try:
            perforce_location = self.session.query(
                'Location where name is "{0}"'.format(SCENARIO_ID)
            ).one()
            return perforce_location.structure.sanitise_for_filesystem(name)
        except AttributeError:
            return StandardStructure().sanitise_for_filesystem(name)

    def _update_workspace_map(self, new_depot):
        self.logger.debug('Updating workspace map with : {}'.format(new_depot))
        workspace = self.connection.fetch_client('-o')
        new_mapping = '//{0}/... "//{1}/{0}/..."'.format(new_depot, workspace['Client'])
        mappings = P4.Map(workspace['View']).as_array()
        if new_mapping in mappings:
            self.logger.info(
                'Depot already in client view. Not adding: {0}'.format(new_mapping)
            )
            return

        mappings.append(new_mapping)
        workspace['View'] = mappings
        self.connection.save_client(workspace)

    def _user_is_admin(self, username, project_id):
        # check perforce super role
        perforce_super_role = any(
            protect
            for protect in self.connection.run_protects()
            if protect['perm'] == 'super'
        )
        return perforce_super_role
