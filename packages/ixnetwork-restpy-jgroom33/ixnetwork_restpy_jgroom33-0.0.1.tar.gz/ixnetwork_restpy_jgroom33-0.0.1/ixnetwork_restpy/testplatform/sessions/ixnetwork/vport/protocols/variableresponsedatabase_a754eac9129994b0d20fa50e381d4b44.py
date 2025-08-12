
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class VariableResponseDatabase(Base):
    """
    The VariableResponseDatabase class encapsulates a list of variableResponseDatabase resources that are managed by the user.
    A list of resources can be retrieved from the server using the VariableResponseDatabase.find() method.
    The list can be managed by using the VariableResponseDatabase.add() and VariableResponseDatabase.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "variableResponseDatabase"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "VariableBranch": "variableBranch",
        "VariableIndication": "variableIndication",
        "VariableLeaf": "variableLeaf",
        "VariableValue": "variableValue",
        "VariableWidth": "variableWidth",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(VariableResponseDatabase, self).__init__(parent, list_op)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def VariableBranch(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["VariableBranch"])

    @VariableBranch.setter
    def VariableBranch(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["VariableBranch"], value)

    @property
    def VariableIndication(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool:
        """
        return self._get_attribute(self._SDM_ATT_MAP["VariableIndication"])

    @VariableIndication.setter
    def VariableIndication(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["VariableIndication"], value)

    @property
    def VariableLeaf(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["VariableLeaf"])

    @VariableLeaf.setter
    def VariableLeaf(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["VariableLeaf"], value)

    @property
    def VariableValue(self):
        # type: () -> str
        """
        Returns
        -------
        - str:
        """
        return self._get_attribute(self._SDM_ATT_MAP["VariableValue"])

    @VariableValue.setter
    def VariableValue(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["VariableValue"], value)

    @property
    def VariableWidth(self):
        # type: () -> int
        """
        Returns
        -------
        - number:
        """
        return self._get_attribute(self._SDM_ATT_MAP["VariableWidth"])

    @VariableWidth.setter
    def VariableWidth(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["VariableWidth"], value)

    def update(
        self,
        Enabled=None,
        VariableBranch=None,
        VariableIndication=None,
        VariableLeaf=None,
        VariableValue=None,
        VariableWidth=None,
    ):
        # type: (bool, int, bool, int, str, int) -> VariableResponseDatabase
        """Updates variableResponseDatabase resource on the server.

        Args
        ----
        - Enabled (bool):
        - VariableBranch (number):
        - VariableIndication (bool):
        - VariableLeaf (number):
        - VariableValue (str):
        - VariableWidth (number):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(
        self,
        Enabled=None,
        VariableBranch=None,
        VariableIndication=None,
        VariableLeaf=None,
        VariableValue=None,
        VariableWidth=None,
    ):
        # type: (bool, int, bool, int, str, int) -> VariableResponseDatabase
        """Adds a new variableResponseDatabase resource on the server and adds it to the container.

        Args
        ----
        - Enabled (bool):
        - VariableBranch (number):
        - VariableIndication (bool):
        - VariableLeaf (number):
        - VariableValue (str):
        - VariableWidth (number):

        Returns
        -------
        - self: This instance with all currently retrieved variableResponseDatabase resources using find and the newly added variableResponseDatabase resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained variableResponseDatabase resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self,
        Enabled=None,
        VariableBranch=None,
        VariableIndication=None,
        VariableLeaf=None,
        VariableValue=None,
        VariableWidth=None,
    ):
        # type: (bool, int, bool, int, str, int) -> VariableResponseDatabase
        """Finds and retrieves variableResponseDatabase resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve variableResponseDatabase resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all variableResponseDatabase resources from the server.

        Args
        ----
        - Enabled (bool):
        - VariableBranch (number):
        - VariableIndication (bool):
        - VariableLeaf (number):
        - VariableValue (str):
        - VariableWidth (number):

        Returns
        -------
        - self: This instance with matching variableResponseDatabase resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of variableResponseDatabase data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the variableResponseDatabase resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
