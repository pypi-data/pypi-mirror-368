
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class OriginIpInfo(Base):
    """(Read Only) List of learned as well as self Origin IP.
    The OriginIpInfo class encapsulates a list of originIpInfo resources that are managed by the system.
    A list of resources can be retrieved from the server using the OriginIpInfo.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "originIpInfo"
    _SDM_ATT_MAP = {
        "OriginIp": "originIp",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(OriginIpInfo, self).__init__(parent, list_op)

    @property
    def RdInfo(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.rdinfo_5d0e7b1db6cf0b7daa15e78fa449470c.RdInfo): An instance of the RdInfo class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.rdinfo_5d0e7b1db6cf0b7daa15e78fa449470c import (
            RdInfo,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("RdInfo", None) is not None:
                return self._properties.get("RdInfo")
        return RdInfo(self)

    @property
    def OriginIp(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Origin IP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["OriginIp"])

    def add(self):
        """Adds a new originIpInfo resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved originIpInfo resources using find and the newly added originIpInfo resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, OriginIp=None):
        # type: (str) -> OriginIpInfo
        """Finds and retrieves originIpInfo resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve originIpInfo resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all originIpInfo resources from the server.

        Args
        ----
        - OriginIp (str): (Read Only) Origin IP.

        Returns
        -------
        - self: This instance with matching originIpInfo resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of originIpInfo data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the originIpInfo resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
