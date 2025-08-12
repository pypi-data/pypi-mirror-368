
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class LatencyBin(Base):
    """This object provides different options for Latency Bin Tracking.
    The LatencyBin class encapsulates a required latencyBin resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "latencyBin"
    _SDM_ATT_MAP = {
        "BinLimits": "binLimits",
        "Enabled": "enabled",
        "NumberOfBins": "numberOfBins",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(LatencyBin, self).__init__(parent, list_op)

    @property
    def BinLimits(self):
        # type: () -> List[int]
        """
        Returns
        -------
        - list(number): Specifies the upper limit of each Time Bins for Latency Bin Tracking.
        """
        return self._get_attribute(self._SDM_ATT_MAP["BinLimits"])

    @BinLimits.setter
    def BinLimits(self, value):
        # type: (List[int]) -> None
        self._set_attribute(self._SDM_ATT_MAP["BinLimits"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, Latency Bin Tracking is enabled.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def NumberOfBins(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Specifies the number of Time Bins for Latency Bin Tracking.
        """
        return self._get_attribute(self._SDM_ATT_MAP["NumberOfBins"])

    @NumberOfBins.setter
    def NumberOfBins(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["NumberOfBins"], value)

    def update(self, BinLimits=None, Enabled=None, NumberOfBins=None):
        # type: (List[int], bool, int) -> LatencyBin
        """Updates latencyBin resource on the server.

        Args
        ----
        - BinLimits (list(number)): Specifies the upper limit of each Time Bins for Latency Bin Tracking.
        - Enabled (bool): If true, Latency Bin Tracking is enabled.
        - NumberOfBins (number): Specifies the number of Time Bins for Latency Bin Tracking.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, BinLimits=None, Enabled=None, NumberOfBins=None):
        # type: (List[int], bool, int) -> LatencyBin
        """Finds and retrieves latencyBin resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve latencyBin resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all latencyBin resources from the server.

        Args
        ----
        - BinLimits (list(number)): Specifies the upper limit of each Time Bins for Latency Bin Tracking.
        - Enabled (bool): If true, Latency Bin Tracking is enabled.
        - NumberOfBins (number): Specifies the number of Time Bins for Latency Bin Tracking.

        Returns
        -------
        - self: This instance with matching latencyBin resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of latencyBin data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the latencyBin resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
