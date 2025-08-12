
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FramePayload(Base):
    """This object provides different options for the Frame Payload.
    The FramePayload class encapsulates a required framePayload resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "framePayload"
    _SDM_ATT_MAP = {
        "CustomPattern": "customPattern",
        "CustomRepeat": "customRepeat",
        "Type": "type",
    }
    _SDM_ENUM_MAP = {
        "type": [
            "CJPAT",
            "CRPAT",
            "custom",
            "decrementByte",
            "decrementWord",
            "incrementByte",
            "incrementWord",
            "random",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(FramePayload, self).__init__(parent, list_op)

    @property
    def CustomPattern(self):
        # type: () -> str
        """
        Returns
        -------
        - str: If Frame Payload type is Custom, then this attribute specifies a string in hex format.
        """
        return self._get_attribute(self._SDM_ATT_MAP["CustomPattern"])

    @CustomPattern.setter
    def CustomPattern(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["CustomPattern"], value)

    @property
    def CustomRepeat(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: f true, Custom Pattern is repeated.
        """
        return self._get_attribute(self._SDM_ATT_MAP["CustomRepeat"])

    @CustomRepeat.setter
    def CustomRepeat(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["CustomRepeat"], value)

    @property
    def Type(self):
        # type: () -> str
        """
        Returns
        -------
        - str(CJPAT | CRPAT | custom | decrementByte | decrementWord | incrementByte | incrementWord | random): The types of Frame Payload.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Type"])

    @Type.setter
    def Type(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Type"], value)

    def update(self, CustomPattern=None, CustomRepeat=None, Type=None):
        # type: (str, bool, str) -> FramePayload
        """Updates framePayload resource on the server.

        Args
        ----
        - CustomPattern (str): If Frame Payload type is Custom, then this attribute specifies a string in hex format.
        - CustomRepeat (bool): f true, Custom Pattern is repeated.
        - Type (str(CJPAT | CRPAT | custom | decrementByte | decrementWord | incrementByte | incrementWord | random)): The types of Frame Payload.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, CustomPattern=None, CustomRepeat=None, Type=None):
        # type: (str, bool, str) -> FramePayload
        """Finds and retrieves framePayload resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve framePayload resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all framePayload resources from the server.

        Args
        ----
        - CustomPattern (str): If Frame Payload type is Custom, then this attribute specifies a string in hex format.
        - CustomRepeat (bool): f true, Custom Pattern is repeated.
        - Type (str(CJPAT | CRPAT | custom | decrementByte | decrementWord | incrementByte | incrementWord | random)): The types of Frame Payload.

        Returns
        -------
        - self: This instance with matching framePayload resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of framePayload data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the framePayload resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
