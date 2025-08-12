
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Cluster(Base):
    """The list of BGP clusters that a particular route has passed through.
    The Cluster class encapsulates a required cluster resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "cluster"
    _SDM_ATT_MAP = {
        "Val": "val",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Cluster, self).__init__(parent, list_op)

    @property
    def Val(self):
        # type: () -> List[int]
        """
        Returns
        -------
        - list(number): The value of the cluster list.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Val"])

    @Val.setter
    def Val(self, value):
        # type: (List[int]) -> None
        self._set_attribute(self._SDM_ATT_MAP["Val"], value)

    def update(self, Val=None):
        # type: (List[int]) -> Cluster
        """Updates cluster resource on the server.

        Args
        ----
        - Val (list(number)): The value of the cluster list.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Val=None):
        # type: (List[int]) -> Cluster
        """Finds and retrieves cluster resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve cluster resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all cluster resources from the server.

        Args
        ----
        - Val (list(number)): The value of the cluster list.

        Returns
        -------
        - self: This instance with matching cluster resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of cluster data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the cluster resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
