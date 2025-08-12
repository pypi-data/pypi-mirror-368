
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class MeterStatsBandLearnedInformation(Base):
    """NOT DEFINED
    The MeterStatsBandLearnedInformation class encapsulates a list of meterStatsBandLearnedInformation resources that are managed by the system.
    A list of resources can be retrieved from the server using the MeterStatsBandLearnedInformation.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "meterStatsBandLearnedInformation"
    _SDM_ATT_MAP = {
        "DataPathId": "dataPathId",
        "DataPathIdAsHex": "dataPathIdAsHex",
        "InBandByteCount": "inBandByteCount",
        "InBandPacketCount": "inBandPacketCount",
        "LocalIp": "localIp",
        "MeterId": "meterId",
        "RemoteIp": "remoteIp",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(MeterStatsBandLearnedInformation, self).__init__(parent, list_op)

    @property
    def DataPathId(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The Data Path identifier of the OpenFlow controller.
        """
        return self._get_attribute(self._SDM_ATT_MAP["DataPathId"])

    @property
    def DataPathIdAsHex(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The Data Path identifier of the OpenFlow controller in hexadecimal format.
        """
        return self._get_attribute(self._SDM_ATT_MAP["DataPathIdAsHex"])

    @property
    def InBandByteCount(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Specifies Byte Band Count
        """
        return self._get_attribute(self._SDM_ATT_MAP["InBandByteCount"])

    @property
    def InBandPacketCount(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Specifies Packet Band Count
        """
        return self._get_attribute(self._SDM_ATT_MAP["InBandPacketCount"])

    @property
    def LocalIp(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Indicates the local IP of the Controller.
        """
        return self._get_attribute(self._SDM_ATT_MAP["LocalIp"])

    @property
    def MeterId(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Specifies Meter ID
        """
        return self._get_attribute(self._SDM_ATT_MAP["MeterId"])

    @property
    def RemoteIp(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The Remote IP address of the selected interface.
        """
        return self._get_attribute(self._SDM_ATT_MAP["RemoteIp"])

    def add(self):
        """Adds a new meterStatsBandLearnedInformation resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved meterStatsBandLearnedInformation resources using find and the newly added meterStatsBandLearnedInformation resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        DataPathId=None,
        DataPathIdAsHex=None,
        InBandByteCount=None,
        InBandPacketCount=None,
        LocalIp=None,
        MeterId=None,
        RemoteIp=None,
    ):
        # type: (int, str, int, int, str, int, str) -> MeterStatsBandLearnedInformation
        """Finds and retrieves meterStatsBandLearnedInformation resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve meterStatsBandLearnedInformation resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all meterStatsBandLearnedInformation resources from the server.

        Args
        ----
        - DataPathId (number): The Data Path identifier of the OpenFlow controller.
        - DataPathIdAsHex (str): The Data Path identifier of the OpenFlow controller in hexadecimal format.
        - InBandByteCount (number): Specifies Byte Band Count
        - InBandPacketCount (number): Specifies Packet Band Count
        - LocalIp (str): Indicates the local IP of the Controller.
        - MeterId (number): Specifies Meter ID
        - RemoteIp (str): The Remote IP address of the selected interface.

        Returns
        -------
        - self: This instance with matching meterStatsBandLearnedInformation resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of meterStatsBandLearnedInformation data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the meterStatsBandLearnedInformation resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
