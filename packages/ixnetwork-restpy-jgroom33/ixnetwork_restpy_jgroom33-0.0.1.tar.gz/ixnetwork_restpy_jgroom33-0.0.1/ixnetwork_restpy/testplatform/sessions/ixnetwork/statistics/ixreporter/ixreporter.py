
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Ixreporter(Base):
    """DEPRECATED Root node for IxReporter statistics.
    The Ixreporter class encapsulates a required ixreporter resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "ixreporter"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Ixreporter, self).__init__(parent, list_op)

    @property
    def DataCollection(self):
        """DEPRECATED
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.ixreporter.datacollection.datacollection.DataCollection): An instance of the DataCollection class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.ixreporter.datacollection.datacollection import (
            DataCollection,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("DataCollection", None) is not None:
                return self._properties.get("DataCollection")
        return DataCollection(self)._select()

    @property
    def ReportGeneration(self):
        """DEPRECATED
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.ixreporter.reportgeneration.reportgeneration.ReportGeneration): An instance of the ReportGeneration class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.ixreporter.reportgeneration.reportgeneration import (
            ReportGeneration,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("ReportGeneration", None) is not None:
                return self._properties.get("ReportGeneration")
        return ReportGeneration(self)._select()

    def find(self):
        """Finds and retrieves ixreporter resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve ixreporter resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all ixreporter resources from the server.

        Returns
        -------
        - self: This instance with matching ixreporter resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of ixreporter data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the ixreporter resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
