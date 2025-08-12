
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class TriggeredPingLearnedInfo(Base):
    """This object holds lists of the triggered ping learned information.
    The TriggeredPingLearnedInfo class encapsulates a list of triggeredPingLearnedInfo resources that are managed by the system.
    A list of resources can be retrieved from the server using the TriggeredPingLearnedInfo.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "triggeredPingLearnedInfo"
    _SDM_ATT_MAP = {
        "Fec": "fec",
        "IncomingLabelStack": "incomingLabelStack",
        "OutgoingLabelStack": "outgoingLabelStack",
        "PeerIpAddress": "peerIpAddress",
        "Reachability": "reachability",
        "ReturnCode": "returnCode",
        "ReturnSubCode": "returnSubCode",
        "Rtt": "rtt",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(TriggeredPingLearnedInfo, self).__init__(parent, list_op)

    @property
    def Fec(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the Forwarding Equivalence Class component.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Fec"])

    @property
    def IncomingLabelStack(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the incoming label stack value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IncomingLabelStack"])

    @property
    def OutgoingLabelStack(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the outgoing label stack value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["OutgoingLabelStack"])

    @property
    def PeerIpAddress(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the learnt IP address for the session.
        """
        return self._get_attribute(self._SDM_ATT_MAP["PeerIpAddress"])

    @property
    def Reachability(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the specification of whether the queried MEP could be reached or not, Failure/Partial/Complete.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Reachability"])

    @property
    def ReturnCode(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the return code value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ReturnCode"])

    @property
    def ReturnSubCode(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This signifies the return subcode value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ReturnSubCode"])

    @property
    def Rtt(self):
        # type: () -> str
        """
        Returns
        -------
        - str: This signifies the Round Trip Time.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Rtt"])

    def add(self):
        """Adds a new triggeredPingLearnedInfo resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved triggeredPingLearnedInfo resources using find and the newly added triggeredPingLearnedInfo resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        Fec=None,
        IncomingLabelStack=None,
        OutgoingLabelStack=None,
        PeerIpAddress=None,
        Reachability=None,
        ReturnCode=None,
        ReturnSubCode=None,
        Rtt=None,
    ):
        # type: (str, str, str, str, str, str, int, str) -> TriggeredPingLearnedInfo
        """Finds and retrieves triggeredPingLearnedInfo resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve triggeredPingLearnedInfo resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all triggeredPingLearnedInfo resources from the server.

        Args
        ----
        - Fec (str): This signifies the Forwarding Equivalence Class component.
        - IncomingLabelStack (str): This signifies the incoming label stack value.
        - OutgoingLabelStack (str): This signifies the outgoing label stack value.
        - PeerIpAddress (str): This signifies the learnt IP address for the session.
        - Reachability (str): This signifies the specification of whether the queried MEP could be reached or not, Failure/Partial/Complete.
        - ReturnCode (str): This signifies the return code value.
        - ReturnSubCode (number): This signifies the return subcode value.
        - Rtt (str): This signifies the Round Trip Time.

        Returns
        -------
        - self: This instance with matching triggeredPingLearnedInfo resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of triggeredPingLearnedInfo data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the triggeredPingLearnedInfo resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
