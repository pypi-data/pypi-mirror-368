
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Hex(Base):
    """This specifies the hexadecimal properties related to the parameter.
    The Hex class encapsulates a list of hex resources that are managed by the system.
    A list of resources can be retrieved from the server using the Hex.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "hex"
    _SDM_ATT_MAP = {
        "Default": "default",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Hex, self).__init__(parent, list_op)

    @property
    def Default(self):
        # type: () -> str
        """
        Returns
        -------
        - str: (Read only) Parameter default value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Default"])

    @property
    def Value(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Parameter hex value.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Value=None):
        # type: (str) -> Hex
        """Updates hex resource on the server.

        Args
        ----
        - Value (str): Parameter hex value.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Value=None):
        # type: (str) -> Hex
        """Adds a new hex resource on the json, only valid with batch add utility

        Args
        ----
        - Value (str): Parameter hex value.

        Returns
        -------
        - self: This instance with all currently retrieved hex resources using find and the newly added hex resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Default=None, Value=None):
        # type: (str, str) -> Hex
        """Finds and retrieves hex resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve hex resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all hex resources from the server.

        Args
        ----
        - Default (str): (Read only) Parameter default value.
        - Value (str): Parameter hex value.

        Returns
        -------
        - self: This instance with matching hex resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of hex data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the hex resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
