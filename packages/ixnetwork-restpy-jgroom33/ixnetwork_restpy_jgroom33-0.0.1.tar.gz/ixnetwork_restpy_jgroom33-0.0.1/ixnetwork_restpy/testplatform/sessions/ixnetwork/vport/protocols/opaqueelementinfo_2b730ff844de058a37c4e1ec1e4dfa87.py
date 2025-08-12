
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class OpaqueElementInfo(Base):
    """(Read Only) List of Opaque Elements.
    The OpaqueElementInfo class encapsulates a list of opaqueElementInfo resources that are managed by the system.
    A list of resources can be retrieved from the server using the OpaqueElementInfo.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "opaqueElementInfo"
    _SDM_ATT_MAP = {
        "Length": "length",
        "Type": "type",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(OpaqueElementInfo, self).__init__(parent, list_op)

    @property
    def Length(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Length of the opaque element.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Length"])

    @property
    def Type(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Type of the opaque element.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Type"])

    @property
    def Value(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Value of opaque element.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    def add(self):
        """Adds a new opaqueElementInfo resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved opaqueElementInfo resources using find and the newly added opaqueElementInfo resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Length=None, Type=None, Value=None):
        # type: (str, str, str) -> OpaqueElementInfo
        """Finds and retrieves opaqueElementInfo resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve opaqueElementInfo resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all opaqueElementInfo resources from the server.

        Args
        ----
        - Length (str): (Read Only) Length of the opaque element.
        - Type (str): (Read Only) Type of the opaque element.
        - Value (str): (Read Only) Value of opaque element.

        Returns
        -------
        - self: This instance with matching opaqueElementInfo resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of opaqueElementInfo data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the opaqueElementInfo resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
