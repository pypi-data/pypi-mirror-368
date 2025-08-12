
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Datacenter(Base):
    """This node contains Data Center Settings.
    The Datacenter class encapsulates a required datacenter resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "datacenter"
    _SDM_ATT_MAP = {
        "AdditionalFcoeStat1": "additionalFcoeStat1",
        "AdditionalFcoeStat2": "additionalFcoeStat2",
        "EnableDataCenterSharedStats": "enableDataCenterSharedStats",
    }
    _SDM_ENUM_MAP = {
        "additionalFcoeStat1": [
            "fcoeInvalidDelimiter",
            "fcoeInvalidFrames",
            "fcoeInvalidSize",
            "fcoeNormalSizeBadFcCRC",
            "fcoeNormalSizeGoodFcCRC",
            "fcoeUndersizeBadFcCRC",
            "fcoeUndersizeGoodFcCRC",
            "fcoeValidFrames",
        ],
        "additionalFcoeStat2": [
            "fcoeInvalidDelimiter",
            "fcoeInvalidFrames",
            "fcoeInvalidSize",
            "fcoeNormalSizeBadFcCRC",
            "fcoeNormalSizeGoodFcCRC",
            "fcoeUndersizeBadFcCRC",
            "fcoeUndersizeGoodFcCRC",
            "fcoeValidFrames",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(Datacenter, self).__init__(parent, list_op)

    @property
    def AdditionalFcoeStat1(self):
        # type: () -> str
        """
        Returns
        -------
        - str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames): Signifies additional FCOE stat 1
        """
        return self._get_attribute(self._SDM_ATT_MAP["AdditionalFcoeStat1"])

    @AdditionalFcoeStat1.setter
    def AdditionalFcoeStat1(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["AdditionalFcoeStat1"], value)

    @property
    def AdditionalFcoeStat2(self):
        # type: () -> str
        """
        Returns
        -------
        - str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames): Sets the additional FCoE shared stats.
        """
        return self._get_attribute(self._SDM_ATT_MAP["AdditionalFcoeStat2"])

    @AdditionalFcoeStat2.setter
    def AdditionalFcoeStat2(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["AdditionalFcoeStat2"], value)

    @property
    def EnableDataCenterSharedStats(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, enables statistics for Data Center.
        """
        return self._get_attribute(self._SDM_ATT_MAP["EnableDataCenterSharedStats"])

    @EnableDataCenterSharedStats.setter
    def EnableDataCenterSharedStats(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["EnableDataCenterSharedStats"], value)

    def update(
        self,
        AdditionalFcoeStat1=None,
        AdditionalFcoeStat2=None,
        EnableDataCenterSharedStats=None,
    ):
        # type: (str, str, bool) -> Datacenter
        """Updates datacenter resource on the server.

        Args
        ----
        - AdditionalFcoeStat1 (str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames)): Signifies additional FCOE stat 1
        - AdditionalFcoeStat2 (str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames)): Sets the additional FCoE shared stats.
        - EnableDataCenterSharedStats (bool): If true, enables statistics for Data Center.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        AdditionalFcoeStat1=None,
        AdditionalFcoeStat2=None,
        EnableDataCenterSharedStats=None,
    ):
        # type: (str, str, bool) -> Datacenter
        """Finds and retrieves datacenter resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve datacenter resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all datacenter resources from the server.

        Args
        ----
        - AdditionalFcoeStat1 (str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames)): Signifies additional FCOE stat 1
        - AdditionalFcoeStat2 (str(fcoeInvalidDelimiter | fcoeInvalidFrames | fcoeInvalidSize | fcoeNormalSizeBadFcCRC | fcoeNormalSizeGoodFcCRC | fcoeUndersizeBadFcCRC | fcoeUndersizeGoodFcCRC | fcoeValidFrames)): Sets the additional FCoE shared stats.
        - EnableDataCenterSharedStats (bool): If true, enables statistics for Data Center.

        Returns
        -------
        - self: This instance with matching datacenter resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of datacenter data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the datacenter resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
