# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import logging
import socket
import uuid

from ftrack_perforce_location.import_p4api import import_p4

import_p4()


from P4 import P4, P4Exception
from ftrack_perforce_location.perforce_handlers import errors


class PerforceConnectionHandler(object):
    '''Handles credentials and login to Perforce server.'''

    @property
    def user(self):
        return self._user

    @property
    def host(self):
        return self._hostname

    @property
    def info(self):
        '''Return informations about the current connection.'''
        return self.connection.run_info()[0]

    @property
    def port(self):
        '''Return the current server port.'''
        return self._port

    @property
    def connection(self):
        '''Return the current server connection.'''
        return self._connection

    @property
    def workspace(self):
        '''Return the current workspace.'''
        return self._workspace

    def __init__(self, host=None, port=None, user=None, password=None,
                 using_workspace=None, workspace_root=None):
        '''Initialise Perforce connection handler
        **server** and **port** should point to a live Perforce server
        address to connect to.

        **user** and **password** should be the one registered on
        the Perforce server.

        **using_workspace** is the workspace name to be used on the server.
        **workspace_root** should point to a local folder where files
        will be published to.

        '''

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._port = port
        self._connection = None
        self._user = user
        self._password = password

        self._hostname = host if host is not None else socket.gethostname()
        self._workspace = None
        self._workspace_root = workspace_root
        self._using_workspace = using_workspace

        self.connect()

    def connect(self):
        '''Connect to the server and login.'''

        if self._connect():
            self._login()

        self.connection.client = self._get_workspace()

    def _connect(self):
        '''Handles connection to the server.'''

        p4 = P4()
        p4.host = str(self.host)
        p4.port = str(self.port)
        p4.user = str(self.user)
        p4.password = str(self._password)

        self.logger.debug(
            'Connecting to {0}'.format(
                p4.__repr__()
            )
        )

        try:
            p4.connect()
            if p4.port.startswith('ssl'):
                p4.run_trust('-y')
        except P4Exception as error:
            raise errors.PerforceConnectionHandlerException(error)

        self._connection = p4
        return True

    def _get_workspace(self):
        '''Lookup and return for the workspace to be used.'''
        workspaces = self.connection.run_clients("-u", self._user)
        filtered_workspaces = [
            ws for
            ws in workspaces
            if (ws.get("Host") or self.host) == self.host]
        filtered_workspaces = [
            ws for
            ws in filtered_workspaces
            if ws.get('client') == self._using_workspace]
        if filtered_workspaces:
            workspace = filtered_workspaces[0].get('client')
        else:
            self.logger.info(
                'Could not find valid workspace for {0} on {1}'.format(
                    self._user, self.host
                )
            )
            if self.connection.run_clients('-e', self._using_workspace):
                raise errors.PerforceWorkspaceException(
                    'Specified workspace already in use: {0}'.format(
                        self._using_workspace
                    )
                )
            self.logger.info('Creating new workspace . . .')
            new_workspace = self.create_workspace(
                self._workspace_root, self._using_workspace
            )
            workspace = new_workspace['Client']
        self.logger.debug('getting workspace: {0}'.format(workspace))
        return workspace

    def _login(self):
        '''Handles login to the server.'''

        try:
            self._connection.run_clients()
        except P4Exception as error:
            if len(error.errors) != 1:
                raise errors.PerforceConnectionHandlerException(error)
            if error.errors[0] in [
                errors.invalid_or_unset_password_message,
                errors.invalid_password_message,
            ]:
                pass
        else:
            self.logger.debug(
                'Already logged in as: {0}'.format(self._connection.user)
            )
            return

        self.logger.debug(
            'Logging in as: {0}'.format(self._user)
        )
        try:
            self._connection.run_login()
        except P4Exception as error:
            if len(error.errors) != 1:
                raise errors.PerforceConnectionHandlerException(error)
            if error.errors[0] == errors.expired_session_message:
                raise errors.PerforceSessionExpiredException(error)
            if error.errors[0] in [
                errors.invalid_or_unset_password_message,
                errors.invalid_password_message,
            ]:
                raise errors.PerforceInvalidPasswordException(error)
            raise errors.PerforceConnectionHandlerException(error)

    def disconnect(self):
        '''Handles server disconnection.'''
        if self.connection.connected():
            self.connection.disconnect()
        self._connection = None

    def create_workspace(self, client_root, client_name=None):
        if client_name is None:
            client_name = 'ftrack-{0}'.format(uuid.uuid4())
        workspace = self.connection.fetch_client(client_name)
        workspace['Root'] = str(client_root)
        self.connection.save_client(workspace)
        return workspace
