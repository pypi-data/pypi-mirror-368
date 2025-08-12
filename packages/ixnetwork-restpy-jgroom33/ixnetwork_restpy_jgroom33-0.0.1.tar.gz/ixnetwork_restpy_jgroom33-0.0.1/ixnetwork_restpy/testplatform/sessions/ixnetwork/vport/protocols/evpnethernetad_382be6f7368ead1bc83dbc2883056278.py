
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class EvpnEthernetAd(Base):
    """(Read Only) Ethernet Auto-Discovery route type.
    The EvpnEthernetAd class encapsulates a list of evpnEthernetAd resources that are managed by the system.
    A list of resources can be retrieved from the server using the EvpnEthernetAd.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "evpnEthernetAd"
    _SDM_ATT_MAP = {
        "Esi": "esi",
        "Neighbor": "neighbor",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(EvpnEthernetAd, self).__init__(parent, list_op)

    @property
    def NextHopInfo(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.nexthopinfo_7c16f9ecbb1e65dd91f8f94fb13e38f9.NextHopInfo): An instance of the NextHopInfo class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.nexthopinfo_7c16f9ecbb1e65dd91f8f94fb13e38f9 import (
            NextHopInfo,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("NextHopInfo", None) is not None:
                return self._properties.get("NextHopInfo")
        return NextHopInfo(self)

    @property
    def Esi(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Ethernet Segment ID.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Esi"])

    @property
    def Neighbor(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read Only) Neighbor IP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Neighbor"])

    def add(self):
        """Adds a new evpnEthernetAd resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved evpnEthernetAd resources using find and the newly added evpnEthernetAd resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Esi=None, Neighbor=None):
        # type: (str, str) -> EvpnEthernetAd
        """Finds and retrieves evpnEthernetAd resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve evpnEthernetAd resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all evpnEthernetAd resources from the server.

        Args
        ----
        - Esi (str): (Read Only) Ethernet Segment ID.
        - Neighbor (str): (Read Only) Neighbor IP.

        Returns
        -------
        - self: This instance with matching evpnEthernetAd resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of evpnEthernetAd data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the evpnEthernetAd resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
