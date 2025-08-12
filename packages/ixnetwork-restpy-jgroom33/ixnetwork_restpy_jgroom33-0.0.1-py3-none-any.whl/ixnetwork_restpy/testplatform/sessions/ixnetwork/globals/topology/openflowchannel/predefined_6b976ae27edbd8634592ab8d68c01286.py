
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Predefined(Base):
    """Default template and profile for Flow Match.
    The Predefined class encapsulates a list of predefined resources that are managed by the user.
    A list of resources can be retrieved from the server using the Predefined.find() method.
    The list can be managed by using the Predefined.add() and Predefined.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "predefined"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Predefined, self).__init__(parent, list_op)

    @property
    def MatchTemplate(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.matchtemplate_ee15bafabf192236a3dca22667501f96.MatchTemplate): An instance of the MatchTemplate class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.matchtemplate_ee15bafabf192236a3dca22667501f96 import (
            MatchTemplate,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("MatchTemplate", None) is not None:
                return self._properties.get("MatchTemplate")
        return MatchTemplate(self)

    def add(self):
        """Adds a new predefined resource on the server and adds it to the container.

        Returns
        -------
        - self: This instance with all currently retrieved predefined resources using find and the newly added predefined resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained predefined resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(self):
        """Finds and retrieves predefined resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve predefined resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all predefined resources from the server.

        Returns
        -------
        - self: This instance with matching predefined resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of predefined data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the predefined resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
