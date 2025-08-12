
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class ErroredFramePeriodTlv(Base):
    """
    The ErroredFramePeriodTlv class encapsulates a required erroredFramePeriodTlv resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "erroredFramePeriodTlv"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "Frames": "frames",
        "Threshold": "threshold",
        "Window": "window",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(ErroredFramePeriodTlv, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def Frames(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Frames"])

    @Frames.setter
    def Frames(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Frames"], value)

    @property
    def Threshold(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Threshold"])

    @Threshold.setter
    def Threshold(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Threshold"], value)

    @property
    def Window(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Window"])

    @Window.setter
    def Window(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Window"], value)

    def update(self, Enabled=None, Frames=None, Threshold=None, Window=None):
        # type: (bool, int, int, int) -> ErroredFramePeriodTlv
        """Updates erroredFramePeriodTlv resource on the server.

        Args
        ----
        - Enabled (bool):
        - Frames (number):
        - Threshold (number):
        - Window (number):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None, Frames=None, Threshold=None, Window=None):
        # type: (bool, int, int, int) -> ErroredFramePeriodTlv
        """Finds and retrieves erroredFramePeriodTlv resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve erroredFramePeriodTlv resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all erroredFramePeriodTlv resources from the server.

        Args
        ----
        - Enabled (bool):
        - Frames (number):
        - Threshold (number):
        - Window (number):

        Returns
        -------
        - self: This instance with matching erroredFramePeriodTlv resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of erroredFramePeriodTlv data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the erroredFramePeriodTlv resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
