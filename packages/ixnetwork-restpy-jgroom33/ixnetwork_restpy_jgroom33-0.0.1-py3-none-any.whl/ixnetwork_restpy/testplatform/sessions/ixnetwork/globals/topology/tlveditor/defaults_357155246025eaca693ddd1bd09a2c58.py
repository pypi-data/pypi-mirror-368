
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Defaults(Base):
    """Default Tlv template container
    The Defaults class encapsulates a list of defaults resources that are managed by the system.
    A list of resources can be retrieved from the server using the Defaults.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "defaults"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Defaults, self).__init__(parent, list_op)

    @property
    def Template(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.tlveditor.template_251f4228c795442db61593bcbbdf8694.Template): An instance of the Template class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.tlveditor.template_251f4228c795442db61593bcbbdf8694 import (
            Template,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Template", None) is not None:
                return self._properties.get("Template")
        return Template(self)

    def add(self):
        """Adds a new defaults resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved defaults resources using find and the newly added defaults resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self):
        """Finds and retrieves defaults resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve defaults resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all defaults resources from the server.

        Returns
        -------
        - self: This instance with matching defaults resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of defaults data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the defaults resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
