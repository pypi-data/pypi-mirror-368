class CommunicationException(RuntimeError):
    """
    Indicates an exception regarding the communication with the Worldline Global Collect platform such as a connection exception.
    """

    def __init__(self, exception):
        super(CommunicationException, self).__init__(exception)
        self.cause = exception
