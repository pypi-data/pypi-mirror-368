
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class SourceTrafficRange(Base):
    """Configures the source traffic range values.
    The SourceTrafficRange class encapsulates a list of sourceTrafficRange resources that are managed by the user.
    A list of resources can be retrieved from the server using the SourceTrafficRange.find() method.
    The list can be managed by using the SourceTrafficRange.add() and SourceTrafficRange.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "sourceTrafficRange"
    _SDM_ATT_MAP = {
        "AddrFamily": "addrFamily",
        "FilterOnGroupAddress": "filterOnGroupAddress",
        "GroupAddress": "groupAddress",
        "GrpCountPerLsp": "grpCountPerLsp",
        "SourceAddress": "sourceAddress",
        "SrcCountPerLsp": "srcCountPerLsp",
    }
    _SDM_ENUM_MAP = {
        "addrFamily": ["ipv4", "ipv6"],
    }

    def __init__(self, parent, list_op=False):
        super(SourceTrafficRange, self).__init__(parent, list_op)

    @property
    def AddrFamily(self):
        # type: () -> str
        """
        Returns
        -------
        - str(ipv4 | ipv6): The address familyt value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["AddrFamily"])

    @AddrFamily.setter
    def AddrFamily(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["AddrFamily"], value)

    @property
    def FilterOnGroupAddress(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: The available filters on group address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["FilterOnGroupAddress"])

    @FilterOnGroupAddress.setter
    def FilterOnGroupAddress(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["FilterOnGroupAddress"], value)

    @property
    def GroupAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The group address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["GroupAddress"])

    @GroupAddress.setter
    def GroupAddress(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["GroupAddress"], value)

    @property
    def GrpCountPerLsp(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The total group count per LSP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["GrpCountPerLsp"])

    @GrpCountPerLsp.setter
    def GrpCountPerLsp(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["GrpCountPerLsp"], value)

    @property
    def SourceAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The source address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["SourceAddress"])

    @SourceAddress.setter
    def SourceAddress(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["SourceAddress"], value)

    @property
    def SrcCountPerLsp(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The total source count per LSP.
        """
        return self._get_attribute(self._SDM_ATT_MAP["SrcCountPerLsp"])

    @SrcCountPerLsp.setter
    def SrcCountPerLsp(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["SrcCountPerLsp"], value)

    def update(
        self,
        AddrFamily=None,
        FilterOnGroupAddress=None,
        GroupAddress=None,
        GrpCountPerLsp=None,
        SourceAddress=None,
        SrcCountPerLsp=None,
    ):
        # type: (str, bool, str, int, str, int) -> SourceTrafficRange
        """Updates sourceTrafficRange resource on the server.

        Args
        ----
        - AddrFamily (str(ipv4 | ipv6)): The address familyt value.
        - FilterOnGroupAddress (bool): The available filters on group address.
        - GroupAddress (str): The group address.
        - GrpCountPerLsp (number): The total group count per LSP.
        - SourceAddress (str): The source address.
        - SrcCountPerLsp (number): The total source count per LSP.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(
        self,
        AddrFamily=None,
        FilterOnGroupAddress=None,
        GroupAddress=None,
        GrpCountPerLsp=None,
        SourceAddress=None,
        SrcCountPerLsp=None,
    ):
        # type: (str, bool, str, int, str, int) -> SourceTrafficRange
        """Adds a new sourceTrafficRange resource on the server and adds it to the container.

        Args
        ----
        - AddrFamily (str(ipv4 | ipv6)): The address familyt value.
        - FilterOnGroupAddress (bool): The available filters on group address.
        - GroupAddress (str): The group address.
        - GrpCountPerLsp (number): The total group count per LSP.
        - SourceAddress (str): The source address.
        - SrcCountPerLsp (number): The total source count per LSP.

        Returns
        -------
        - self: This instance with all currently retrieved sourceTrafficRange resources using find and the newly added sourceTrafficRange resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained sourceTrafficRange resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self,
        AddrFamily=None,
        FilterOnGroupAddress=None,
        GroupAddress=None,
        GrpCountPerLsp=None,
        SourceAddress=None,
        SrcCountPerLsp=None,
    ):
        # type: (str, bool, str, int, str, int) -> SourceTrafficRange
        """Finds and retrieves sourceTrafficRange resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve sourceTrafficRange resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all sourceTrafficRange resources from the server.

        Args
        ----
        - AddrFamily (str(ipv4 | ipv6)): The address familyt value.
        - FilterOnGroupAddress (bool): The available filters on group address.
        - GroupAddress (str): The group address.
        - GrpCountPerLsp (number): The total group count per LSP.
        - SourceAddress (str): The source address.
        - SrcCountPerLsp (number): The total source count per LSP.

        Returns
        -------
        - self: This instance with matching sourceTrafficRange resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of sourceTrafficRange data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the sourceTrafficRange resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
