
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class NacPosture(Base):
    """NAC Posture settings
    The NacPosture class encapsulates a list of nacPosture resources that are managed by the user.
    A list of resources can be retrieved from the server using the NacPosture.find() method.
    The list can be managed by using the NacPosture.add() and NacPosture.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "nacPosture"
    _SDM_ATT_MAP = {
        "ExpectedSystemToken": "expectedSystemToken",
        "NacTlvs": "nacTlvs",
        "Name": "name",
        "ObjectId": "objectId",
        "Selected": "selected",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(NacPosture, self).__init__(parent, list_op)

    @property
    def ExpectedSystemToken(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Expected System Token.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ExpectedSystemToken"])

    @ExpectedSystemToken.setter
    def ExpectedSystemToken(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["ExpectedSystemToken"], value)

    @property
    def NacTlvs(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str[None | /api/v1/sessions/1/ixnetwork/globals/protocolStack/dot1xGlobals/nacSettings/nacTlv]): List of NacTLVs.
        """
        return self._get_attribute(self._SDM_ATT_MAP["NacTlvs"])

    @NacTlvs.setter
    def NacTlvs(self, value):
        # type: (List[str]) -> None
        self._set_attribute(self._SDM_ATT_MAP["NacTlvs"], value)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Unique name for this NAC Posture.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    @Name.setter
    def Name(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Name"], value)

    @property
    def ObjectId(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Unique identifier for this object
        """
        return self._get_attribute(self._SDM_ATT_MAP["ObjectId"])

    @property
    def Selected(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Add to postures list.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Selected"])

    @Selected.setter
    def Selected(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Selected"], value)

    def update(self, ExpectedSystemToken=None, NacTlvs=None, Name=None, Selected=None):
        # type: (int, List[str], str, bool) -> NacPosture
        """Updates nacPosture resource on the server.

        Args
        ----
        - ExpectedSystemToken (number): Expected System Token.
        - NacTlvs (list(str[None | /api/v1/sessions/1/ixnetwork/globals/protocolStack/dot1xGlobals/nacSettings/nacTlv])): List of NacTLVs.
        - Name (str): Unique name for this NAC Posture.
        - Selected (bool): Add to postures list.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, ExpectedSystemToken=None, NacTlvs=None, Name=None, Selected=None):
        # type: (int, List[str], str, bool) -> NacPosture
        """Adds a new nacPosture resource on the server and adds it to the container.

        Args
        ----
        - ExpectedSystemToken (number): Expected System Token.
        - NacTlvs (list(str[None | /api/v1/sessions/1/ixnetwork/globals/protocolStack/dot1xGlobals/nacSettings/nacTlv])): List of NacTLVs.
        - Name (str): Unique name for this NAC Posture.
        - Selected (bool): Add to postures list.

        Returns
        -------
        - self: This instance with all currently retrieved nacPosture resources using find and the newly added nacPosture resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained nacPosture resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self,
        ExpectedSystemToken=None,
        NacTlvs=None,
        Name=None,
        ObjectId=None,
        Selected=None,
    ):
        # type: (int, List[str], str, str, bool) -> NacPosture
        """Finds and retrieves nacPosture resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve nacPosture resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all nacPosture resources from the server.

        Args
        ----
        - ExpectedSystemToken (number): Expected System Token.
        - NacTlvs (list(str[None | /api/v1/sessions/1/ixnetwork/globals/protocolStack/dot1xGlobals/nacSettings/nacTlv])): List of NacTLVs.
        - Name (str): Unique name for this NAC Posture.
        - ObjectId (str): Unique identifier for this object
        - Selected (bool): Add to postures list.

        Returns
        -------
        - self: This instance with matching nacPosture resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of nacPosture data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the nacPosture resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
