
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class NextTable(Base):
    """NOT DEFINED
    The NextTable class encapsulates a required nextTable resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "nextTable"
    _SDM_ATT_MAP = {
        "TableId": "tableId",
        "TableIdMiss": "tableIdMiss",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(NextTable, self).__init__(parent, list_op)

    @property
    def TableId(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["TableId"])

    @TableId.setter
    def TableId(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["TableId"], value)

    @property
    def TableIdMiss(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["TableIdMiss"])

    @TableIdMiss.setter
    def TableIdMiss(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["TableIdMiss"], value)

    def update(self, TableId=None, TableIdMiss=None):
        # type: (str, str) -> NextTable
        """Updates nextTable resource on the server.

        Args
        ----
        - TableId (str): NOT DEFINED
        - TableIdMiss (str): NOT DEFINED

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, TableId=None, TableIdMiss=None):
        # type: (str, str) -> NextTable
        """Finds and retrieves nextTable resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve nextTable resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all nextTable resources from the server.

        Args
        ----
        - TableId (str): NOT DEFINED
        - TableIdMiss (str): NOT DEFINED

        Returns
        -------
        - self: This instance with matching nextTable resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of nextTable data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the nextTable resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
