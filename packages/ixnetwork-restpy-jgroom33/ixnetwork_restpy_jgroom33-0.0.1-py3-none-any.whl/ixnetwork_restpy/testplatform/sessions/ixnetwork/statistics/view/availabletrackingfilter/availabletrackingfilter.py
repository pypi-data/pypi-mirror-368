
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class AvailableTrackingFilter(Base):
    """List of tracking available for filtering.
    The AvailableTrackingFilter class encapsulates a list of availableTrackingFilter resources that are managed by the system.
    A list of resources can be retrieved from the server using the AvailableTrackingFilter.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "availableTrackingFilter"
    _SDM_ATT_MAP = {
        "Constraints": "constraints",
        "Name": "name",
        "TrackingType": "trackingType",
        "ValueType": "valueType",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(AvailableTrackingFilter, self).__init__(parent, list_op)

    @property
    def Constraints(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str): Lists down the constraints associated with the available tracking filter list.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Constraints"])

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Displays the name of the tracking filter.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    @property
    def TrackingType(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Indicates the tracking type.
        """
        return self._get_attribute(self._SDM_ATT_MAP["TrackingType"])

    @property
    def ValueType(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Value of tracking to be matched based on operator.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ValueType"])

    def add(self):
        """Adds a new availableTrackingFilter resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved availableTrackingFilter resources using find and the newly added availableTrackingFilter resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Constraints=None, Name=None, TrackingType=None, ValueType=None):
        # type: (List[str], str, str, str) -> AvailableTrackingFilter
        """Finds and retrieves availableTrackingFilter resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve availableTrackingFilter resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all availableTrackingFilter resources from the server.

        Args
        ----
        - Constraints (list(str)): Lists down the constraints associated with the available tracking filter list.
        - Name (str): Displays the name of the tracking filter.
        - TrackingType (str): Indicates the tracking type.
        - ValueType (str): Value of tracking to be matched based on operator.

        Returns
        -------
        - self: This instance with matching availableTrackingFilter resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of availableTrackingFilter data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the availableTrackingFilter resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
