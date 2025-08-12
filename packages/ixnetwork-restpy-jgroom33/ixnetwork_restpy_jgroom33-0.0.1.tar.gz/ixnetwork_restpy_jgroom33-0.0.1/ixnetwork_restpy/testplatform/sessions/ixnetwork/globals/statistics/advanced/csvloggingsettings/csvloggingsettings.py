
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class CsvLoggingSettings(Base):
    """This node contains CSV Logging Settings.
    The CsvLoggingSettings class encapsulates a required csvLoggingSettings resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "csvLoggingSettings"
    _SDM_ATT_MAP = {
        "CsvLogPollingIntervalMultiplier": "csvLogPollingIntervalMultiplier",
        "CsvLoggingPath": "csvLoggingPath",
        "EnableCSVLoggingForAllViews": "enableCSVLoggingForAllViews",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(CsvLoggingSettings, self).__init__(parent, list_op)

    @property
    def CsvLogPollingIntervalMultiplier(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Used to specify the time interval between log polling events.
        """
        return self._get_attribute(self._SDM_ATT_MAP["CsvLogPollingIntervalMultiplier"])

    @CsvLogPollingIntervalMultiplier.setter
    def CsvLogPollingIntervalMultiplier(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["CsvLogPollingIntervalMultiplier"], value)

    @property
    def CsvLoggingPath(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Returns the CSV Logging path.
        """
        return self._get_attribute(self._SDM_ATT_MAP["CsvLoggingPath"])

    @property
    def EnableCSVLoggingForAllViews(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: When set, the CSV Logging for all views is enabled
        """
        return self._get_attribute(self._SDM_ATT_MAP["EnableCSVLoggingForAllViews"])

    @EnableCSVLoggingForAllViews.setter
    def EnableCSVLoggingForAllViews(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["EnableCSVLoggingForAllViews"], value)

    def update(
        self, CsvLogPollingIntervalMultiplier=None, EnableCSVLoggingForAllViews=None
    ):
        # type: (int, bool) -> CsvLoggingSettings
        """Updates csvLoggingSettings resource on the server.

        Args
        ----
        - CsvLogPollingIntervalMultiplier (number): Used to specify the time interval between log polling events.
        - EnableCSVLoggingForAllViews (bool): When set, the CSV Logging for all views is enabled

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        CsvLogPollingIntervalMultiplier=None,
        CsvLoggingPath=None,
        EnableCSVLoggingForAllViews=None,
    ):
        # type: (int, str, bool) -> CsvLoggingSettings
        """Finds and retrieves csvLoggingSettings resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve csvLoggingSettings resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all csvLoggingSettings resources from the server.

        Args
        ----
        - CsvLogPollingIntervalMultiplier (number): Used to specify the time interval between log polling events.
        - CsvLoggingPath (str): Returns the CSV Logging path.
        - EnableCSVLoggingForAllViews (bool): When set, the CSV Logging for all views is enabled

        Returns
        -------
        - self: This instance with matching csvLoggingSettings resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of csvLoggingSettings data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the csvLoggingSettings resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
