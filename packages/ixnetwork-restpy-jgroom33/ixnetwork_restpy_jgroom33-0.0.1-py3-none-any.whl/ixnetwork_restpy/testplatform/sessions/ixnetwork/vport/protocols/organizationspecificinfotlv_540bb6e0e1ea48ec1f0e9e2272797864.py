
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class OrganizationSpecificInfoTlv(Base):
    """
    The OrganizationSpecificInfoTlv class encapsulates a list of organizationSpecificInfoTlv resources that are managed by the user.
    A list of resources can be retrieved from the server using the OrganizationSpecificInfoTlv.find() method.
    The list can be managed by using the OrganizationSpecificInfoTlv.add() and OrganizationSpecificInfoTlv.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "organizationSpecificInfoTlv"
    _SDM_ATT_MAP = {
        "Enabled": "enabled",
        "Oui": "oui",
        "Value": "value",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(OrganizationSpecificInfoTlv, self).__init__(parent, list_op)

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
    def Oui(self):
        # type: () -> str
        """
        Returns
        -------
        - str:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Oui"])

    @Oui.setter
    def Oui(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Oui"], value)

    @property
    def Value(self):
        # type: () -> str
        """
        Returns
        -------
        - str:
        """
        return self._get_attribute(self._SDM_ATT_MAP["Value"])

    @Value.setter
    def Value(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Value"], value)

    def update(self, Enabled=None, Oui=None, Value=None):
        # type: (bool, str, str) -> OrganizationSpecificInfoTlv
        """Updates organizationSpecificInfoTlv resource on the server.

        Args
        ----
        - Enabled (bool):
        - Oui (str):
        - Value (str):

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, Enabled=None, Oui=None, Value=None):
        # type: (bool, str, str) -> OrganizationSpecificInfoTlv
        """Adds a new organizationSpecificInfoTlv resource on the server and adds it to the container.

        Args
        ----
        - Enabled (bool):
        - Oui (str):
        - Value (str):

        Returns
        -------
        - self: This instance with all currently retrieved organizationSpecificInfoTlv resources using find and the newly added organizationSpecificInfoTlv resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained organizationSpecificInfoTlv resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, Enabled=None, Oui=None, Value=None):
        # type: (bool, str, str) -> OrganizationSpecificInfoTlv
        """Finds and retrieves organizationSpecificInfoTlv resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve organizationSpecificInfoTlv resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all organizationSpecificInfoTlv resources from the server.

        Args
        ----
        - Enabled (bool):
        - Oui (str):
        - Value (str):

        Returns
        -------
        - self: This instance with matching organizationSpecificInfoTlv resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of organizationSpecificInfoTlv data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the organizationSpecificInfoTlv resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
