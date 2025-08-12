
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class UserLsaGroup(Base):
    """This object configures a user LSA group for use in OSPF.
    The UserLsaGroup class encapsulates a list of userLsaGroup resources that are managed by the user.
    A list of resources can be retrieved from the server using the UserLsaGroup.find() method.
    The list can be managed by using the UserLsaGroup.add() and UserLsaGroup.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "userLsaGroup"
    _SDM_ATT_MAP = {
        "AreaId": "areaId",
        "Description": "description",
        "Enabled": "enabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(UserLsaGroup, self).__init__(parent, list_op)

    @property
    def UserLsa(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.userlsa_6ef084d0dede50140d3cd2a284051b56.UserLsa): An instance of the UserLsa class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.userlsa_6ef084d0dede50140d3cd2a284051b56 import (
            UserLsa,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("UserLsa", None) is not None:
                return self._properties.get("UserLsa")
        return UserLsa(self)

    @property
    def AreaId(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The area ID for the LSA group. (default = 0)
        """
        return self._get_attribute(self._SDM_ATT_MAP["AreaId"])

    @AreaId.setter
    def AreaId(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["AreaId"], value)

    @property
    def Description(self):
        # type: () -> str
        """
        Returns
        -------
        - str: A commentary description for the user LSA group.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Description"])

    @Description.setter
    def Description(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Description"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Enables the use of this router in the simulated OSPF network.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    def update(self, AreaId=None, Description=None, Enabled=None):
        # type: (int, str, bool) -> UserLsaGroup
        """Updates userLsaGroup resource on the server.

        Args
        ----
        - AreaId (number): The area ID for the LSA group. (default = 0)
        - Description (str): A commentary description for the user LSA group.
        - Enabled (bool): Enables the use of this router in the simulated OSPF network.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(self, AreaId=None, Description=None, Enabled=None):
        # type: (int, str, bool) -> UserLsaGroup
        """Adds a new userLsaGroup resource on the server and adds it to the container.

        Args
        ----
        - AreaId (number): The area ID for the LSA group. (default = 0)
        - Description (str): A commentary description for the user LSA group.
        - Enabled (bool): Enables the use of this router in the simulated OSPF network.

        Returns
        -------
        - self: This instance with all currently retrieved userLsaGroup resources using find and the newly added userLsaGroup resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained userLsaGroup resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, AreaId=None, Description=None, Enabled=None):
        # type: (int, str, bool) -> UserLsaGroup
        """Finds and retrieves userLsaGroup resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve userLsaGroup resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all userLsaGroup resources from the server.

        Args
        ----
        - AreaId (number): The area ID for the LSA group. (default = 0)
        - Description (str): A commentary description for the user LSA group.
        - Enabled (bool): Enables the use of this router in the simulated OSPF network.

        Returns
        -------
        - self: This instance with matching userLsaGroup resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of userLsaGroup data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the userLsaGroup resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
