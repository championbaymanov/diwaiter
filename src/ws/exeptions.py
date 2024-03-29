from typing import Union


class WSBaseCustomException(Exception):
    default_message = "Exception occured"

    def init(self, message: Union[str, None] = None, errors: Union[str, None] = None):
        super(WSBaseCustomException, self).init(str(message), errors)
        self.message = str(message) if message is not None else self.default_message


class PermissionDenied(WSBaseCustomException):
    status = 403
    default_message = "У вас нет разрешения на выполнение этого действия"


class NotFound(WSBaseCustomException):
    status = 404
    default_message = "Object not Found!"


class ValidationError(WSBaseCustomException):
    status = 400
    default_message = "Validation error"