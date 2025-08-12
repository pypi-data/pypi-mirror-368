
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class ConfigMANamesParams(Base):
    """Import IPv6 routes from standard route file. Supported format - Cisco IOS, Juniper JUNOS, Classis Ixia (.csv) and standard CSV.
    The ConfigMANamesParams class encapsulates a required configMANamesParams resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "configMANamesParams"
    _SDM_ATT_MAP = {
        "IncrementMaName": "incrementMaName",
        "MaName": "maName",
        "SmaFormat": "smaFormat",
    }
    _SDM_ENUM_MAP = {
        "smaFormat": [
            "megIdFormatTypeIccBasedFormat",
            "megIdFormatTypePrimaryVid",
            "megIdFormatTypeCharStr",
            "megIdFormatTypeTwoOctetInt",
            "megIdFormatTypeRfc2685VpnId",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(ConfigMANamesParams, self).__init__(parent, list_op)

    @property
    def IncrementMaName(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Import only the best routes (provided route file has this information).
        """
        return self._get_attribute(self._SDM_ATT_MAP["IncrementMaName"])

    @IncrementMaName.setter
    def IncrementMaName(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IncrementMaName"], value)

    @property
    def MaName(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Import only the best routes (provided route file has this information).
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaName"])

    @MaName.setter
    def MaName(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["MaName"], value)

    @property
    def SmaFormat(self):
        # type: () -> str
        """
        Returns
        -------
        - str(megIdFormatTypeIccBasedFormat | megIdFormatTypePrimaryVid | megIdFormatTypeCharStr | megIdFormatTypeTwoOctetInt | megIdFormatTypeRfc2685VpnId): Import only the best routes (provided route file has this information).
        """
        return self._get_attribute(self._SDM_ATT_MAP["SmaFormat"])

    @SmaFormat.setter
    def SmaFormat(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["SmaFormat"], value)

    def update(self, IncrementMaName=None, MaName=None, SmaFormat=None):
        # type: (bool, str, str) -> ConfigMANamesParams
        """Updates configMANamesParams resource on the server.

        Args
        ----
        - IncrementMaName (bool): Import only the best routes (provided route file has this information).
        - MaName (str): Import only the best routes (provided route file has this information).
        - SmaFormat (str(megIdFormatTypeIccBasedFormat | megIdFormatTypePrimaryVid | megIdFormatTypeCharStr | megIdFormatTypeTwoOctetInt | megIdFormatTypeRfc2685VpnId)): Import only the best routes (provided route file has this information).

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, IncrementMaName=None, MaName=None, SmaFormat=None):
        # type: (bool, str, str) -> ConfigMANamesParams
        """Finds and retrieves configMANamesParams resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve configMANamesParams resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all configMANamesParams resources from the server.

        Args
        ----
        - IncrementMaName (bool): Import only the best routes (provided route file has this information).
        - MaName (str): Import only the best routes (provided route file has this information).
        - SmaFormat (str(megIdFormatTypeIccBasedFormat | megIdFormatTypePrimaryVid | megIdFormatTypeCharStr | megIdFormatTypeTwoOctetInt | megIdFormatTypeRfc2685VpnId)): Import only the best routes (provided route file has this information).

        Returns
        -------
        - self: This instance with matching configMANamesParams resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of configMANamesParams data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the configMANamesParams resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)

    def AddDeleteTags(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Executes the addDeleteTags operation on the server.

        addDeleteTags(Arg2=bool, Arg3=bool, async_operation=bool)
        ---------------------------------------------------------
        - Arg2 (bool):
        - Arg3 (bool):
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        payload = {"Arg1": self.href}
        for i in range(len(args)):
            payload["Arg%s" % (i + 2)] = args[i]
        for item in kwargs.items():
            payload[item[0]] = item[1]
        return self._execute("addDeleteTags", payload=payload, response_object=None)

    def ConfigMANames(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Executes the configMANames operation on the server.

        Import IPv6 routes from standard route file. Supported format - Cisco IOS, Juniper JUNOS, Classis Ixia (.csv) and standard CSV.

        configMANames(async_operation=bool)
        -----------------------------------
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        payload = {"Arg1": self.href}
        for i in range(len(args)):
            payload["Arg%s" % (i + 2)] = args[i]
        for item in kwargs.items():
            payload[item[0]] = item[1]
        return self._execute("configMANames", payload=payload, response_object=None)

    def PerformActionOnAllObjects(self, *args, **kwargs):
        # type: (*Any, **Any) -> Union[str, None]
        """Executes the performActionOnAllObjects operation on the server.

        Action on All Objects

        performActionOnAllObjects(Arg2=string, async_operation=bool)string
        ------------------------------------------------------------------
        - Arg2 (str): Action Name
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.
        - Returns str:

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        payload = {"Arg1": self.href}
        for i in range(len(args)):
            payload["Arg%s" % (i + 2)] = args[i]
        for item in kwargs.items():
            payload[item[0]] = item[1]
        return self._execute(
            "performActionOnAllObjects", payload=payload, response_object=None
        )
