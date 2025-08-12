
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FcoeClientOptionTlv(Base):
    """A single TLV option.
    The FcoeClientOptionTlv class encapsulates a list of fcoeClientOptionTlv resources that are managed by the user.
    A list of resources can be retrieved from the server using the FcoeClientOptionTlv.find() method.
    The list can be managed by using the FcoeClientOptionTlv.add() and FcoeClientOptionTlv.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "fcoeClientOptionTlv"
    _SDM_ATT_MAP = {
        "Code": "code",
        "Name": "name",
        "ObjectId": "objectId",
        "Rfc": "rfc",
        "Type": "type",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {
        "type": [
            "boolean",
            "domainName",
            "hexadecimal",
            "integer16",
            "integer16List",
            "integer32",
            "integer32List",
            "integer8",
            "integer8List",
            "ipv4Address",
            "ipv4AddressList",
            "ipv4Prefix",
            "ipv6Address",
            "ipv6AddressList",
            "ipv6Prefix",
            "string",
            "zeroLength",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(FcoeClientOptionTlv, self).__init__(parent, list_op)

    @property
    def Code(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Option code.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Code"])

    @Code.setter
    def Code(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Code"], value)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Option name.
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
    def Rfc(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: True if defined in RFC documents.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Rfc"])

    @Rfc.setter
    def Rfc(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Rfc"], value)

    @property
    def Type(self):
        # type: () -> str
        """
        Returns
        -------
        - str(boolean | domainName | hexadecimal | integer16 | integer16List | integer32 | integer32List | integer8 | integer8List | ipv4Address | ipv4AddressList | ipv4Prefix | ipv6Address | ipv6AddressList | ipv6Prefix | string | zeroLength): Option value type.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Type"])

    @Type.setter
    def Type(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Type"], value)

    @property
    def Value(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Option value represented as string.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Code=None, Name=None, Rfc=None, Type=None, Value=None):
        # type: (int, str, bool, str, str) -> FcoeClientOptionTlv
        """Updates fcoeClientOptionTlv resource on the server.

        Args
        ----
        - Code (number): Option code.
        - Name (str): Option name.
        - Rfc (bool): True if defined in RFC documents.
        - Type (str(boolean | domainName | hexadecimal | integer16 | integer16List | integer32 | integer32List | integer8 | integer8List | ipv4Address | ipv4AddressList | ipv4Prefix | ipv6Address | ipv6AddressList | ipv6Prefix | string | zeroLength)): Option value type.
        - Value (str): Option value represented as string.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Code=None, Name=None, Rfc=None, Type=None, Value=None):
        # type: (int, str, bool, str, str) -> FcoeClientOptionTlv
        """Adds a new fcoeClientOptionTlv resource on the server and adds it to the container.

        Args
        ----
        - Code (number): Option code.
        - Name (str): Option name.
        - Rfc (bool): True if defined in RFC documents.
        - Type (str(boolean | domainName | hexadecimal | integer16 | integer16List | integer32 | integer32List | integer8 | integer8List | ipv4Address | ipv4AddressList | ipv4Prefix | ipv6Address | ipv6AddressList | ipv6Prefix | string | zeroLength)): Option value type.
        - Value (str): Option value represented as string.

        Returns
        -------
        - self: This instance with all currently retrieved fcoeClientOptionTlv resources using find and the newly added fcoeClientOptionTlv resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained fcoeClientOptionTlv resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self, Code=None, Name=None, ObjectId=None, Rfc=None, Type=None, Value=None
    ):
        # type: (int, str, str, bool, str, str) -> FcoeClientOptionTlv
        """Finds and retrieves fcoeClientOptionTlv resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve fcoeClientOptionTlv resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all fcoeClientOptionTlv resources from the server.

        Args
        ----
        - Code (number): Option code.
        - Name (str): Option name.
        - ObjectId (str): Unique identifier for this object
        - Rfc (bool): True if defined in RFC documents.
        - Type (str(boolean | domainName | hexadecimal | integer16 | integer16List | integer32 | integer32List | integer8 | integer8List | ipv4Address | ipv4AddressList | ipv4Prefix | ipv6Address | ipv6AddressList | ipv6Prefix | string | zeroLength)): Option value type.
        - Value (str): Option value represented as string.

        Returns
        -------
        - self: This instance with matching fcoeClientOptionTlv resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of fcoeClientOptionTlv data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the fcoeClientOptionTlv resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
