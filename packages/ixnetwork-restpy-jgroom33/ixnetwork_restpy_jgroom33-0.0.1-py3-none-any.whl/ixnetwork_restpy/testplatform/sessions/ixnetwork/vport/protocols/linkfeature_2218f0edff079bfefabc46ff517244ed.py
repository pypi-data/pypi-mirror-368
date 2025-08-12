
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class LinkFeature(Base):
    """NOT DEFINED
    The LinkFeature class encapsulates a required linkFeature resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "linkFeature"
    _SDM_ATT_MAP = {
        "OfppfAutoNegotiation": "ofppfAutoNegotiation",
        "OfppfPause": "ofppfPause",
        "OfppfPauseAsym": "ofppfPauseAsym",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(LinkFeature, self).__init__(parent, list_op)

    @property
    def OfppfAutoNegotiation(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["OfppfAutoNegotiation"])

    @OfppfAutoNegotiation.setter
    def OfppfAutoNegotiation(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["OfppfAutoNegotiation"], value)

    @property
    def OfppfPause(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["OfppfPause"])

    @OfppfPause.setter
    def OfppfPause(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["OfppfPause"], value)

    @property
    def OfppfPauseAsym(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["OfppfPauseAsym"])

    @OfppfPauseAsym.setter
    def OfppfPauseAsym(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["OfppfPauseAsym"], value)

    def update(self, OfppfAutoNegotiation=None, OfppfPause=None, OfppfPauseAsym=None):
        # type: (bool, bool, bool) -> LinkFeature
        """Updates linkFeature resource on the server.

        Args
        ----
        - OfppfAutoNegotiation (bool): NOT DEFINED
        - OfppfPause (bool): NOT DEFINED
        - OfppfPauseAsym (bool): NOT DEFINED

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, OfppfAutoNegotiation=None, OfppfPause=None, OfppfPauseAsym=None):
        # type: (bool, bool, bool) -> LinkFeature
        """Finds and retrieves linkFeature resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve linkFeature resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all linkFeature resources from the server.

        Args
        ----
        - OfppfAutoNegotiation (bool): NOT DEFINED
        - OfppfPause (bool): NOT DEFINED
        - OfppfPauseAsym (bool): NOT DEFINED

        Returns
        -------
        - self: This instance with matching linkFeature resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of linkFeature data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the linkFeature resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
