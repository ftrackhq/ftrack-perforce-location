# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

expired_session_message = 'Your session has expired, please login again.'
invalid_password_message = 'Perforce password (P4PASSWD) invalid or unset.'


class PerforceLocationError(Exception):
    '''Base Location exception.'''


class PerforceHandlerException(Exception):
    '''Base Perforce exception.'''


class PerforceConnectionHandlerException(PerforceHandlerException):
    '''Perforce connection exception.'''


class PerforceInvalidPasswordException(PerforceConnectionHandlerException):
    '''Perforce invalid password exception.'''


class PerforceWorkspaceException(PerforceConnectionHandlerException):
    '''Perforce workspace exception.'''


class PerforceSessionExpiredException(PerforceConnectionHandlerException):
    '''Perforce expired session exception.'''


class PerforceFileHandlerException(PerforceHandlerException):
    '''Perforce file exception.'''


class PerforceChangeHanderException(PerforceHandlerException):
    '''Perforce change exception.'''


class PerforceSettingsHandlerException(PerforceHandlerException):
    '''Perforce settings exception.'''


class PerforceValidationError(Exception):
    '''Perforce configuration validation exception.'''
