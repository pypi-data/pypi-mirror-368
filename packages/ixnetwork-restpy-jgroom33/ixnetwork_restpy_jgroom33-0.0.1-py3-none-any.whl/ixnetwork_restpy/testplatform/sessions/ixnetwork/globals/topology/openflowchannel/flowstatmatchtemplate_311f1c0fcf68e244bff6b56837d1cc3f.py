
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FlowStatMatchTemplate(Base):
    """Global data for OFMatch template data extension.
    The FlowStatMatchTemplate class encapsulates a required flowStatMatchTemplate resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "flowStatMatchTemplate"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(FlowStatMatchTemplate, self).__init__(parent, list_op)

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

    @property
    def Predefined(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.predefined_6b976ae27edbd8634592ab8d68c01286.Predefined): An instance of the Predefined class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.topology.openflowchannel.predefined_6b976ae27edbd8634592ab8d68c01286 import (
            Predefined,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Predefined", None) is not None:
                return self._properties.get("Predefined")
        return Predefined(self)

    def find(self):
        """Finds and retrieves flowStatMatchTemplate resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve flowStatMatchTemplate resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all flowStatMatchTemplate resources from the server.

        Returns
        -------
        - self: This instance with matching flowStatMatchTemplate resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of flowStatMatchTemplate data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the flowStatMatchTemplate resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
