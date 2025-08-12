
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class SourceRange(Base):
    """This object holds a list of source IPv4 addresses that multicast traffic should be included from or excluded from.
    The SourceRange class encapsulates a list of sourceRange resources that are managed by the user.
    A list of resources can be retrieved from the server using the SourceRange.find() method.
    The list can be managed by using the SourceRange.add() and SourceRange.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "sourceRange"
    _SDM_ATT_MAP = {
        "Count": "count",
        "IpFrom": "ipFrom",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(SourceRange, self).__init__(parent, list_op)

    @property
    def Count(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The number of IP addresses in the source range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Count"])

    @Count.setter
    def Count(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Count"], value)

    @property
    def IpFrom(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The first IP address in the source range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IpFrom"])

    @IpFrom.setter
    def IpFrom(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["IpFrom"], value)

    def update(self, Count=None, IpFrom=None):
        # type: (int, str) -> SourceRange
        """Updates sourceRange resource on the server.

        Args
        ----
        - Count (number): The number of IP addresses in the source range.
        - IpFrom (str): The first IP address in the source range.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Count=None, IpFrom=None):
        # type: (int, str) -> SourceRange
        """Adds a new sourceRange resource on the server and adds it to the container.

        Args
        ----
        - Count (number): The number of IP addresses in the source range.
        - IpFrom (str): The first IP address in the source range.

        Returns
        -------
        - self: This instance with all currently retrieved sourceRange resources using find and the newly added sourceRange resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained sourceRange resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Count=None, IpFrom=None):
        # type: (int, str) -> SourceRange
        """Finds and retrieves sourceRange resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve sourceRange resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all sourceRange resources from the server.

        Args
        ----
        - Count (number): The number of IP addresses in the source range.
        - IpFrom (str): The first IP address in the source range.

        Returns
        -------
        - self: This instance with matching sourceRange resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of sourceRange data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the sourceRange resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
