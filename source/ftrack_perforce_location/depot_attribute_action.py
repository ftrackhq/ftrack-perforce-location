# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_action_handler.action import BaseAction
import P4

from ftrack_perforce_location.constants import SCENARIO_ID


ICON_URL = 'https://bam.gallerycdn.vsassets.io/extensions/bam/vscode-perforce/1.1.3/1498206133077/Microsoft.VisualStudio.Services.Icons.Default'


class PerforceAttributeAction(BaseAction):
    label = 'Configure Project Perforce'
    identifier = 'com.ftrack.ftrack_perforce_location.perforce_attribute'
    description = 'Configure various Perforce options for the current project'

    def _discover(self, event):
        '''Inject Perforce icon into the attribute dictionary.'''
        my_dict = super(PerforceAttributeAction, self)._discover(event)
        if my_dict is None:
            return my_dict

        my_dict['items'][0].update({'icon': ICON_URL})
        return my_dict

    def discover(self, session, entities, event):
        '''Return True to be discovered when *entities* is a single Project.
        '''
        if not entities or len(entities) != 1:
            return False

        entity_type, entity_id = entities[0]
        if not self._user_is_admin(
            username=event['source']['user']['username'],
                project_id=entity_id):
            return False

        return entity_type == 'Project'

    def interface(self, session, entities, event):
        values = event['data'].get('values', {})
        if values:
            return

        entity_type, entity_id = entities[0]

        self._create_attribute(entity_id)

        project = self.session.get(entity_type, entity_id)
        # Custom attributes are cached, but we want to be sure our value is
        # up to date
        del project['custom_attributes']
        self.session.populate(project, 'custom_attributes')
        current_value = project['custom_attributes'].get(
            'own_perforce_depot', False)

        widgets = [{
            'type': 'boolean',
            'label': 'Project should have its own Perforce depot:',
            'name': 'own_depot',
            'value': current_value
        }]

        return widgets

    def launch(self, session, entities, event):
        # It is possible but unlikely that someone has launched the event
        # directly. Let's make sure the source a valid user.
        if not self.discover(session, entities, event):
            return False

        entity_type, entity_id = entities[0]
        values = event['data'].get('values', {})
        project = self.session.get(entity_type, entity_id)
        project['custom_attributes']['own_perforce_depot'] = (
            values['own_depot'])
        self.session.commit()

        if values['own_depot']:
            depot_name = str(self._sanitise(project['name']))
            if depot_name not in (depot['name'] for depot
                                  in self.connection.run_depots()):
                self._create_depot(depot_name)
            self._update_workspace_map(depot_name)

        return True

    @property
    def connection(self):
        '''Return connection to Perforce server.'''
        perforce_location = self.session.query(
            'Location where name is "{0}"'.format(SCENARIO_ID)).one()
        return perforce_location.resource_identifier_transformer.connection

    def _create_attribute(self, project_id):
        admin_role = self.session.query(
            'SecurityRole where name is "{0}"'.format('Administrator')).one()
        all_roles = self.session.query('SecurityRole').all()
        attribute_group = self.session.ensure(
            'CustomAttributeGroup',
            {'name': 'Perforce'})
        boolean_type = self.session.query(
            'select id from CustomAttributeType where name is "{0}"'.format(
                'boolean')
        ).one()

        # Leaves roles off the identifying_keys list since the query
        # generated by ensure() would fail.
        perforce_attribute = self.session.ensure(
            'CustomAttributeConfiguration',
            {
                'default': 0,
                'entity_type': 'show',
                'group_id': attribute_group['id'],
                'key': 'own_perforce_depot',
                'label': 'Project requires own depot',
                'project_id': project_id,
                'read_security_roles': all_roles,
                'type_id': boolean_type['id'],
                'write_security_roles': [admin_role],
            },
            identifying_keys=['entity_type', 'key', 'project_id', 'type_id']
        )

        return perforce_attribute

    def _create_depot(self, depot_name):
        self.connection.save_depot({
            'Depot': depot_name,
            'Map': '{0}/...'.format(depot_name),
            'Description': 'Created by ftrack.',
            'Type': 'local'
        })

    def _sanitise(self, name):
        perforce_location = self.session.query(
            'Location where name is "{0}"'.format(SCENARIO_ID)).one()
        return perforce_location.structure.sanitise_for_filesystem(name)

    def _update_workspace_map(self, new_depot):
        workspace = self.connection.fetch_client('-o')
        map_ = P4.Map(workspace['View'])
        map_.insert(
            '//{0}/... //{1}/{0}/...'.format(
                new_depot, workspace['Client']
            )
        )
        workspace['View'] = map_.as_array()
        self.connection.save_client(workspace)

    def _user_is_admin(self, username, project_id):
        appropriate_admin_role = self.session.query(
            'UserSecurityRole where user.username is "{0}"'
            ' and security_role.name is "Administrator"'
            ' and (is_all_projects is True'
            ' or projects any (id is "{1}"))'.format(
                username, project_id)).first()
        return appropriate_admin_role is not None
