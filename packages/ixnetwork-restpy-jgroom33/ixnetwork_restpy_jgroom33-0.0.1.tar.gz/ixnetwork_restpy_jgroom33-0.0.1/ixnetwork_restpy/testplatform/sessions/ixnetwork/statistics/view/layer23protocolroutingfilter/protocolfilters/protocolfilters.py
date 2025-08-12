
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class ProtocolFilters(Base):
    """Contains list of all the protocols available which can be enabled for the custom view.
    The ProtocolFilters class encapsulates a list of protocolFilters resources that are managed by the system.
    A list of resources can be retrieved from the server using the ProtocolFilters.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "protocolFilters"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "Name": "name",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(ProtocolFilters, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Value determining whether the filter is selected or not
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Protocol Filter Name.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    def update(self, Enabled=None):
        # type: (bool) -> ProtocolFilters
        """Updates protocolFilters resource on the server.

        Args
        ----
        - Enabled (bool): Value determining whether the filter is selected or not

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Enabled=None):
        # type: (bool) -> ProtocolFilters
        """Adds a new protocolFilters resource on the json, only valid with batch add utility

        Args
        ----
        - Enabled (bool): Value determining whether the filter is selected or not

        Returns
        -------
        - self: This instance with all currently retrieved protocolFilters resources using find and the newly added protocolFilters resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None, Name=None):
        # type: (bool, str) -> ProtocolFilters
        """Finds and retrieves protocolFilters resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve protocolFilters resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all protocolFilters resources from the server.

        Args
        ----
        - Enabled (bool): Value determining whether the filter is selected or not
        - Name (str): Protocol Filter Name.

        Returns
        -------
        - self: This instance with matching protocolFilters resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of protocolFilters data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the protocolFilters resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
