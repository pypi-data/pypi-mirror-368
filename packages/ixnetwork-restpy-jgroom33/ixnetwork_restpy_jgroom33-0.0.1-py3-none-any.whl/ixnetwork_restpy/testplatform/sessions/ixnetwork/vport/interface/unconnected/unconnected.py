
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Unconnected(Base):
    """Unconnected protocol interfaces that are not connected by any links to the SUT or to other Ixia ports. The unconnected interfaces can be set up to link the Ixia-emulated router to virtual networks "behind" the router, such as emulated OSPF network ranges.
    The Unconnected class encapsulates a required unconnected resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "unconnected"
    _SDM_ATT_MAP = {
        "ConnectedVia": "connectedVia",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Unconnected, self).__init__(parent, list_op)

    @property
    def ConnectedVia(self):
        # type: () -> str
        """
        Returns
        -------
        - str(None | /api/v1/sessions/1/ixnetwork/vport/interface): The name of a specified connected protocol interface on the link that is directly connected to the DUT.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ConnectedVia"])

    @ConnectedVia.setter
    def ConnectedVia(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["ConnectedVia"], value)

    def update(self, ConnectedVia=None):
        # type: (str) -> Unconnected
        """Updates unconnected resource on the server.

        Args
        ----
        - ConnectedVia (str(None | /api/v1/sessions/1/ixnetwork/vport/interface)): The name of a specified connected protocol interface on the link that is directly connected to the DUT.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, ConnectedVia=None):
        # type: (str) -> Unconnected
        """Finds and retrieves unconnected resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve unconnected resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all unconnected resources from the server.

        Args
        ----
        - ConnectedVia (str(None | /api/v1/sessions/1/ixnetwork/vport/interface)): The name of a specified connected protocol interface on the link that is directly connected to the DUT.

        Returns
        -------
        - self: This instance with matching unconnected resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of unconnected data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the unconnected resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
