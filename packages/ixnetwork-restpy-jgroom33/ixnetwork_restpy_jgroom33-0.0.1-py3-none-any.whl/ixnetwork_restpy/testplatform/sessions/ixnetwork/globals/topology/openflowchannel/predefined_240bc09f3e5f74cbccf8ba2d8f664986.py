
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Predefined(Base):
    """Default template and profile for Action Builder.
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
    def ActionTemplate(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.actiontemplate_fa40ad00e03788c7e139f3ecbe0f7842.ActionTemplate): An instance of the ActionTemplate class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.actiontemplate_fa40ad00e03788c7e139f3ecbe0f7842 import (
            ActionTemplate,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("ActionTemplate", None) is not None:
                return self._properties.get("ActionTemplate")
        return ActionTemplate(self)

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
