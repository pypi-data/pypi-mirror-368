
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class DhcpHostsRange(Base):
    """Manages a range of IP addresses that are configured using DHCP protocol.
    The DhcpHostsRange class encapsulates a required dhcpHostsRange resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "dhcpHostsRange"
    _SDM_ATT_MAP = {
        "Count": "count",
        "Enabled": "enabled",
        "EuiIncrement": "euiIncrement",
        "FirstEui": "firstEui",
        "IpPrefix": "ipPrefix",
        "IpType": "ipType",
        "Name": "name",
        "ObjectId": "objectId",
        "SubnetCount": "subnetCount",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(DhcpHostsRange, self).__init__(parent, list_op)

    @property
    def Count(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The number of hosts
        """
        return self._get_attribute(self._SDM_ATT_MAP["Count"])

    @Count.setter
    def Count(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Count"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Disabled ranges won't be configured nor validated.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def EuiIncrement(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Defines the EUI increment.
        """
        return self._get_attribute(self._SDM_ATT_MAP["EuiIncrement"])

    @EuiIncrement.setter
    def EuiIncrement(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["EuiIncrement"], value)

    @property
    def FirstEui(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Defines the first EUI to be used.
        """
        return self._get_attribute(self._SDM_ATT_MAP["FirstEui"])

    @FirstEui.setter
    def FirstEui(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["FirstEui"], value)

    @property
    def IpPrefix(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The network prefix length associated with this address pool.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IpPrefix"])

    @IpPrefix.setter
    def IpPrefix(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["IpPrefix"], value)

    @property
    def IpType(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The IP version to be used for describing the range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IpType"])

    @IpType.setter
    def IpType(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["IpType"], value)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Name of range
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    @Name.setter
    def Name(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Name"], value)

    @property
    def ObjectId(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Unique identifier for this object
        """
        return self._get_attribute(self._SDM_ATT_MAP["ObjectId"])

    @property
    def SubnetCount(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The number of subnets.
        """
        return self._get_attribute(self._SDM_ATT_MAP["SubnetCount"])

    @SubnetCount.setter
    def SubnetCount(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["SubnetCount"], value)

    def update(
        self,
        Count=None,
        Enabled=None,
        EuiIncrement=None,
        FirstEui=None,
        IpPrefix=None,
        IpType=None,
        Name=None,
        SubnetCount=None,
    ):
        # type: (int, bool, str, str, int, str, str, int) -> DhcpHostsRange
        """Updates dhcpHostsRange resource on the server.

        Args
        ----
        - Count (number): The number of hosts
        - Enabled (bool): Disabled ranges won't be configured nor validated.
        - EuiIncrement (str): Defines the EUI increment.
        - FirstEui (str): Defines the first EUI to be used.
        - IpPrefix (number): The network prefix length associated with this address pool.
        - IpType (str): The IP version to be used for describing the range.
        - Name (str): Name of range
        - SubnetCount (number): The number of subnets.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        Count=None,
        Enabled=None,
        EuiIncrement=None,
        FirstEui=None,
        IpPrefix=None,
        IpType=None,
        Name=None,
        ObjectId=None,
        SubnetCount=None,
    ):
        # type: (int, bool, str, str, int, str, str, str, int) -> DhcpHostsRange
        """Finds and retrieves dhcpHostsRange resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve dhcpHostsRange resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all dhcpHostsRange resources from the server.

        Args
        ----
        - Count (number): The number of hosts
        - Enabled (bool): Disabled ranges won't be configured nor validated.
        - EuiIncrement (str): Defines the EUI increment.
        - FirstEui (str): Defines the first EUI to be used.
        - IpPrefix (number): The network prefix length associated with this address pool.
        - IpType (str): The IP version to be used for describing the range.
        - Name (str): Name of range
        - ObjectId (str): Unique identifier for this object
        - SubnetCount (number): The number of subnets.

        Returns
        -------
        - self: This instance with matching dhcpHostsRange resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of dhcpHostsRange data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the dhcpHostsRange resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)

    def CustomProtocolStack(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """Executes the customProtocolStack operation on the server.

        Create custom protocol stack under /vport/protocolStack

        customProtocolStack(Arg2=list, Arg3=enum, async_operation=bool)
        ---------------------------------------------------------------
        - Arg2 (list(str)): List of plugin types to be added in the new custom stack
        - Arg3 (str(kAppend | kMerge | kOverwrite)): Append, merge or overwrite existing protocol stack
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        payload = {"Arg1": self}
        for i in range(len(args)):
            payload["Arg%s" % (i + 2)] = args[i]
        for item in kwargs.items():
            payload[item[0]] = item[1]
        return self._execute(
            "customProtocolStack", payload=payload, response_object=None
        )

    def DisableProtocolStack(self, *args, **kwargs):
        # type: (*Any, **Any) -> Union[str, None]
        """Executes the disableProtocolStack operation on the server.

        Disable a protocol under protocolStack using the class name

        disableProtocolStack(Arg2=string, async_operation=bool)string
        -------------------------------------------------------------
        - Arg2 (str): Protocol class name to disable
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.
        - Returns str: Status of the exec

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
            "disableProtocolStack", payload=payload, response_object=None
        )

    def EnableProtocolStack(self, *args, **kwargs):
        # type: (*Any, **Any) -> Union[str, None]
        """Executes the enableProtocolStack operation on the server.

        Enable a protocol under protocolStack using the class name

        enableProtocolStack(Arg2=string, async_operation=bool)string
        ------------------------------------------------------------
        - Arg2 (str): Protocol class name to enable
        - async_operation (bool=False): True to execute the operation asynchronously. Any subsequent rest api calls made through the Connection class will block until the operation is complete.
        - Returns str: Status of the exec

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
            "enableProtocolStack", payload=payload, response_object=None
        )
