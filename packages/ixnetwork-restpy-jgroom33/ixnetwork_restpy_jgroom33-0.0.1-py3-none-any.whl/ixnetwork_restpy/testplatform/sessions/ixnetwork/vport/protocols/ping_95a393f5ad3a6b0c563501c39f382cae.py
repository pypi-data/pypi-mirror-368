
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Ping(Base):
    """ "Packet Internet Groper/PING" uses Internet Message Control Protocol (ICMP) echo messages and responses.
    The Ping class encapsulates a list of ping resources that are managed by the user.
    A list of resources can be retrieved from the server using the Ping.find() method.
    The list can be managed by using the Ping.add() and Ping.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "ping"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Ping, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Enables IPv4 PING transmission and reception for this port. PING messages are IPv4 ICMP messages of type Echo Request. Responses are IPv4 ICMP message of type Echo Response.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, Enabled=None):
        # type: (bool) -> Ping
        """Updates ping resource on the server.

        Args
        ----
        - Enabled (bool): Enables IPv4 PING transmission and reception for this port. PING messages are IPv4 ICMP messages of type Echo Request. Responses are IPv4 ICMP message of type Echo Response.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Enabled=None):
        # type: (bool) -> Ping
        """Adds a new ping resource on the server and adds it to the container.

        Args
        ----
        - Enabled (bool): Enables IPv4 PING transmission and reception for this port. PING messages are IPv4 ICMP messages of type Echo Request. Responses are IPv4 ICMP message of type Echo Response.

        Returns
        -------
        - self: This instance with all currently retrieved ping resources using find and the newly added ping resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained ping resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Enabled=None):
        # type: (bool) -> Ping
        """Finds and retrieves ping resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve ping resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all ping resources from the server.

        Args
        ----
        - Enabled (bool): Enables IPv4 PING transmission and reception for this port. PING messages are IPv4 ICMP messages of type Echo Request. Responses are IPv4 ICMP message of type Echo Response.

        Returns
        -------
        - self: This instance with matching ping resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of ping data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the ping resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
