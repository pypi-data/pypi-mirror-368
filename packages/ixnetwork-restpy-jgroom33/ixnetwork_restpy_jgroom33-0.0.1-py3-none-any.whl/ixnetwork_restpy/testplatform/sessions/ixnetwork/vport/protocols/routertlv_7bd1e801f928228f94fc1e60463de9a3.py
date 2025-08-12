
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class RouterTlv(Base):
    """
    The RouterTlv class encapsulates a list of routerTlv resources that are managed by the system.
    A list of resources can be retrieved from the server using the RouterTlv.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "routerTlv"
    _SDM_ATT_MAP = {
        "RouterAddress": "routerAddress",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(RouterTlv, self).__init__(parent, list_op)

    @property
    def RouterAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str:
        """
        return self._get_attribute(self._SDM_ATT_MAP["RouterAddress"])

    @RouterAddress.setter
    def RouterAddress(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["RouterAddress"], value)

    def update(self, RouterAddress=None):
        # type: (str) -> RouterTlv
        """Updates routerTlv resource on the server.

        Args
        ----
        - RouterAddress (str):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, RouterAddress=None):
        # type: (str) -> RouterTlv
        """Adds a new routerTlv resource on the json, only valid with batch add utility

        Args
        ----
        - RouterAddress (str):

        Returns
        -------
        - self: This instance with all currently retrieved routerTlv resources using find and the newly added routerTlv resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, RouterAddress=None):
        # type: (str) -> RouterTlv
        """Finds and retrieves routerTlv resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve routerTlv resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all routerTlv resources from the server.

        Args
        ----
        - RouterAddress (str):

        Returns
        -------
        - self: This instance with matching routerTlv resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of routerTlv data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the routerTlv resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
