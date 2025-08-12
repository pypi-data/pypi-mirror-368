
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Network(Base):
    """
    The Network class encapsulates a list of network resources that are managed by the system.
    A list of resources can be retrieved from the server using the Network.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "network"
    _SDM_ATT_MAP = {
        "NeighborRouterIds": "neighborRouterIds",
        "NetworkMask": "networkMask",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Network, self).__init__(parent, list_op)

    @property
    def NeighborRouterIds(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str):
        """
        return self._get_attribute(self._SDM_ATT_MAP["NeighborRouterIds"])

    @NeighborRouterIds.setter
    def NeighborRouterIds(self, value):
        # type: (List[str]) -> None
        self._set_attribute(self._SDM_ATT_MAP["NeighborRouterIds"], value)

    @property
    def NetworkMask(self):
        # type: () -> str
        """
        Returns
        -------
        - str:
        """
        return self._get_attribute(self._SDM_ATT_MAP["NetworkMask"])

    @NetworkMask.setter
    def NetworkMask(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["NetworkMask"], value)

    def update(self, NeighborRouterIds=None, NetworkMask=None):
        # type: (List[str], str) -> Network
        """Updates network resource on the server.

        Args
        ----
        - NeighborRouterIds (list(str)):
        - NetworkMask (str):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, NeighborRouterIds=None, NetworkMask=None):
        # type: (List[str], str) -> Network
        """Adds a new network resource on the json, only valid with batch add utility

        Args
        ----
        - NeighborRouterIds (list(str)):
        - NetworkMask (str):

        Returns
        -------
        - self: This instance with all currently retrieved network resources using find and the newly added network resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, NeighborRouterIds=None, NetworkMask=None):
        # type: (List[str], str) -> Network
        """Finds and retrieves network resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve network resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all network resources from the server.

        Args
        ----
        - NeighborRouterIds (list(str)):
        - NetworkMask (str):

        Returns
        -------
        - self: This instance with matching network resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of network data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the network resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
