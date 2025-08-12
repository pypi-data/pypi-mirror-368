
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Delay(Base):
    """Delay each packet.
    The Delay class encapsulates a required delay resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "delay"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "Units": "units",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {
        "units": [
            "kilometers",
            "kKilometers",
            "kMicroseconds",
            "kMilliseconds",
            "kSeconds",
            "microseconds",
            "milliseconds",
            "seconds",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(Delay, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, delay packets.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def Units(self):
        # type: () -> str
        """
        Returns
        -------
        - str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds): Specify the units for the delay value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Units"])

    @Units.setter
    def Units(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Units"], value)

    @property
    def Value(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Time to delay each packet.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Enabled=None, Units=None, Value=None):
        # type: (bool, str, int) -> Delay
        """Updates delay resource on the server.

        Args
        ----
        - Enabled (bool): If true, delay packets.
        - Units (str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds)): Specify the units for the delay value.
        - Value (number): Time to delay each packet.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None, Units=None, Value=None):
        # type: (bool, str, int) -> Delay
        """Finds and retrieves delay resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve delay resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all delay resources from the server.

        Args
        ----
        - Enabled (bool): If true, delay packets.
        - Units (str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds)): Specify the units for the delay value.
        - Value (number): Time to delay each packet.

        Returns
        -------
        - self: This instance with matching delay resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of delay data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the delay resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
