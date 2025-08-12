
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class TrafficGroup(Base):
    """This object fetches the traffic group related statistics.
    The TrafficGroup class encapsulates a list of trafficGroup resources that are managed by the user.
    A list of resources can be retrieved from the server using the TrafficGroup.find() method.
    The list can be managed by using the TrafficGroup.add() and TrafficGroup.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "trafficGroup"
    _SDM_ATT_MAP = {
        "Name": "name",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(TrafficGroup, self).__init__(parent, list_op)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Name of the traffic item.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Name"])

    @Name.setter
    def Name(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Name"], value)

    def update(self, Name=None):
        # type: (str) -> TrafficGroup
        """Updates trafficGroup resource on the server.

        Args
        ----
        - Name (str): Name of the traffic item.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Name=None):
        # type: (str) -> TrafficGroup
        """Adds a new trafficGroup resource on the server and adds it to the container.

        Args
        ----
        - Name (str): Name of the traffic item.

        Returns
        -------
        - self: This instance with all currently retrieved trafficGroup resources using find and the newly added trafficGroup resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained trafficGroup resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Name=None):
        # type: (str) -> TrafficGroup
        """Finds and retrieves trafficGroup resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve trafficGroup resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all trafficGroup resources from the server.

        Args
        ----
        - Name (str): Name of the traffic item.

        Returns
        -------
        - self: This instance with matching trafficGroup resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of trafficGroup data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the trafficGroup resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
