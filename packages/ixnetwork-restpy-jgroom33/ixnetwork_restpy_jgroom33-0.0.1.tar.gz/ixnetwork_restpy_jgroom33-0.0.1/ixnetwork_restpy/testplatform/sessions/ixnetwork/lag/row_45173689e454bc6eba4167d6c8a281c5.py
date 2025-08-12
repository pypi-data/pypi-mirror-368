
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Row(Base):
    """A row view of learned information.
    The Row class encapsulates a list of row resources that are managed by the system.
    A list of resources can be retrieved from the server using the Row.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "row"
    _SDM_ATT_MAP = {
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Row, self).__init__(parent, list_op)

    @property
    def Value(self):
        # type: () -> str
        """
        Returns
        -------
        - str: A learned information value
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    def add(self):
        """Adds a new row resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved row resources using find and the newly added row resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Value=None):
        # type: (str) -> Row
        """Finds and retrieves row resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve row resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all row resources from the server.

        Args
        ----
        - Value (str): A learned information value

        Returns
        -------
        - self: This instance with matching row resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of row data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the row resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
