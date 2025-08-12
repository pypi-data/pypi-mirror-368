
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Type(Base):
    """Tlv type container
    The Type class encapsulates a required type resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "type"
    _SDM_ATT_MAP = {
        "IsEditable": "isEditable",
        "IsRequired": "isRequired",
        "Name": "name",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Type, self).__init__(parent, list_op)

    @property
    def Object(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.tlveditor.object_12e587bd6e412f6d3d8361017e8dcba9.Object): An instance of the Object class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.tlveditor.object_12e587bd6e412f6d3d8361017e8dcba9 import (
            Object,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Object", None) is not None:
                return self._properties.get("Object")
        return Object(self)

    @property
    def IsEditable(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates whether this is editable or not
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsEditable"])

    @IsEditable.setter
    def IsEditable(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsEditable"], value)

    @property
    def IsRequired(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates whether this is required or not
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsRequired"])

    @IsRequired.setter
    def IsRequired(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsRequired"], value)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Name of the node
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    @Name.setter
    def Name(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Name"], value)

    def update(self, IsEditable=None, IsRequired=None, Name=None):
        # type: (bool, bool, str) -> Type
        """Updates type resource on the server.

        Args
        ----
        - IsEditable (bool): Indicates whether this is editable or not
        - IsRequired (bool): Indicates whether this is required or not
        - Name (str): Name of the node

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, IsEditable=None, IsRequired=None, Name=None):
        # type: (bool, bool, str) -> Type
        """Finds and retrieves type resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve type resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all type resources from the server.

        Args
        ----
        - IsEditable (bool): Indicates whether this is editable or not
        - IsRequired (bool): Indicates whether this is required or not
        - Name (str): Name of the node

        Returns
        -------
        - self: This instance with matching type resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of type data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the type resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
