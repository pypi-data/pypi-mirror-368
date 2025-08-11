from signature_validation_exception import SignatureValidationException


class SecretKeyNotAvailableException(SignatureValidationException):
    """
    Represents an error that causes a secret key to not be available.
    """

    def __init__(self, key_id, message=None, cause=None):
        super(SecretKeyNotAvailableException, self).__init__(message=message,
                                                             cause=cause)
        self.__key_id = key_id

    @property
    def key_id(self):
        return self.__key_id
