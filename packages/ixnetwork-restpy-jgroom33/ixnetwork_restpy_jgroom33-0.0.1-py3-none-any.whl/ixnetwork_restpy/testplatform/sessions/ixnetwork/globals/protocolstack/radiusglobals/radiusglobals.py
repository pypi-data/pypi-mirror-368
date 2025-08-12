
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class RadiusGlobals(Base):
    """Global settings for the RADIUS extension.
    The RadiusGlobals class encapsulates a list of radiusGlobals resources that are managed by the user.
    A list of resources can be retrieved from the server using the RadiusGlobals.find() method.
    The list can be managed by using the RadiusGlobals.add() and RadiusGlobals.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "radiusGlobals"
    _SDM_ATT_MAP = {
        "ObjectId": "objectId",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(RadiusGlobals, self).__init__(parent, list_op)

    @property
    def DhcpOptionSet(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.radiusglobals.dhcpoptionset.dhcpoptionset.DhcpOptionSet): An instance of the DhcpOptionSet class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.protocolstack.radiusglobals.dhcpoptionset.dhcpoptionset import (
            DhcpOptionSet,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("DhcpOptionSet", None) is not None:
                return self._properties.get("DhcpOptionSet")
        return DhcpOptionSet(self)

    @property
    def ObjectId(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Unique identifier for this object
        """
        return self._get_attribute(self._SDM_ATT_MAP["ObjectId"])

    def add(self):
        """Adds a new radiusGlobals resource on the server and adds it to the container.

        Returns
        -------
        - self: This instance with all currently retrieved radiusGlobals resources using find and the newly added radiusGlobals resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained radiusGlobals resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self, ObjectId=None):
        # type: (str) -> RadiusGlobals
        """Finds and retrieves radiusGlobals resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve radiusGlobals resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all radiusGlobals resources from the server.

        Args
        ----
        - ObjectId (str): Unique identifier for this object

        Returns
        -------
        - self: This instance with matching radiusGlobals resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of radiusGlobals data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the radiusGlobals resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
