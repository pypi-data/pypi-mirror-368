
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class NacApps(Base):
    """TLV Application Code
    The NacApps class encapsulates a list of nacApps resources that are managed by the user.
    A list of resources can be retrieved from the server using the NacApps.find() method.
    The list can be managed by using the NacApps.add() and NacApps.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "nacApps"
    _SDM_ATT_MAP = {
        "Name": "name",
        "ObjectId": "objectId",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(NacApps, self).__init__(parent, list_op)

    @property
    def Name(self):
        # type: () -> str
        """
        Returns
        -------
        - str: AppCode Name.
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
    def Value(self):
        # type: () -> int
        """
        Returns
        -------
        - number: AppCode ID.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Name=None, Value=None):
        # type: (str, int) -> NacApps
        """Updates nacApps resource on the server.

        Args
        ----
        - Name (str): AppCode Name.
        - Value (number): AppCode ID.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Name=None, Value=None):
        # type: (str, int) -> NacApps
        """Adds a new nacApps resource on the server and adds it to the container.

        Args
        ----
        - Name (str): AppCode Name.
        - Value (number): AppCode ID.

        Returns
        -------
        - self: This instance with all currently retrieved nacApps resources using find and the newly added nacApps resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained nacApps resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Name=None, ObjectId=None, Value=None):
        # type: (str, str, int) -> NacApps
        """Finds and retrieves nacApps resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve nacApps resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all nacApps resources from the server.

        Args
        ----
        - Name (str): AppCode Name.
        - ObjectId (str): Unique identifier for this object
        - Value (number): AppCode ID.

        Returns
        -------
        - self: This instance with matching nacApps resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of nacApps data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the nacApps resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
