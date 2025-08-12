
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class CustomGraph(Base):
    """This node contains Custom Graph Settings.
    The CustomGraph class encapsulates a required customGraph resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "customGraph"
    _SDM_ATT_MAP = {
        "MaxNumberOfStatsPerCustomGraph": "maxNumberOfStatsPerCustomGraph",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(CustomGraph, self).__init__(parent, list_op)

    @property
    def MaxNumberOfStatsPerCustomGraph(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The maximum number of stats a custom graph can have. The range is 1 - 256.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaxNumberOfStatsPerCustomGraph"])

    @MaxNumberOfStatsPerCustomGraph.setter
    def MaxNumberOfStatsPerCustomGraph(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MaxNumberOfStatsPerCustomGraph"], value)

    def update(self, MaxNumberOfStatsPerCustomGraph=None):
        # type: (int) -> CustomGraph
        """Updates customGraph resource on the server.

        Args
        ----
        - MaxNumberOfStatsPerCustomGraph (number): The maximum number of stats a custom graph can have. The range is 1 - 256.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, MaxNumberOfStatsPerCustomGraph=None):
        # type: (int) -> CustomGraph
        """Finds and retrieves customGraph resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve customGraph resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all customGraph resources from the server.

        Args
        ----
        - MaxNumberOfStatsPerCustomGraph (number): The maximum number of stats a custom graph can have. The range is 1 - 256.

        Returns
        -------
        - self: This instance with matching customGraph resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of customGraph data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the customGraph resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
