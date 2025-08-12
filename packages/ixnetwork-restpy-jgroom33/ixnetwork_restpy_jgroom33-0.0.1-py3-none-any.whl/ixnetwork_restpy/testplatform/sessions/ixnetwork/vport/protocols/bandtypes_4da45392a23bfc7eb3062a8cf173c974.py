
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class BandTypes(Base):
    """Select the band types supported.
    The BandTypes class encapsulates a required bandTypes resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "bandTypes"
    _SDM_ATT_MAP = {
        "Drop": "drop",
        "DscpRemark": "dscpRemark",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(BandTypes, self).__init__(parent, list_op)

    @property
    def Drop(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: This indicates that packets which exceed the band rate value are dropped.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Drop"])

    @Drop.setter
    def Drop(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Drop"], value)

    @property
    def DscpRemark(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: This indicates that the drop precedence of the DSCP field is remarked in the IP header of the packets that exceed the band rate value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["DscpRemark"])

    @DscpRemark.setter
    def DscpRemark(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["DscpRemark"], value)

    def update(self, Drop=None, DscpRemark=None):
        # type: (bool, bool) -> BandTypes
        """Updates bandTypes resource on the server.

        Args
        ----
        - Drop (bool): This indicates that packets which exceed the band rate value are dropped.
        - DscpRemark (bool): This indicates that the drop precedence of the DSCP field is remarked in the IP header of the packets that exceed the band rate value.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Drop=None, DscpRemark=None):
        # type: (bool, bool) -> BandTypes
        """Finds and retrieves bandTypes resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve bandTypes resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all bandTypes resources from the server.

        Args
        ----
        - Drop (bool): This indicates that packets which exceed the band rate value are dropped.
        - DscpRemark (bool): This indicates that the drop precedence of the DSCP field is remarked in the IP header of the packets that exceed the band rate value.

        Returns
        -------
        - self: This instance with matching bandTypes resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of bandTypes data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the bandTypes resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
