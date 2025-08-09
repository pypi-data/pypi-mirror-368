from logos_cdi.abstract import AbstractContext


class LogosException(Exception):

    def __init__(self, message: str, context: AbstractContext):
        super().__init__(message)
        self.context = context


class ResourceNotFoundException(LogosException):

    def __init__(self, resource_name: str, context: AbstractContext):
        super().__init__(f'resource "{resource_name}" not found', context)
        self.resource_name = resource_name
