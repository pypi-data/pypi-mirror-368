
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class EvpnMulticast(Base):
    """(Read Only) Inclusive Multicast Ethernet Tag route type.
    The EvpnMulticast class encapsulates a list of evpnMulticast resources that are managed by the system.
    A list of resources can be retrieved from the server using the EvpnMulticast.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "evpnMulticast"
    _SDM_ATT_MAP = {
        "Neighbor": "neighbor",
        "OriginatorsIp": "originatorsIp",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(EvpnMulticast, self).__init__(parent, list_op)

    @property
    def NextHopInfo(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.nexthopinfo_27593f5bf51f1d6b95b80c04d9eaf7f0.NextHopInfo): An instance of the NextHopInfo class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.nexthopinfo_27593f5bf51f1d6b95b80c04d9eaf7f0 import (
            NextHopInfo,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("NextHopInfo", None) is not None:
                return self._properties.get("NextHopInfo")
        return NextHopInfo(self)

    @property
    def Neighbor(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Neighbr IP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Neighbor"])

    @property
    def OriginatorsIp(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Learned Originator's IP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["OriginatorsIp"])

    def add(self):
        """Adds a new evpnMulticast resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved evpnMulticast resources using find and the newly added evpnMulticast resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Neighbor=None, OriginatorsIp=None):
        # type: (str, str) -> EvpnMulticast
        """Finds and retrieves evpnMulticast resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve evpnMulticast resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all evpnMulticast resources from the server.

        Args
        ----
        - Neighbor (str): (Read Only) Neighbr IP.
        - OriginatorsIp (str): (Read Only) Learned Originator's IP.

        Returns
        -------
        - self: This instance with matching evpnMulticast resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of evpnMulticast data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the evpnMulticast resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
