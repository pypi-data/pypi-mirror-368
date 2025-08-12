
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class PortTestOptions(Base):
    """
    The PortTestOptions class encapsulates a required portTestOptions resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "portTestOptions"
    _SDM_ATT_MAP = {
        "EnableDpdkPerformanceAcceleration": "enableDpdkPerformanceAcceleration",
        "PortLldpOperation": "portLldpOperation",
    }
    _SDM_ENUM_MAP = {
        "portLldpOperation": ["noOp", "enablePortLldp", "disablePortLldp"],
    }

    def __init__(self, parent, list_op=False):
        super(PortTestOptions, self).__init__(parent, list_op)

    @property
    def EnableDpdkPerformanceAcceleration(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Enable DPDK traffic engine mode for performance acceleration in data plane.
        """
        return self._get_attribute(
            self._SDM_ATT_MAP["EnableDpdkPerformanceAcceleration"]
        )

    @EnableDpdkPerformanceAcceleration.setter
    def EnableDpdkPerformanceAcceleration(self, value):
        # type: (bool) -> None
        self._set_attribute(
            self._SDM_ATT_MAP["EnableDpdkPerformanceAcceleration"], value
        )

    @property
    def PortLldpOperation(self):
        # type: () -> str
        """
        Returns
        -------
        - str(noOp | enablePortLldp | disablePortLldp): Port LLDP operation performed during port connect/reboot. Please reconnect or reboot the port(s) for this to take effect.
        """
        return self._get_attribute(self._SDM_ATT_MAP["PortLldpOperation"])

    @PortLldpOperation.setter
    def PortLldpOperation(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["PortLldpOperation"], value)

    def update(self, EnableDpdkPerformanceAcceleration=None, PortLldpOperation=None):
        # type: (bool, str) -> PortTestOptions
        """Updates portTestOptions resource on the server.

        Args
        ----
        - EnableDpdkPerformanceAcceleration (bool): Enable DPDK traffic engine mode for performance acceleration in data plane.
        - PortLldpOperation (str(noOp | enablePortLldp | disablePortLldp)): Port LLDP operation performed during port connect/reboot. Please reconnect or reboot the port(s) for this to take effect.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, EnableDpdkPerformanceAcceleration=None, PortLldpOperation=None):
        # type: (bool, str) -> PortTestOptions
        """Finds and retrieves portTestOptions resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve portTestOptions resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all portTestOptions resources from the server.

        Args
        ----
        - EnableDpdkPerformanceAcceleration (bool): Enable DPDK traffic engine mode for performance acceleration in data plane.
        - PortLldpOperation (str(noOp | enablePortLldp | disablePortLldp)): Port LLDP operation performed during port connect/reboot. Please reconnect or reboot the port(s) for this to take effect.

        Returns
        -------
        - self: This instance with matching portTestOptions resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of portTestOptions data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the portTestOptions resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
