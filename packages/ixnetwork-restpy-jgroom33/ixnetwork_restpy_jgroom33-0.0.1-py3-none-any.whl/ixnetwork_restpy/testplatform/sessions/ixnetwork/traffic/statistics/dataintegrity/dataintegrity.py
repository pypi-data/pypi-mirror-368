
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class DataIntegrity(Base):
    """Fetches the data integrity statistics.
    The DataIntegrity class encapsulates a required dataIntegrity resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "dataIntegrity"
    _SDM_ATT_MAP = {
        "DataIntegrityVirtualPorts": "dataIntegrityVirtualPorts",
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(DataIntegrity, self).__init__(parent, list_op)

    @property
    def DataIntegrityVirtualPorts(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, enables and fetches data integrity statistics on Virtual Ports
        """
        return self._get_attribute(self._SDM_ATT_MAP["DataIntegrityVirtualPorts"])

    @DataIntegrityVirtualPorts.setter
    def DataIntegrityVirtualPorts(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["DataIntegrityVirtualPorts"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, enables and fetches data integrity statistics
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, DataIntegrityVirtualPorts=None, Enabled=None):
        # type: (bool, bool) -> DataIntegrity
        """Updates dataIntegrity resource on the server.

        Args
        ----
        - DataIntegrityVirtualPorts (bool): If true, enables and fetches data integrity statistics on Virtual Ports
        - Enabled (bool): If true, enables and fetches data integrity statistics

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, DataIntegrityVirtualPorts=None, Enabled=None):
        # type: (bool, bool) -> DataIntegrity
        """Finds and retrieves dataIntegrity resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve dataIntegrity resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all dataIntegrity resources from the server.

        Args
        ----
        - DataIntegrityVirtualPorts (bool): If true, enables and fetches data integrity statistics on Virtual Ports
        - Enabled (bool): If true, enables and fetches data integrity statistics

        Returns
        -------
        - self: This instance with matching dataIntegrity resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of dataIntegrity data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the dataIntegrity resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
