
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class IptvGlobals(Base):
    """
    The IptvGlobals class encapsulates a list of iptvGlobals resources that are managed by the user.
    A list of resources can be retrieved from the server using the IptvGlobals.find() method.
    The list can be managed by using the IptvGlobals.add() and IptvGlobals.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "iptvGlobals"
    _SDM_ATT_MAP = {
        "ObjectId": "objectId",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(IptvGlobals, self).__init__(parent, list_op)

    @property
    def GlobalChannelList(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.globalchannellist.globalchannellist.GlobalChannelList): An instance of the GlobalChannelList class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.globalchannellist.globalchannellist import (
            GlobalChannelList,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("GlobalChannelList", None) is not None:
                return self._properties.get("GlobalChannelList")
        return GlobalChannelList(self)

    @property
    def IgmpGroupRange(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.igmpgrouprange.igmpgrouprange.IgmpGroupRange): An instance of the IgmpGroupRange class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.igmpgrouprange.igmpgrouprange import (
            IgmpGroupRange,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("IgmpGroupRange", None) is not None:
                return self._properties.get("IgmpGroupRange")
        return IgmpGroupRange(self)

    @property
    def IptvProfile(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.iptvprofile.iptvprofile.IptvProfile): An instance of the IptvProfile class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.iptvglobals.iptvprofile.iptvprofile import (
            IptvProfile,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("IptvProfile", None) is not None:
                return self._properties.get("IptvProfile")
        return IptvProfile(self)

    @property
    def ObjectId(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Unique identifier for this object
        """
        return self._get_attribute(self._SDM_ATT_MAP["ObjectId"])

    def add(self):
        """Adds a new iptvGlobals resource on the server and adds it to the container.

        Returns
        -------
        - self: This instance with all currently retrieved iptvGlobals resources using find and the newly added iptvGlobals resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained iptvGlobals resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, ObjectId=None):
        # type: (str) -> IptvGlobals
        """Finds and retrieves iptvGlobals resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve iptvGlobals resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all iptvGlobals resources from the server.

        Args
        ----
        - ObjectId (str): Unique identifier for this object

        Returns
        -------
        - self: This instance with matching iptvGlobals resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of iptvGlobals data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the iptvGlobals resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
