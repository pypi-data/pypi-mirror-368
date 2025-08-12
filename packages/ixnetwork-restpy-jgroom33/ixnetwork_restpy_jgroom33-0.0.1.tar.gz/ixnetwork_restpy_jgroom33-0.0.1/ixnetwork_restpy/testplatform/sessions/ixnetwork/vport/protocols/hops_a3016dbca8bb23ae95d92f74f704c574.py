
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Hops(Base):
    """This object holds attributes for Trace Route Hops view.
    The Hops class encapsulates a list of hops resources that are managed by the system.
    A list of resources can be retrieved from the server using the Hops.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "hops"
    _SDM_ATT_MAP = {
        "ReturnCode": "returnCode",
        "ReturnSubCode": "returnSubCode",
        "SrcIp": "srcIp",
        "Ttl": "ttl",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Hops, self).__init__(parent, list_op)

    @property
    def ReturnCode(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the return code to be specified in the trace route hop.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ReturnCode"])

    @property
    def ReturnSubCode(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This signifies the return sub-code to be specified in the trace route hop.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ReturnSubCode"])

    @property
    def SrcIp(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the source IP address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["SrcIp"])

    @property
    def Ttl(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This signifies the MPLS time to live value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Ttl"])

    def add(self):
        """Adds a new hops resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved hops resources using find and the newly added hops resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, ReturnCode=None, ReturnSubCode=None, SrcIp=None, Ttl=None):
        # type: (str, int, str, int) -> Hops
        """Finds and retrieves hops resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve hops resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all hops resources from the server.

        Args
        ----
        - ReturnCode (str): This signifies the return code to be specified in the trace route hop.
        - ReturnSubCode (number): This signifies the return sub-code to be specified in the trace route hop.
        - SrcIp (str): This signifies the source IP address.
        - Ttl (number): This signifies the MPLS time to live value.

        Returns
        -------
        - self: This instance with matching hops resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of hops data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the hops resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
