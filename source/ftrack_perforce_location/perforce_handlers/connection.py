import os
import socket
import logging
from P4 import P4, P4Exception, Map
from ftrack_perforce_location.perforce_handlers.errors import PerforceConnectionHandlerException


class PerforceConnectionHandler(object):

    @property
    def info(self):
        return self.connection.run('info')[0]

    @property
    def server(self):
        return self._server

    @property
    def port(self):
        return self._port

    @property
    def connection(self):
        return self._connection

    @property
    def workspace(self):
        return self._workspace

    def __init__(self,
        server=None, port=None,
        user=None, password=None,
        using_workspace=None,
        workspace_root=None
    ):

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._server = server
        self._port = port
        self._connection = None
        self._user = user
        self._password = password
        self._hostname = socket.gethostname()
        self._workspace = None
        self._workspace_root = workspace_root

        self.connect(using_workspace)

    def connect(self, using_workspace):
        if self._connect():
            self._login()

        self.connection.client = self._get_workspace(using_workspace)

    def _connect(self):
        p4 = P4()
        p4.host = str(self.server)
        p4.port = str(self.port)
        p4.user = str(self._user)
        p4.password = str(self._password)

        self.logger.debug(
            'Connecting to : {0}:{1}'.format(self.server, self.port)
        )

        try:
            p4.connect()
        except P4Exception as error:
            print error
            return False

        self._connection = p4
        return True

    def _get_workspace(self, using_workspace):
        workspaces = self.connection.run_clients("-u", self._user)
        filtered_workspaces = [ws for ws in workspaces if (ws.get("Host") or self._hostname) == self._hostname]
        filtered_workspaces = [ws for ws in filtered_workspaces if ws.get('client') == using_workspace]
        if not filtered_workspaces:
            raise PerforceConnectionHandlerException('No worspace found named : {}'.format(using_workspace))

        workspace = filtered_workspaces[0].get('client')
        self.logger.debug('getting workspace :{}'.format(workspace))
        return workspace

    def _login(self):

        self.logger.debug(
            'Logging in as: {0}'.format(self._user)
        )
        self._connection.run_login(self._user)

    def disconnect(self):
        if self.connection.connected():
            self.connection.disconnect()
        self._connection = None