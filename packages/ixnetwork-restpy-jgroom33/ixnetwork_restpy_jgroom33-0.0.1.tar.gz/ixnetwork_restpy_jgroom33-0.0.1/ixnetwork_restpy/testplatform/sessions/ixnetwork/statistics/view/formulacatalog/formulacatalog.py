
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class FormulaCatalog(Base):
    """This object holds the catalog information for the various statistical

    formula.
        The FormulaCatalog class encapsulates a required formulaCatalog resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "formulaCatalog"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(FormulaCatalog, self).__init__(parent, list_op)

    @property
    def FormulaColumn(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.view.formulacatalog.formulacolumn.formulacolumn.FormulaColumn): An instance of the FormulaColumn class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.statistics.view.formulacatalog.formulacolumn.formulacolumn import (
            FormulaColumn,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("FormulaColumn", None) is not None:
                return self._properties.get("FormulaColumn")
        return FormulaColumn(self)

    def find(self):
        """Finds and retrieves formulaCatalog resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve formulaCatalog resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all formulaCatalog resources from the server.

        Returns
        -------
        - self: This instance with matching formulaCatalog resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of formulaCatalog data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the formulaCatalog resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
