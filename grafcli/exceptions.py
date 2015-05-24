from climb.exceptions import CLIException


class HostConfigError(CLIException):
    pass


class MissingHostName(CLIException):
    pass


class MissingTemplateCategory(CLIException):
    pass


class InvalidPath(CLIException):
    pass


class InvalidDocument(CLIException):
    pass


class DocumentNotFound(CLIException):
    pass


class CommandCancelled(CLIException):
    pass
