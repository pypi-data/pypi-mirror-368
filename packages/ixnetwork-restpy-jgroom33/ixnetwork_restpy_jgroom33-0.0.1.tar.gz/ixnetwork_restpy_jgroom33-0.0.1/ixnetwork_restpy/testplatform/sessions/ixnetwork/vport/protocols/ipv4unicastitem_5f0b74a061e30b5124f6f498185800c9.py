
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Ipv4UnicastItem(Base):
    """The DCE ISIS Learned Information option fetches the learned information for the IPv4 Unicast Item of a particular DCE ISIS router.
    The Ipv4UnicastItem class encapsulates a list of ipv4UnicastItem resources that are managed by the system.
    A list of resources can be retrieved from the server using the Ipv4UnicastItem.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "ipv4UnicastItem"
    _SDM_ATT_MAP = {
        "Ipv4UnicastSourceAddress": "ipv4UnicastSourceAddress",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Ipv4UnicastItem, self).__init__(parent, list_op)

    @property
    def Ipv4UnicastSourceAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This indicates the IPv4 Source, if any, associated with the IPv4 Multicast Group Address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Ipv4UnicastSourceAddress"])

    def add(self):
        """Adds a new ipv4UnicastItem resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved ipv4UnicastItem resources using find and the newly added ipv4UnicastItem resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Ipv4UnicastSourceAddress=None):
        # type: (str) -> Ipv4UnicastItem
        """Finds and retrieves ipv4UnicastItem resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve ipv4UnicastItem resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all ipv4UnicastItem resources from the server.

        Args
        ----
        - Ipv4UnicastSourceAddress (str): This indicates the IPv4 Source, if any, associated with the IPv4 Multicast Group Address.

        Returns
        -------
        - self: This instance with matching ipv4UnicastItem resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of ipv4UnicastItem data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the ipv4UnicastItem resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
