

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