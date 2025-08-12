
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class State(Base):
    """Describes the current state of the physical port.
    The State class encapsulates a required state resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "state"
    _SDM_ATT_MAP = {
        "LinkDown": "linkDown",
        "StpBlock": "stpBlock",
        "StpForward": "stpForward",
        "StpLearn": "stpLearn",
        "StpListen": "stpListen",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(State, self).__init__(parent, list_op)

    @property
    def LinkDown(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates that, no physical link is present.
        """
        return self._get_attribute(self._SDM_ATT_MAP["LinkDown"])

    @LinkDown.setter
    def LinkDown(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["LinkDown"], value)

    @property
    def StpBlock(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates that the port is not part of spanning tree.
        """
        return self._get_attribute(self._SDM_ATT_MAP["StpBlock"])

    @StpBlock.setter
    def StpBlock(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["StpBlock"], value)

    @property
    def StpForward(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates that the port is learning and relaying frames.
        """
        return self._get_attribute(self._SDM_ATT_MAP["StpForward"])

    @StpForward.setter
    def StpForward(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["StpForward"], value)

    @property
    def StpLearn(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates that the port is learning but not relaying frames.
        """
        return self._get_attribute(self._SDM_ATT_MAP["StpLearn"])

    @StpLearn.setter
    def StpLearn(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["StpLearn"], value)

    @property
    def StpListen(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Indicates that the port is not learning or relaying frames.
        """
        return self._get_attribute(self._SDM_ATT_MAP["StpListen"])

    @StpListen.setter
    def StpListen(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["StpListen"], value)

    def update(
        self,
        LinkDown=None,
        StpBlock=None,
        StpForward=None,
        StpLearn=None,
        StpListen=None,
    ):
        # type: (bool, bool, bool, bool, bool) -> State
        """Updates state resource on the server.

        Args
        ----
        - LinkDown (bool): Indicates that, no physical link is present.
        - StpBlock (bool): Indicates that the port is not part of spanning tree.
        - StpForward (bool): Indicates that the port is learning and relaying frames.
        - StpLearn (bool): Indicates that the port is learning but not relaying frames.
        - StpListen (bool): Indicates that the port is not learning or relaying frames.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        LinkDown=None,
        StpBlock=None,
        StpForward=None,
        StpLearn=None,
        StpListen=None,
    ):
        # type: (bool, bool, bool, bool, bool) -> State
        """Finds and retrieves state resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve state resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all state resources from the server.

        Args
        ----
        - LinkDown (bool): Indicates that, no physical link is present.
        - StpBlock (bool): Indicates that the port is not part of spanning tree.
        - StpForward (bool): Indicates that the port is learning and relaying frames.
        - StpLearn (bool): Indicates that the port is learning but not relaying frames.
        - StpListen (bool): Indicates that the port is not learning or relaying frames.

        Returns
        -------
        - self: This instance with matching state resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of state data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the state resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
