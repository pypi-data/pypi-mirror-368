
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class TableUdf(Base):
    """This object specifies the UDF table properties.
    The TableUdf class encapsulates a list of tableUdf resources that are managed by the system.
    A list of resources can be retrieved from the server using the TableUdf.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "tableUdf"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(TableUdf, self).__init__(parent, list_op)

    @property
    def Column(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.traffic.trafficitem.highlevelstream.tableudf.column.column.Column): An instance of the Column class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.traffic.trafficitem.highlevelstream.tableudf.column.column import (
            Column,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Column", None) is not None:
                return self._properties.get("Column")
        return Column(self)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If enabled, enables the UDF table for this flow group if it is supported.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, Enabled=None):
        # type: (bool) -> TableUdf
        """Updates tableUdf resource on the server.

        Args
        ----
        - Enabled (bool): If enabled, enables the UDF table for this flow group if it is supported.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Enabled=None):
        # type: (bool) -> TableUdf
        """Adds a new tableUdf resource on the json, only valid with batch add utility

        Args
        ----
        - Enabled (bool): If enabled, enables the UDF table for this flow group if it is supported.

        Returns
        -------
        - self: This instance with all currently retrieved tableUdf resources using find and the newly added tableUdf resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None):
        # type: (bool) -> TableUdf
        """Finds and retrieves tableUdf resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve tableUdf resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all tableUdf resources from the server.

        Args
        ----
        - Enabled (bool): If enabled, enables the UDF table for this flow group if it is supported.

        Returns
        -------
        - self: This instance with matching tableUdf resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of tableUdf data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the tableUdf resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
