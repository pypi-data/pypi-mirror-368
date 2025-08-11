from abc import ABCMeta, abstractmethod

from connection import Connection


class PooledConnection(Connection):
    """
    Represents a pooled connection to the Worldline Global Collect platform server.
    Instead of setting up a new HTTP connection for each request, this
    connection uses a pool of HTTP connections.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def close_idle_connections(self, idle_time):
        """
        Closes all HTTP connections that have been idle for the specified time.
        This should also include all expired HTTP connections.

        :param idle_time: a datetime.timedelta object indicating the idle time
        """
        raise NotImplementedError

    @abstractmethod
    def close_expired_connections(self):
        """
        Closes all expired HTTP connections.
        """
        raise NotImplementedError
