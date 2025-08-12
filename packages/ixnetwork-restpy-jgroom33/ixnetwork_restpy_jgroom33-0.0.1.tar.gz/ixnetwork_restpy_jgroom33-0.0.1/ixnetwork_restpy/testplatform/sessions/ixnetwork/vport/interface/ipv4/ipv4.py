
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Ipv4(Base):
    """Controls the general IPv4 interface properties.
    The Ipv4 class encapsulates a list of ipv4 resources that are managed by the user.
    A list of resources can be retrieved from the server using the Ipv4.find() method.
    The list can be managed by using the Ipv4.add() and Ipv4.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "ipv4"
    _SDM_ATT_MAP = {
        "Gateway": "gateway",
        "Ip": "ip",
        "MaskWidth": "maskWidth",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Ipv4, self).__init__(parent, list_op)

    @property
    def Gateway(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The IPv4 address of the Gateway to the network, typically an interface on the DUT.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Gateway"])

    @Gateway.setter
    def Gateway(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Gateway"], value)

    @property
    def Ip(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The 32-bit IPv4 address assigned to this unconnected interface.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Ip"])

    @Ip.setter
    def Ip(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Ip"], value)

    @property
    def MaskWidth(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The number of bits in the mask used with the IPv4 address. The default is 24 bits.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaskWidth"])

    @MaskWidth.setter
    def MaskWidth(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MaskWidth"], value)

    def update(self, Gateway=None, Ip=None, MaskWidth=None):
        # type: (str, str, int) -> Ipv4
        """Updates ipv4 resource on the server.

        Args
        ----
        - Gateway (str): The IPv4 address of the Gateway to the network, typically an interface on the DUT.
        - Ip (str): The 32-bit IPv4 address assigned to this unconnected interface.
        - MaskWidth (number): The number of bits in the mask used with the IPv4 address. The default is 24 bits.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Gateway=None, Ip=None, MaskWidth=None):
        # type: (str, str, int) -> Ipv4
        """Adds a new ipv4 resource on the server and adds it to the container.

        Args
        ----
        - Gateway (str): The IPv4 address of the Gateway to the network, typically an interface on the DUT.
        - Ip (str): The 32-bit IPv4 address assigned to this unconnected interface.
        - MaskWidth (number): The number of bits in the mask used with the IPv4 address. The default is 24 bits.

        Returns
        -------
        - self: This instance with all currently retrieved ipv4 resources using find and the newly added ipv4 resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained ipv4 resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Gateway=None, Ip=None, MaskWidth=None):
        # type: (str, str, int) -> Ipv4
        """Finds and retrieves ipv4 resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve ipv4 resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all ipv4 resources from the server.

        Args
        ----
        - Gateway (str): The IPv4 address of the Gateway to the network, typically an interface on the DUT.
        - Ip (str): The 32-bit IPv4 address assigned to this unconnected interface.
        - MaskWidth (number): The number of bits in the mask used with the IPv4 address. The default is 24 bits.

        Returns
        -------
        - self: This instance with matching ipv4 resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of ipv4 data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the ipv4 resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
