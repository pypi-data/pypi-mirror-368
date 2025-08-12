
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class CellTable(Base):
    """The node where learned information is grouped into tables or columns and rows.
    The CellTable class encapsulates a list of cellTable resources that are managed by the system.
    A list of resources can be retrieved from the server using the CellTable.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "cellTable"
    _SDM_ATT_MAP = {
        "Actions": "actions",
        "Columns": "columns",
        "Type": "type",
        "Values": "values",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(CellTable, self).__init__(parent, list_op)

    @property
    def Col(self):
        """DEPRECATED
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.lag.col_667991bd02f140c2b2287de796fe1846.Col): An instance of the Col class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.lag.col_667991bd02f140c2b2287de796fe1846 import (
            Col,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Col", None) is not None:
                return self._properties.get("Col")
        return Col(self)

    @property
    def Actions(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str): The list of actions allowed on the learned information table
        """
        return self._get_attribute(self._SDM_ATT_MAP["Actions"])

    @property
    def Columns(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str): The list of columns in the learned information table
        """
        return self._get_attribute(self._SDM_ATT_MAP["Columns"])

    @property
    def Type(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Description of the learned information type
        """
        return self._get_attribute(self._SDM_ATT_MAP["Type"])

    @property
    def Values(self):
        """
        Returns
        -------
        - list(list[str]): A list of rows of learned information values
        """
        return self._get_attribute(self._SDM_ATT_MAP["Values"])

    def add(self):
        """Adds a new cellTable resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved cellTable resources using find and the newly added cellTable resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Actions=None, Columns=None, Type=None, Values=None):
        """Finds and retrieves cellTable resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve cellTable resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all cellTable resources from the server.

        Args
        ----
        - Actions (list(str)): The list of actions allowed on the learned information table
        - Columns (list(str)): The list of columns in the learned information table
        - Type (str): Description of the learned information type
        - Values (list(list[str])): A list of rows of learned information values

        Returns
        -------
        - self: This instance with matching cellTable resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of cellTable data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the cellTable resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
