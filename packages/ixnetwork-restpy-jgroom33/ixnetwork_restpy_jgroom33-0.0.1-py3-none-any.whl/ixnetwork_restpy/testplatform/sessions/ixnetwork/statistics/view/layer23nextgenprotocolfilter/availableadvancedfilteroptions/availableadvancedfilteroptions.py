
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class AvailableAdvancedFilterOptions(Base):
    """Provides a list of all the statistics and the filtering options for the current view.
    The AvailableAdvancedFilterOptions class encapsulates a list of availableAdvancedFilterOptions resources that are managed by the system.
    A list of resources can be retrieved from the server using the AvailableAdvancedFilterOptions.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "availableAdvancedFilterOptions"
    _SDM_ATT_MAP = {
        "Operators": "operators",
        "Stat": "stat",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(AvailableAdvancedFilterOptions, self).__init__(parent, list_op)

    @property
    def Operators(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Returns the operators list for a filter option.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Operators"])

    @property
    def Stat(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Returns the statistic name for a filter option.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Stat"])

    def add(self):
        """Adds a new availableAdvancedFilterOptions resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved availableAdvancedFilterOptions resources using find and the newly added availableAdvancedFilterOptions resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Operators=None, Stat=None):
        # type: (str, str) -> AvailableAdvancedFilterOptions
        """Finds and retrieves availableAdvancedFilterOptions resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve availableAdvancedFilterOptions resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all availableAdvancedFilterOptions resources from the server.

        Args
        ----
        - Operators (str): Returns the operators list for a filter option.
        - Stat (str): Returns the statistic name for a filter option.

        Returns
        -------
        - self: This instance with matching availableAdvancedFilterOptions resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of availableAdvancedFilterOptions data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the availableAdvancedFilterOptions resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
