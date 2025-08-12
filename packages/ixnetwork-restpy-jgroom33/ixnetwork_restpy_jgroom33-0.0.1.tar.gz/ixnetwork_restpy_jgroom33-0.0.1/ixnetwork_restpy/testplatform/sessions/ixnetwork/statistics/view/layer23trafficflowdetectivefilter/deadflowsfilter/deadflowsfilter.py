
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class DeadFlowsFilter(Base):
    """Dead flows filter specification.
    The DeadFlowsFilter class encapsulates a list of deadFlowsFilter resources that are managed by the user.
    A list of resources can be retrieved from the server using the DeadFlowsFilter.find() method.
    The list can be managed by using the DeadFlowsFilter.add() and DeadFlowsFilter.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "deadFlowsFilter"
    _SDM_ATT_MAP = {
        "NumberOfResults": "numberOfResults",
        "SortingCondition": "sortingCondition",
    }
    _SDM_ENUM_MAP = {
        "sortingCondition": ["ascending", "descending"],
    }

    def __init__(self, parent, list_op=False):
        super(DeadFlowsFilter, self).__init__(parent, list_op)

    @property
    def NumberOfResults(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Number of traffic flows to be displayed.
        """
        return self._get_attribute(self._SDM_ATT_MAP["NumberOfResults"])

    @NumberOfResults.setter
    def NumberOfResults(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["NumberOfResults"], value)

    @property
    def SortingCondition(self):
        # type: () -> str
        """
        Returns
        -------
        - str(ascending | descending): Sets the display order of the view.
        """
        return self._get_attribute(self._SDM_ATT_MAP["SortingCondition"])

    @SortingCondition.setter
    def SortingCondition(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["SortingCondition"], value)

    def update(self, NumberOfResults=None, SortingCondition=None):
        # type: (int, str) -> DeadFlowsFilter
        """Updates deadFlowsFilter resource on the server.

        Args
        ----
        - NumberOfResults (number): Number of traffic flows to be displayed.
        - SortingCondition (str(ascending | descending)): Sets the display order of the view.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, NumberOfResults=None, SortingCondition=None):
        # type: (int, str) -> DeadFlowsFilter
        """Adds a new deadFlowsFilter resource on the server and adds it to the container.

        Args
        ----
        - NumberOfResults (number): Number of traffic flows to be displayed.
        - SortingCondition (str(ascending | descending)): Sets the display order of the view.

        Returns
        -------
        - self: This instance with all currently retrieved deadFlowsFilter resources using find and the newly added deadFlowsFilter resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained deadFlowsFilter resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, NumberOfResults=None, SortingCondition=None):
        # type: (int, str) -> DeadFlowsFilter
        """Finds and retrieves deadFlowsFilter resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve deadFlowsFilter resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all deadFlowsFilter resources from the server.

        Args
        ----
        - NumberOfResults (number): Number of traffic flows to be displayed.
        - SortingCondition (str(ascending | descending)): Sets the display order of the view.

        Returns
        -------
        - self: This instance with matching deadFlowsFilter resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of deadFlowsFilter data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the deadFlowsFilter resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
