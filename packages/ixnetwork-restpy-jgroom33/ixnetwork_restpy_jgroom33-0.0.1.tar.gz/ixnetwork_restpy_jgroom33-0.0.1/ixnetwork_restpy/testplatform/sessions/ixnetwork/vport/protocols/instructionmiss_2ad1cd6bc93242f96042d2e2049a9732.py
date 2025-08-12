
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class InstructionMiss(Base):
    """Select the type of instruction miss capabilities that the table miss flow entry will support.
    The InstructionMiss class encapsulates a required instructionMiss resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "instructionMiss"
    _SDM_ATT_MAP = {
        "ApplyActions": "applyActions",
        "ClearActions": "clearActions",
        "Experimenter": "experimenter",
        "GoToTable": "goToTable",
        "Meter": "meter",
        "WriteActions": "writeActions",
        "WriteMetadata": "writeMetadata",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(InstructionMiss, self).__init__(parent, list_op)

    @property
    def ApplyActions(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, applies the actions associated with a flow immediately.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ApplyActions"])

    @ApplyActions.setter
    def ApplyActions(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["ApplyActions"], value)

    @property
    def ClearActions(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, clears the actions attached with the flow.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ClearActions"])

    @ClearActions.setter
    def ClearActions(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["ClearActions"], value)

    @property
    def Experimenter(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, gives experimenter instruction.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Experimenter"])

    @Experimenter.setter
    def Experimenter(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Experimenter"], value)

    @property
    def GoToTable(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, forwards the packet to the next table in the pipeline.
        """
        return self._get_attribute(self._SDM_ATT_MAP["GoToTable"])

    @GoToTable.setter
    def GoToTable(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["GoToTable"], value)

    @property
    def Meter(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, directs a flow to a particular meter.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Meter"])

    @Meter.setter
    def Meter(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Meter"], value)

    @property
    def WriteActions(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, appends actions to the existing action set of the packet.
        """
        return self._get_attribute(self._SDM_ATT_MAP["WriteActions"])

    @WriteActions.setter
    def WriteActions(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["WriteActions"], value)

    @property
    def WriteMetadata(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If selected, writes the masked metadata field to the match.
        """
        return self._get_attribute(self._SDM_ATT_MAP["WriteMetadata"])

    @WriteMetadata.setter
    def WriteMetadata(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["WriteMetadata"], value)

    def update(
        self,
        ApplyActions=None,
        ClearActions=None,
        Experimenter=None,
        GoToTable=None,
        Meter=None,
        WriteActions=None,
        WriteMetadata=None,
    ):
        # type: (bool, bool, bool, bool, bool, bool, bool) -> InstructionMiss
        """Updates instructionMiss resource on the server.

        Args
        ----
        - ApplyActions (bool): If selected, applies the actions associated with a flow immediately.
        - ClearActions (bool): If selected, clears the actions attached with the flow.
        - Experimenter (bool): If selected, gives experimenter instruction.
        - GoToTable (bool): If selected, forwards the packet to the next table in the pipeline.
        - Meter (bool): If selected, directs a flow to a particular meter.
        - WriteActions (bool): If selected, appends actions to the existing action set of the packet.
        - WriteMetadata (bool): If selected, writes the masked metadata field to the match.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        ApplyActions=None,
        ClearActions=None,
        Experimenter=None,
        GoToTable=None,
        Meter=None,
        WriteActions=None,
        WriteMetadata=None,
    ):
        # type: (bool, bool, bool, bool, bool, bool, bool) -> InstructionMiss
        """Finds and retrieves instructionMiss resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve instructionMiss resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all instructionMiss resources from the server.

        Args
        ----
        - ApplyActions (bool): If selected, applies the actions associated with a flow immediately.
        - ClearActions (bool): If selected, clears the actions attached with the flow.
        - Experimenter (bool): If selected, gives experimenter instruction.
        - GoToTable (bool): If selected, forwards the packet to the next table in the pipeline.
        - Meter (bool): If selected, directs a flow to a particular meter.
        - WriteActions (bool): If selected, appends actions to the existing action set of the packet.
        - WriteMetadata (bool): If selected, writes the masked metadata field to the match.

        Returns
        -------
        - self: This instance with matching instructionMiss resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of instructionMiss data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the instructionMiss resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
