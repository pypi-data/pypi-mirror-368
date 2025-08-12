
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class InterfaceDiscoveredAddress(Base):
    """The tab that shows description and ip of interface configured on this port.
    The InterfaceDiscoveredAddress class encapsulates a required interfaceDiscoveredAddress resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "interfaceDiscoveredAddress"
    _SDM_ATT_MAP = {
        "Description": "description",
        "IpAddress": "ipAddress",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(InterfaceDiscoveredAddress, self).__init__(parent, list_op)

    @property
    def Description(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Shows description of the interface.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Description"])

    @property
    def IpAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Shows IP address of the interface.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IpAddress"])

    def find(self, Description=None, IpAddress=None):
        # type: (str, str) -> InterfaceDiscoveredAddress
        """Finds and retrieves interfaceDiscoveredAddress resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve interfaceDiscoveredAddress resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all interfaceDiscoveredAddress resources from the server.

        Args
        ----
        - Description (str): Shows description of the interface.
        - IpAddress (str): Shows IP address of the interface.

        Returns
        -------
        - self: This instance with matching interfaceDiscoveredAddress resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of interfaceDiscoveredAddress data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the interfaceDiscoveredAddress resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
