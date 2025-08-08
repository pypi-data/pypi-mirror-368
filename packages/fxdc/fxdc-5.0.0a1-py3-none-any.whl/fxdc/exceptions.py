# EXCEPTIONS
class FXDCException(Exception):
    def __init__(self, *args, **kw) -> None:
        if self.__class__ is FXDCException:
            raise RuntimeError(
                "FXDCException should not be instantiated directly"
            )
        super().__init__(*args, **kw)

    def _get_code(self):
        return self.code


class InvalidExtension(FXDCException):
    code = 1


class FileNotReadable(FXDCException):
    code = 2


class FileNotWritable(FXDCException):
    code = 3


class InvalidData(FXDCException):
    code = 5


class InvalidJSONKey(FXDCException):
    code = 6


class ClassAlreadyInitialized(FXDCException):
    code = 7

class FieldError(FXDCException):
    code = 8

class TypeCheckFailure(FXDCException):
    code = 9
    
class NullFailure(FXDCException):
    code = 10

class BlankFailure(FXDCException):
    code = 11
    
