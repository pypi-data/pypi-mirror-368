
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Prefix(Base):
    """Filters based on route prefix information.
    The Prefix class encapsulates a required prefix resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "prefix"
    _SDM_ATT_MAP = {
        "Prefix": "prefix",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Prefix, self).__init__(parent, list_op)

    @property
    def Prefix(self):
        """
        Returns
        -------
        - list(dict(arg1:str,arg2:bool,arg3:number,arg4:number)): Controls the prefix attributes that are filtered on.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Prefix"])

    @Prefix.setter
    def Prefix(self, value):
        self._set_attribute(self._SDM_ATT_MAP["Prefix"], value)

    def update(self, Prefix=None):
        """Updates prefix resource on the server.

        Args
        ----
        - Prefix (list(dict(arg1:str,arg2:bool,arg3:number,arg4:number))): Controls the prefix attributes that are filtered on.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Prefix=None):
        """Finds and retrieves prefix resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve prefix resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all prefix resources from the server.

        Args
        ----
        - Prefix (list(dict(arg1:str,arg2:bool,arg3:number,arg4:number))): Controls the prefix attributes that are filtered on.

        Returns
        -------
        - self: This instance with matching prefix resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of prefix data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the prefix resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
