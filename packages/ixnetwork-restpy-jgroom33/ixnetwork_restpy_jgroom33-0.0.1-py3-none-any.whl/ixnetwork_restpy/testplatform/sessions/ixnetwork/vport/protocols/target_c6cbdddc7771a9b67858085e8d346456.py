
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Target(Base):
    """This object controls the configuration of L3 Site targets.
    The Target class encapsulates a required target resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "target"
    _SDM_ATT_MAP = {
        "TargetList": "targetList",
        "TargetListEx": "targetListEx",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Target, self).__init__(parent, list_op)

    @property
    def TargetList(self):
        """DEPRECATED
        Returns
        -------
        - list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number)): Configures a target attribute to be associated with advertised L3 VPN route ranges.
        """
        return self._get_attribute(self._SDM_ATT_MAP["TargetList"])

    @TargetList.setter
    def TargetList(self, value):
        self._set_attribute(self._SDM_ATT_MAP["TargetList"], value)

    @property
    def TargetListEx(self):
        """
        Returns
        -------
        - list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str)): Configures a list of export targets to be associated with advertised L3 VPN route ranges.
        """
        return self._get_attribute(self._SDM_ATT_MAP["TargetListEx"])

    @TargetListEx.setter
    def TargetListEx(self, value):
        self._set_attribute(self._SDM_ATT_MAP["TargetListEx"], value)

    def update(self, TargetList=None, TargetListEx=None):
        """Updates target resource on the server.

        Args
        ----
        - TargetList (list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number))): Configures a target attribute to be associated with advertised L3 VPN route ranges.
        - TargetListEx (list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str))): Configures a list of export targets to be associated with advertised L3 VPN route ranges.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, TargetList=None, TargetListEx=None):
        """Finds and retrieves target resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve target resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all target resources from the server.

        Args
        ----
        - TargetList (list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number))): Configures a target attribute to be associated with advertised L3 VPN route ranges.
        - TargetListEx (list(dict(arg1:str[as | ip | asNumber2],arg2:number,arg3:str,arg4:number,arg5:number,arg6:number,arg7:str))): Configures a list of export targets to be associated with advertised L3 VPN route ranges.

        Returns
        -------
        - self: This instance with matching target resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of target data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the target resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
