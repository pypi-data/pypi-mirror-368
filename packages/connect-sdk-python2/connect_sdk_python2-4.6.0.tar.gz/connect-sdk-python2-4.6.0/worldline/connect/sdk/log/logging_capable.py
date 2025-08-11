from abc import ABCMeta, abstractmethod


class LoggingCapable(object):
    """
    Classes that extend this class have support for log messages from
    communicators.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def enable_logging(self, communicator_logger):
        """
        Turns on logging using the given communicator logger.

        :raise ValueError: If the given communicator logger is None.
        """
        raise NotImplementedError

    @abstractmethod
    def disable_logging(self):
        """
        Turns off logging.
        """
        raise NotImplementedError
