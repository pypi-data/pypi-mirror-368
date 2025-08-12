
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Atm(Base):
    """On Asynchronous Transport Mode (ATM) is a Layer 2, connection-oriented, switching protocol, based on L2 Virtual Circuits (VCs). For operation in a connection-less IP routing or bridging environment, the IP PDUs must be encapsulated within the payload field of an ATM AAL5 CPCS-PDU (ATM Adaptation Layer 5 - Common Part Convergence Sublayer - Protocol Data Unit). The ATM CPCS-PDUs are divided into 48-byte segments which receive 5-byte headers - to form 53-byte ATM cells. The ATM cells are then switched across the ATM network, based on the Virtual Port Identifiers (VPIs) and the Virtual Connection Identifiers (VCIs).
    The Atm class encapsulates a required atm resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "atm"
    _SDM_ATT_MAP = {
        "Encapsulation": "encapsulation",
        "Vci": "vci",
        "Vpi": "vpi",
    }
    _SDM_ENUM_MAP = {
        "encapsulation": [
            "vcMuxIpv4",
            "vcMuxIpv6",
            "vcMuxBridgeFcs",
            "vcMuxBridgeNoFcs",
            "llcClip",
            "llcBridgeFcs",
            "llcBridgeNoFcs",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(Atm, self).__init__(parent, list_op)

    @property
    def Encapsulation(self):
        # type: () -> str
        """
        Returns
        -------
        - str(vcMuxIpv4 | vcMuxIpv6 | vcMuxBridgeFcs | vcMuxBridgeNoFcs | llcClip | llcBridgeFcs | llcBridgeNoFcs): The type of RFC 2684 ATM multiplexing encapsulation (routing) protocol to be used.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Encapsulation"])

    @Encapsulation.setter
    def Encapsulation(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Encapsulation"], value)

    @property
    def Vci(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Virtual Circuit/Connection Identifier (VCI) for the ATM VC over which information is being transmitted.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Vci"])

    @Vci.setter
    def Vci(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Vci"], value)

    @property
    def Vpi(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Virtual Path Identifier (VPI) for the ATM VC over which information is being transmitted.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Vpi"])

    @Vpi.setter
    def Vpi(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Vpi"], value)

    def update(self, Encapsulation=None, Vci=None, Vpi=None):
        # type: (str, int, int) -> Atm
        """Updates atm resource on the server.

        Args
        ----
        - Encapsulation (str(vcMuxIpv4 | vcMuxIpv6 | vcMuxBridgeFcs | vcMuxBridgeNoFcs | llcClip | llcBridgeFcs | llcBridgeNoFcs)): The type of RFC 2684 ATM multiplexing encapsulation (routing) protocol to be used.
        - Vci (number): Virtual Circuit/Connection Identifier (VCI) for the ATM VC over which information is being transmitted.
        - Vpi (number): Virtual Path Identifier (VPI) for the ATM VC over which information is being transmitted.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Encapsulation=None, Vci=None, Vpi=None):
        # type: (str, int, int) -> Atm
        """Finds and retrieves atm resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve atm resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all atm resources from the server.

        Args
        ----
        - Encapsulation (str(vcMuxIpv4 | vcMuxIpv6 | vcMuxBridgeFcs | vcMuxBridgeNoFcs | llcClip | llcBridgeFcs | llcBridgeNoFcs)): The type of RFC 2684 ATM multiplexing encapsulation (routing) protocol to be used.
        - Vci (number): Virtual Circuit/Connection Identifier (VCI) for the ATM VC over which information is being transmitted.
        - Vpi (number): Virtual Path Identifier (VPI) for the ATM VC over which information is being transmitted.

        Returns
        -------
        - self: This instance with matching atm resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of atm data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the atm resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
