
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class CustomValue(Base):
    """List of custom values.
    The CustomValue class encapsulates a list of customValue resources that are managed by the user.
    A list of resources can be retrieved from the server using the CustomValue.find() method.
    The list can be managed by using the CustomValue.add() and CustomValue.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "customValue"
    _SDM_ATT_MAP = {
        "Percentage": "percentage",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(CustomValue, self).__init__(parent, list_op)

    @property
    def Percentage(self):
        # type: () -> int
        """
        Returns
        -------
        - number: How often this value occurs, as a percentage.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Percentage"])

    @Percentage.setter
    def Percentage(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Percentage"], value)

    @property
    def Value(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Delay value, in microseconds.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Percentage=None, Value=None):
        # type: (int, int) -> CustomValue
        """Updates customValue resource on the server.

        Args
        ----
        - Percentage (number): How often this value occurs, as a percentage.
        - Value (number): Delay value, in microseconds.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Percentage=None, Value=None):
        # type: (int, int) -> CustomValue
        """Adds a new customValue resource on the server and adds it to the container.

        Args
        ----
        - Percentage (number): How often this value occurs, as a percentage.
        - Value (number): Delay value, in microseconds.

        Returns
        -------
        - self: This instance with all currently retrieved customValue resources using find and the newly added customValue resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained customValue resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Percentage=None, Value=None):
        # type: (int, int) -> CustomValue
        """Finds and retrieves customValue resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve customValue resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all customValue resources from the server.

        Args
        ----
        - Percentage (number): How often this value occurs, as a percentage.
        - Value (number): Delay value, in microseconds.

        Returns
        -------
        - self: This instance with matching customValue resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of customValue data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the customValue resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
