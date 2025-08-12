
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class AtmLabelRange(Base):
    """A single ATM label range of VPIs and VCIs used for ATM sessions.
    The AtmLabelRange class encapsulates a list of atmLabelRange resources that are managed by the user.
    A list of resources can be retrieved from the server using the AtmLabelRange.find() method.
    The list can be managed by using the AtmLabelRange.add() and AtmLabelRange.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "atmLabelRange"
    _SDM_ATT_MAP = {
        "MaxVci": "maxVci",
        "MaxVpi": "maxVpi",
        "MinVci": "minVci",
        "MinVpi": "minVpi",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(AtmLabelRange, self).__init__(parent, list_op)

    @property
    def MaxVci(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The maximum virtual circuit identifier (VCI) value that will be included in the ATM label range. The valid maximum VCI value = 65,535 [0xFFFF (hex)].
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaxVci"])

    @MaxVci.setter
    def MaxVci(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MaxVci"], value)

    @property
    def MaxVpi(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The maximum virtual path identifier (VPI) value that will be included in the ATM label range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MaxVpi"])

    @MaxVpi.setter
    def MaxVpi(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MaxVpi"], value)

    @property
    def MinVci(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The minimum virtual circuit identifier (VCI) value that will be included in the ATM label range.The valid minimum VCI value = 33.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MinVci"])

    @MinVci.setter
    def MinVci(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MinVci"], value)

    @property
    def MinVpi(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The minimum virtual path identifier (VPI) value that will be included in the ATM label range.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MinVpi"])

    @MinVpi.setter
    def MinVpi(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["MinVpi"], value)

    def update(self, MaxVci=None, MaxVpi=None, MinVci=None, MinVpi=None):
        # type: (int, int, int, int) -> AtmLabelRange
        """Updates atmLabelRange resource on the server.

        Args
        ----
        - MaxVci (number): The maximum virtual circuit identifier (VCI) value that will be included in the ATM label range. The valid maximum VCI value = 65,535 [0xFFFF (hex)].
        - MaxVpi (number): The maximum virtual path identifier (VPI) value that will be included in the ATM label range.
        - MinVci (number): The minimum virtual circuit identifier (VCI) value that will be included in the ATM label range.The valid minimum VCI value = 33.
        - MinVpi (number): The minimum virtual path identifier (VPI) value that will be included in the ATM label range.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, MaxVci=None, MaxVpi=None, MinVci=None, MinVpi=None):
        # type: (int, int, int, int) -> AtmLabelRange
        """Adds a new atmLabelRange resource on the server and adds it to the container.

        Args
        ----
        - MaxVci (number): The maximum virtual circuit identifier (VCI) value that will be included in the ATM label range. The valid maximum VCI value = 65,535 [0xFFFF (hex)].
        - MaxVpi (number): The maximum virtual path identifier (VPI) value that will be included in the ATM label range.
        - MinVci (number): The minimum virtual circuit identifier (VCI) value that will be included in the ATM label range.The valid minimum VCI value = 33.
        - MinVpi (number): The minimum virtual path identifier (VPI) value that will be included in the ATM label range.

        Returns
        -------
        - self: This instance with all currently retrieved atmLabelRange resources using find and the newly added atmLabelRange resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained atmLabelRange resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, MaxVci=None, MaxVpi=None, MinVci=None, MinVpi=None):
        # type: (int, int, int, int) -> AtmLabelRange
        """Finds and retrieves atmLabelRange resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve atmLabelRange resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all atmLabelRange resources from the server.

        Args
        ----
        - MaxVci (number): The maximum virtual circuit identifier (VCI) value that will be included in the ATM label range. The valid maximum VCI value = 65,535 [0xFFFF (hex)].
        - MaxVpi (number): The maximum virtual path identifier (VPI) value that will be included in the ATM label range.
        - MinVci (number): The minimum virtual circuit identifier (VCI) value that will be included in the ATM label range.The valid minimum VCI value = 33.
        - MinVpi (number): The minimum virtual path identifier (VPI) value that will be included in the ATM label range.

        Returns
        -------
        - self: This instance with matching atmLabelRange resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of atmLabelRange data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the atmLabelRange resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
