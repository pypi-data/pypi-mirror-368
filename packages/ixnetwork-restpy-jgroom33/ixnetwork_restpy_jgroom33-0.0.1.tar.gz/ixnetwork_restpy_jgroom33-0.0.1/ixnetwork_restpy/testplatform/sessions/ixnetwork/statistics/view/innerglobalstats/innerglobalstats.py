
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class InnerGlobalStats(Base):
    """NOT DEFINED
    The InnerGlobalStats class encapsulates a required innerGlobalStats resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "innerGlobalStats"
    _SDM_ATT_MAP = {
        "ColumnCaptions": "columnCaptions",
        "RowValues": "rowValues",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(InnerGlobalStats, self).__init__(parent, list_op)

    @property
    def ColumnCaptions(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str): The statistics column caption.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ColumnCaptions"])

    @property
    def RowValues(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str): All statistics values in a row.
        """
        return self._get_attribute(self._SDM_ATT_MAP["RowValues"])

    def find(self, ColumnCaptions=None, RowValues=None):
        # type: (List[str], List[str]) -> InnerGlobalStats
        """Finds and retrieves innerGlobalStats resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve innerGlobalStats resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all innerGlobalStats resources from the server.

        Args
        ----
        - ColumnCaptions (list(str)): The statistics column caption.
        - RowValues (list(str)): All statistics values in a row.

        Returns
        -------
        - self: This instance with matching innerGlobalStats resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of innerGlobalStats data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the innerGlobalStats resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
