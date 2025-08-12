
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class RxFilters(Base):
    """This object defines the parameters for the Rx Filters.
    The RxFilters class encapsulates a required rxFilters resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "rxFilters"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(RxFilters, self).__init__(parent, list_op)

    @property
    def FilterPalette(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.rxfilters.filterpalette.filterpalette.FilterPalette): An instance of the FilterPalette class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.rxfilters.filterpalette.filterpalette import (
            FilterPalette,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("FilterPalette", None) is not None:
                return self._properties.get("FilterPalette")
        return FilterPalette(self)._select()

    @property
    def Uds(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.rxfilters.uds.uds.Uds): An instance of the Uds class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.rxfilters.uds.uds import (
            Uds,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Uds", None) is not None:
                return self._properties.get("Uds")
        return Uds(self)

    def find(self):
        """Finds and retrieves rxFilters resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve rxFilters resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all rxFilters resources from the server.

        Returns
        -------
        - self: This instance with matching rxFilters resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of rxFilters data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the rxFilters resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
