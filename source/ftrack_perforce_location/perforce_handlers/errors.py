# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack


class PerforceLocationError(Exception):
    '''Base Location exception.'''


class PerforceHandlerException(Exception):
    '''Base Perforce exception.'''


class PerforceConnectionHandlerException(PerforceHandlerException):
    '''Perforce connection exception.'''


class PerforceFileHandlerException(PerforceHandlerException):
    '''Perforce file exception.'''


class PerforceChangeHanderException(PerforceHandlerException):
    '''Perforce change exception.'''


class PerforceSettingsHandlerException(PerforceHandlerException):
    '''Perforce settings exception.'''


class PerforceValidationError(Exception):
    '''Perforce configuration validation exception.'''
