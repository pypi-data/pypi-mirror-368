
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FieldOffset(Base):
    """Specifies the offset position of the selected field.
    The FieldOffset class encapsulates a required fieldOffset resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "fieldOffset"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(FieldOffset, self).__init__(parent, list_op)

    @property
    def Stack(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.traffic.trafficitem.tracking.egress.fieldoffset.stack.stack.Stack): An instance of the Stack class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.traffic.trafficitem.tracking.egress.fieldoffset.stack.stack import (
            Stack,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Stack", None) is not None:
                return self._properties.get("Stack")
        return Stack(self)

    def find(self):
        """Finds and retrieves fieldOffset resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve fieldOffset resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all fieldOffset resources from the server.

        Returns
        -------
        - self: This instance with matching fieldOffset resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of fieldOffset data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the fieldOffset resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
