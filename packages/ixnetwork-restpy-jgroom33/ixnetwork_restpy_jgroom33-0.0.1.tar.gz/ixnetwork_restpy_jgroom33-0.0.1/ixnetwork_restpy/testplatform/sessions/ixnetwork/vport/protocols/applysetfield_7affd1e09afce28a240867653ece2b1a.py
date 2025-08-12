
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class ApplySetField(Base):
    """NOT DEFINED
    The ApplySetField class encapsulates a required applySetField resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "applySetField"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(ApplySetField, self).__init__(parent, list_op)

    @property
    def Fields(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.fields_82c6ee107b12ee013dcfe1404de190d2.Fields): An instance of the Fields class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.fields_82c6ee107b12ee013dcfe1404de190d2 import (
            Fields,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Fields", None) is not None:
                return self._properties.get("Fields")
        return Fields(self)._select()

    @property
    def MissFields(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.missfields_731e6a490626a72d2ce6360754e838fe.MissFields): An instance of the MissFields class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.missfields_731e6a490626a72d2ce6360754e838fe import (
            MissFields,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("MissFields", None) is not None:
                return self._properties.get("MissFields")
        return MissFields(self)._select()

    def find(self):
        """Finds and retrieves applySetField resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve applySetField resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all applySetField resources from the server.

        Returns
        -------
        - self: This instance with matching applySetField resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of applySetField data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the applySetField resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
