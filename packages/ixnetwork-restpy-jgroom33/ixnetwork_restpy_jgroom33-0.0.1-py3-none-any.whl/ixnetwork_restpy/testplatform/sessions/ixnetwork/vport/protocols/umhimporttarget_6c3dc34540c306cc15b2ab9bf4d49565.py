
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class UmhImportTarget(Base):
    """This object represents import RT
    The UmhImportTarget class encapsulates a required umhImportTarget resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "umhImportTarget"
    _SDM_ATT_MAP = {
        "ImportTargetList": "importTargetList",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(UmhImportTarget, self).__init__(parent, list_op)

    @property
    def ImportTargetList(self):
        """
        Returns
        -------
        - list(dict(arg1:str[as | asNumber2 | ip],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str)): Configures import route target in case of UMH routes
        """
        return self._get_attribute(self._SDM_ATT_MAP["ImportTargetList"])

    @ImportTargetList.setter
    def ImportTargetList(self, value):
        self._set_attribute(self._SDM_ATT_MAP["ImportTargetList"], value)

    def update(self, ImportTargetList=None):
        """Updates umhImportTarget resource on the server.

        Args
        ----
        - ImportTargetList (list(dict(arg1:str[as | asNumber2 | ip],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str))): Configures import route target in case of UMH routes

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, ImportTargetList=None):
        """Finds and retrieves umhImportTarget resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve umhImportTarget resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all umhImportTarget resources from the server.

        Args
        ----
        - ImportTargetList (list(dict(arg1:str[as | asNumber2 | ip],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str))): Configures import route target in case of UMH routes

        Returns
        -------
        - self: This instance with matching umhImportTarget resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of umhImportTarget data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the umhImportTarget resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
