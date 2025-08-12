
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class CustomTopologyUnicastMacRange(Base):
    """NOT DEFINED
    The CustomTopologyUnicastMacRange class encapsulates a list of customTopologyUnicastMacRange resources that are managed by the user.
    A list of resources can be retrieved from the server using the CustomTopologyUnicastMacRange.find() method.
    The list can be managed by using the CustomTopologyUnicastMacRange.add() and CustomTopologyUnicastMacRange.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "customTopologyUnicastMacRange"
    _SDM_ATT_MAP = {
        "Count": "count",
        "Enabled": "enabled",
        "InterNodeMacIncrement": "interNodeMacIncrement",
        "MacIncrement": "macIncrement",
        "StartMac": "startMac",
        "StartVlanId": "startVlanId",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(CustomTopologyUnicastMacRange, self).__init__(parent, list_op)

    @property
    def Count(self):
        # type: () -> int
        """
        Returns
        -------
        - number: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["Count"])

    @Count.setter
    def Count(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Count"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def InterNodeMacIncrement(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["InterNodeMacIncrement"])

    @InterNodeMacIncrement.setter
    def InterNodeMacIncrement(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["InterNodeMacIncrement"], value)

    @property
    def MacIncrement(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["MacIncrement"])

    @MacIncrement.setter
    def MacIncrement(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["MacIncrement"], value)

    @property
    def StartMac(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["StartMac"])

    @StartMac.setter
    def StartMac(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["StartMac"], value)

    @property
    def StartVlanId(self):
        # type: () -> int
        """
        Returns
        -------
        - number: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["StartVlanId"])

    @StartVlanId.setter
    def StartVlanId(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["StartVlanId"], value)

    def update(
        self,
        Count=None,
        Enabled=None,
        InterNodeMacIncrement=None,
        MacIncrement=None,
        StartMac=None,
        StartVlanId=None,
    ):
        # type: (int, bool, str, str, str, int) -> CustomTopologyUnicastMacRange
        """Updates customTopologyUnicastMacRange resource on the server.

        Args
        ----
        - Count (number): NOT DEFINED
        - Enabled (bool): NOT DEFINED
        - InterNodeMacIncrement (str): NOT DEFINED
        - MacIncrement (str): NOT DEFINED
        - StartMac (str): NOT DEFINED
        - StartVlanId (number): NOT DEFINED

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(
        self,
        Count=None,
        Enabled=None,
        InterNodeMacIncrement=None,
        MacIncrement=None,
        StartMac=None,
        StartVlanId=None,
    ):
        # type: (int, bool, str, str, str, int) -> CustomTopologyUnicastMacRange
        """Adds a new customTopologyUnicastMacRange resource on the server and adds it to the container.

        Args
        ----
        - Count (number): NOT DEFINED
        - Enabled (bool): NOT DEFINED
        - InterNodeMacIncrement (str): NOT DEFINED
        - MacIncrement (str): NOT DEFINED
        - StartMac (str): NOT DEFINED
        - StartVlanId (number): NOT DEFINED

        Returns
        -------
        - self: This instance with all currently retrieved customTopologyUnicastMacRange resources using find and the newly added customTopologyUnicastMacRange resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained customTopologyUnicastMacRange resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self,
        Count=None,
        Enabled=None,
        InterNodeMacIncrement=None,
        MacIncrement=None,
        StartMac=None,
        StartVlanId=None,
    ):
        # type: (int, bool, str, str, str, int) -> CustomTopologyUnicastMacRange
        """Finds and retrieves customTopologyUnicastMacRange resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve customTopologyUnicastMacRange resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all customTopologyUnicastMacRange resources from the server.

        Args
        ----
        - Count (number): NOT DEFINED
        - Enabled (bool): NOT DEFINED
        - InterNodeMacIncrement (str): NOT DEFINED
        - MacIncrement (str): NOT DEFINED
        - StartMac (str): NOT DEFINED
        - StartVlanId (number): NOT DEFINED

        Returns
        -------
        - self: This instance with matching customTopologyUnicastMacRange resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of customTopologyUnicastMacRange data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the customTopologyUnicastMacRange resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
