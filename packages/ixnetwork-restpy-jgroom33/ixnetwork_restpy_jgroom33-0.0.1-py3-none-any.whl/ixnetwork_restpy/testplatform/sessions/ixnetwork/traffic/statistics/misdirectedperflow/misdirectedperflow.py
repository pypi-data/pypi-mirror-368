
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class MisdirectedPerFlow(Base):
    """Display misdirected statistics on a per-flow basis. When active this replaces port level misdirected statistics
    The MisdirectedPerFlow class encapsulates a required misdirectedPerFlow resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "misdirectedPerFlow"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(MisdirectedPerFlow, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true then misdirected per flow statistics will be enabled
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, Enabled=None):
        # type: (bool) -> MisdirectedPerFlow
        """Updates misdirectedPerFlow resource on the server.

        Args
        ----
        - Enabled (bool): If true then misdirected per flow statistics will be enabled

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None):
        # type: (bool) -> MisdirectedPerFlow
        """Finds and retrieves misdirectedPerFlow resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve misdirectedPerFlow resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all misdirectedPerFlow resources from the server.

        Args
        ----
        - Enabled (bool): If true then misdirected per flow statistics will be enabled

        Returns
        -------
        - self: This instance with matching misdirectedPerFlow resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of misdirectedPerFlow data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the misdirectedPerFlow resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
