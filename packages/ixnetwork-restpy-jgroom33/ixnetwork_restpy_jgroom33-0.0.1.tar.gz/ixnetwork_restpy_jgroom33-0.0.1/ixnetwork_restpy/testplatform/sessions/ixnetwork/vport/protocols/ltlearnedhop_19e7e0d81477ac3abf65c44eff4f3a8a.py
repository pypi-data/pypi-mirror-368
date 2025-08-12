
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class LtLearnedHop(Base):
    """This object contains the link trace hop learned information.
    The LtLearnedHop class encapsulates a list of ltLearnedHop resources that are managed by the system.
    A list of resources can be retrieved from the server using the LtLearnedHop.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "ltLearnedHop"
    _SDM_ATT_MAP = {
        "EgressMac": "egressMac",
        "IngressMac": "ingressMac",
        "ReplyTtl": "replyTtl",
        "Self": "self",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(LtLearnedHop, self).__init__(parent, list_op)

    @property
    def EgressMac(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (read only) The link trace message egress MAC address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["EgressMac"])

    @property
    def IngressMac(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (read only) The link trace message ingress MAC address.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IngressMac"])

    @property
    def ReplyTtl(self):
        # type: () -> int
        """
        Returns
        -------
        - number: (read only) The time-to-live value of the link trace hop information, in milliseconds.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ReplyTtl"])

    @property
    def Self(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: (read only) If true, the next hop is the origin of the message.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Self"])

    def add(self):
        """Adds a new ltLearnedHop resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved ltLearnedHop resources using find and the newly added ltLearnedHop resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, EgressMac=None, IngressMac=None, ReplyTtl=None, Self=None):
        # type: (str, str, int, bool) -> LtLearnedHop
        """Finds and retrieves ltLearnedHop resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve ltLearnedHop resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all ltLearnedHop resources from the server.

        Args
        ----
        - EgressMac (str): (read only) The link trace message egress MAC address.
        - IngressMac (str): (read only) The link trace message ingress MAC address.
        - ReplyTtl (number): (read only) The time-to-live value of the link trace hop information, in milliseconds.
        - Self (bool): (read only) If true, the next hop is the origin of the message.

        Returns
        -------
        - self: This instance with matching ltLearnedHop resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of ltLearnedHop data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the ltLearnedHop resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
