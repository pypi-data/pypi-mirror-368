class ClientError(Exception):
    pass


class UnauthorizedError(ClientError):
    pass


class NoAccessError(ClientError):
    pass


class InputDataError(ClientError):
    pass


class MethodError(ClientError):
    pass


class TooManyRequestsError(ClientError):
    pass


class ServerError(ClientError):
    pass


class RedirectError(ClientError):
    pass
