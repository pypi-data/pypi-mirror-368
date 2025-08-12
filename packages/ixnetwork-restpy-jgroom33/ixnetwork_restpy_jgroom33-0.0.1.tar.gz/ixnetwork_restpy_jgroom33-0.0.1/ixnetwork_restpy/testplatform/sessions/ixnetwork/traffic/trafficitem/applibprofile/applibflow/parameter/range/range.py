
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Range(Base):
    """This specifies the range parameter of the properties.
    The Range class encapsulates a list of range resources that are managed by the system.
    A list of resources can be retrieved from the server using the Range.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "range"
    _SDM_ATT_MAP = {
        "From": "from",
        "MaxValue": "maxValue",
        "MinValue": "minValue",
        "To": "to",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Range, self).__init__(parent, list_op)

    @property
    def From(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Start range value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["From"])

    @From.setter
    def From(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["From"], value)

    @property
    def MaxValue(self):
        # type: () -> int
        """
        Returns
        -------
        - number: (Read only) Maximum supported value for parameter range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaxValue"])

    @property
    def MinValue(self):
        # type: () -> int
        """
        Returns
        -------
        - number: (Read only) Minimum supported value for parameter range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MinValue"])

    @property
    def To(self):
        # type: () -> int
        """
        Returns
        -------
        - number: End range value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["To"])

    @To.setter
    def To(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["To"], value)

    def update(self, From=None, To=None):
        # type: (int, int) -> Range
        """Updates range resource on the server.

        Args
        ----
        - From (number): Start range value.
        - To (number): End range value.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, From=None, To=None):
        # type: (int, int) -> Range
        """Adds a new range resource on the json, only valid with batch add utility

        Args
        ----
        - From (number): Start range value.
        - To (number): End range value.

        Returns
        -------
        - self: This instance with all currently retrieved range resources using find and the newly added range resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, From=None, MaxValue=None, MinValue=None, To=None):
        # type: (int, int, int, int) -> Range
        """Finds and retrieves range resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve range resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all range resources from the server.

        Args
        ----
        - From (number): Start range value.
        - MaxValue (number): (Read only) Maximum supported value for parameter range.
        - MinValue (number): (Read only) Minimum supported value for parameter range.
        - To (number): End range value.

        Returns
        -------
        - self: This instance with matching range resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of range data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the range resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
