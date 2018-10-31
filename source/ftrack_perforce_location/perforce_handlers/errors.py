# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack


class PerforceHandlerException(Exception):
    pass


class PerforceConnectionHandlerException(PerforceHandlerException):
    pass


class PerforceFileHandlerException(PerforceHandlerException):
    pass


class PerforceChangeHanderException(PerforceHandlerException):
    pass


class PerforceSettingsHandlerException(PerforceHandlerException):
    pass