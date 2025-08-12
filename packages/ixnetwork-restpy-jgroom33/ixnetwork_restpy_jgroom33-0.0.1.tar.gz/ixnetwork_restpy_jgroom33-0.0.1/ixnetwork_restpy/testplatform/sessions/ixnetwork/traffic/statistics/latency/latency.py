
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Latency(Base):
    """This object sets the latency mode to fetch related statistics for each mode.
    The Latency class encapsulates a required latency resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "latency"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "Mode": "mode",
    }
    _SDM_ENUM_MAP = {
        "mode": ["cutThrough", "forwardingDelay", "mef", "storeForward"],
    }

    def __init__(self, parent, list_op=False):
        super(Latency, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, latency statistics is enabled and if false, latency statistics is disabled.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def Mode(self):
        # type: () -> str
        """
        Returns
        -------
        - str(cutThrough | forwardingDelay | mef | storeForward): Latency statistics is generated according to the mode set if latency is enabled.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Mode"])

    @Mode.setter
    def Mode(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Mode"], value)

    def update(self, Enabled=None, Mode=None):
        # type: (bool, str) -> Latency
        """Updates latency resource on the server.

        Args
        ----
        - Enabled (bool): If true, latency statistics is enabled and if false, latency statistics is disabled.
        - Mode (str(cutThrough | forwardingDelay | mef | storeForward)): Latency statistics is generated according to the mode set if latency is enabled.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None, Mode=None):
        # type: (bool, str) -> Latency
        """Finds and retrieves latency resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve latency resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all latency resources from the server.

        Args
        ----
        - Enabled (bool): If true, latency statistics is enabled and if false, latency statistics is disabled.
        - Mode (str(cutThrough | forwardingDelay | mef | storeForward)): Latency statistics is generated according to the mode set if latency is enabled.

        Returns
        -------
        - self: This instance with matching latency resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of latency data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the latency resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
