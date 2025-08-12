
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class NextHopInfo(Base):
    """(Read Only) List of next hops learned.
    The NextHopInfo class encapsulates a list of nextHopInfo resources that are managed by the system.
    A list of resources can be retrieved from the server using the NextHopInfo.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "nextHopInfo"
    _SDM_ATT_MAP = {
        "NextHop": "nextHop",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(NextHopInfo, self).__init__(parent, list_op)

    @property
    def RdInfo(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.rdinfo_65d647e799bc16edf6f558b7893ebe8a.RdInfo): An instance of the RdInfo class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.rdinfo_65d647e799bc16edf6f558b7893ebe8a import (
            RdInfo,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("RdInfo", None) is not None:
                return self._properties.get("RdInfo")
        return RdInfo(self)

    @property
    def NextHop(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Next Hop IP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["NextHop"])

    def add(self):
        """Adds a new nextHopInfo resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved nextHopInfo resources using find and the newly added nextHopInfo resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, NextHop=None):
        # type: (str) -> NextHopInfo
        """Finds and retrieves nextHopInfo resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve nextHopInfo resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all nextHopInfo resources from the server.

        Args
        ----
        - NextHop (str): (Read Only) Next Hop IP.

        Returns
        -------
        - self: This instance with matching nextHopInfo resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of nextHopInfo data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the nextHopInfo resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
