
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class AsSegment(Base):
    """This object controls the contruction of AS path segments.
    The AsSegment class encapsulates a required asSegment resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "asSegment"
    _SDM_ATT_MAP = {
        "AsSegments": "asSegments",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(AsSegment, self).__init__(parent, list_op)

    @property
    def AsSegments(self):
        """
        Returns
        -------
        - list(dict(arg1:bool,arg2:str[asSet | asSequence | asConfedSet | unknown | asConfedSequence],arg3:list[number])): Used to construct AS list related items.
        """
        return self._get_attribute(self._SDM_ATT_MAP["AsSegments"])

    @AsSegments.setter
    def AsSegments(self, value):
        self._set_attribute(self._SDM_ATT_MAP["AsSegments"], value)

    def update(self, AsSegments=None):
        """Updates asSegment resource on the server.

        Args
        ----
        - AsSegments (list(dict(arg1:bool,arg2:str[asSet | asSequence | asConfedSet | unknown | asConfedSequence],arg3:list[number]))): Used to construct AS list related items.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, AsSegments=None):
        """Finds and retrieves asSegment resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve asSegment resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all asSegment resources from the server.

        Args
        ----
        - AsSegments (list(dict(arg1:bool,arg2:str[asSet | asSequence | asConfedSet | unknown | asConfedSequence],arg3:list[number]))): Used to construct AS list related items.

        Returns
        -------
        - self: This instance with matching asSegment resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of asSegment data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the asSegment resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
