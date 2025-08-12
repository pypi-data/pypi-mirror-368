
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FramePreemption(Base):
    """
    The FramePreemption class encapsulates a required framePreemption resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "framePreemption"
    _SDM_ATT_MAP = {
        "IsFramePreemptionEnabled": "isFramePreemptionEnabled",
        "IsSmdVREnabled": "isSmdVREnabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(FramePreemption, self).__init__(parent, list_op)

    @property
    def IsFramePreemptionEnabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool:
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsFramePreemptionEnabled"])

    @IsFramePreemptionEnabled.setter
    def IsFramePreemptionEnabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsFramePreemptionEnabled"], value)

    @property
    def IsSmdVREnabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool:
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsSmdVREnabled"])

    @IsSmdVREnabled.setter
    def IsSmdVREnabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsSmdVREnabled"], value)

    def update(self, IsFramePreemptionEnabled=None, IsSmdVREnabled=None):
        # type: (bool, bool) -> FramePreemption
        """Updates framePreemption resource on the server.

        Args
        ----
        - IsFramePreemptionEnabled (bool):
        - IsSmdVREnabled (bool):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, IsFramePreemptionEnabled=None, IsSmdVREnabled=None):
        # type: (bool, bool) -> FramePreemption
        """Finds and retrieves framePreemption resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve framePreemption resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all framePreemption resources from the server.

        Args
        ----
        - IsFramePreemptionEnabled (bool):
        - IsSmdVREnabled (bool):

        Returns
        -------
        - self: This instance with matching framePreemption resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of framePreemption data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the framePreemption resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
