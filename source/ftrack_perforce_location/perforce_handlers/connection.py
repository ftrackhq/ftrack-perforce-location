# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import socket
import logging

from P4 import P4, P4Exception

from ftrack_perforce_location.perforce_handlers.errors import PerforceConnectionHandlerException


class PerforceConnectionHandler(object):
    '''Handles credentials and login to perforce server.'''

    @property
    def info(self):
        '''Return informations about the current connection.'''
        return self.connection.run('info')[0]

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
        '''Initialise perforce connection handler
        **server** and **port** should point to a live perforce server
        address to connect to.

        **user** and **password** should be the one registered on
        the perforce server.

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
        p4.host = str(self._hostname)
        p4.port = str(self.port)
        p4.user = str(self._user)
        p4.password = str(self._password)

        self.logger.debug(
            'Connecting to : {0}'.format(self.port)
        )

        try:
            p4.connect()
        except P4Exception as error:
            print error
            return False

        self._connection = p4
        return True

    def _get_workspace(self):
        '''Lookup and return for the workspace to be used.'''
        workspaces = self.connection.run_clients("-u", self._user)
        filtered_workspaces = [
            ws for
            ws in workspaces
            if (ws.get("Host") or self._hostname) == self._hostname]
        filtered_workspaces = [
            ws for
            ws in filtered_workspaces
            if ws.get('client') == self._using_workspace]
        if not filtered_workspaces:
            raise PerforceConnectionHandlerException(
                'No worspace found named : {}'.format(self._using_workspace))

        workspace = filtered_workspaces[0].get('client')
        self.logger.debug('getting workspace :{}'.format(workspace))
        return workspace

    def _login(self):
        '''Handles login to the server.'''

        self.logger.debug(
            'Logging in as: {0}'.format(self._user)
        )
        self._connection.run_login(self._user)

    def disconnect(self):
        '''Handles server disconnection.'''
        if self.connection.connected():
            self.connection.disconnect()
        self._connection = None
