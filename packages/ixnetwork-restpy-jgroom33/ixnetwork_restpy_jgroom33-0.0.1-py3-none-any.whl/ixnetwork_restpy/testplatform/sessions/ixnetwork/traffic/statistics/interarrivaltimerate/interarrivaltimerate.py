
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class InterArrivalTimeRate(Base):
    """This object sets the inter arrival time delay of each packet.
    The InterArrivalTimeRate class encapsulates a required interArrivalTimeRate resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "interArrivalTimeRate"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(InterArrivalTimeRate, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If enabled, fetches inter-arrival time and rate statistics.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, Enabled=None):
        # type: (bool) -> InterArrivalTimeRate
        """Updates interArrivalTimeRate resource on the server.

        Args
        ----
        - Enabled (bool): If enabled, fetches inter-arrival time and rate statistics.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Enabled=None):
        # type: (bool) -> InterArrivalTimeRate
        """Finds and retrieves interArrivalTimeRate resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve interArrivalTimeRate resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all interArrivalTimeRate resources from the server.

        Args
        ----
        - Enabled (bool): If enabled, fetches inter-arrival time and rate statistics.

        Returns
        -------
        - self: This instance with matching interArrivalTimeRate resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of interArrivalTimeRate data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the interArrivalTimeRate resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
