class ErrorInfrastructure(Exception):
    pass


class UseCaseError(Exception):
    pass


class SIATException(Exception):
    pass


class SIATInfrastructureError(SIATException):
    pass


class SIATValidationError(SIATException):
    pass


class SincproTimeoutException(Exception):
    pass


class SincproNoResultFound(Exception):
    pass
