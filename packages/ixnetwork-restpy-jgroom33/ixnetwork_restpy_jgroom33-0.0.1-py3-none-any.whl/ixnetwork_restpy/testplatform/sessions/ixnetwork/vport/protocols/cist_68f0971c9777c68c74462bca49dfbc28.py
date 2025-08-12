
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Cist(Base):
    """This object holds a list of the CIST learned information and learned interfaces.
    The Cist class encapsulates a required cist resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "cist"
    _SDM_ATT_MAP = {}
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Cist, self).__init__(parent, list_op)

    @property
    def CistLearnedInfo(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.cistlearnedinfo_ab0130170187b84c756a225eddf532d7.CistLearnedInfo): An instance of the CistLearnedInfo class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.cistlearnedinfo_ab0130170187b84c756a225eddf532d7 import (
            CistLearnedInfo,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("CistLearnedInfo", None) is not None:
                return self._properties.get("CistLearnedInfo")
        return CistLearnedInfo(self)._select()

    @property
    def LearnedInterface(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.learnedinterface_624758fed3751b10c746ab8fdb7d7f56.LearnedInterface): An instance of the LearnedInterface class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.protocols.learnedinterface_624758fed3751b10c746ab8fdb7d7f56 import (
            LearnedInterface,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("LearnedInterface", None) is not None:
                return self._properties.get("LearnedInterface")
        return LearnedInterface(self)

    def find(self):
        """Finds and retrieves cist resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve cist resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all cist resources from the server.

        Returns
        -------
        - self: This instance with matching cist resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of cist data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the cist resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
