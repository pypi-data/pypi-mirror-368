
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Qbv(Base):
    """
    The Qbv class encapsulates a required qbv resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "qbv"
    _SDM_ATT_MAP = {
        "IsQbvEnabled": "isQbvEnabled",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Qbv, self).__init__(parent, list_op)

    @property
    def RxGateControlList(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.qbv.rxgatecontrollist.rxgatecontrollist.RxGateControlList): An instance of the RxGateControlList class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.vport.l1config.qbv.rxgatecontrollist.rxgatecontrollist import (
            RxGateControlList,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("RxGateControlList", None) is not None:
                return self._properties.get("RxGateControlList")
        return RxGateControlList(self)

    @property
    def IsQbvEnabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Enables Gate Control List configurations to be used for IEEE 802.1Qbv Traffic Shaping.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsQbvEnabled"])

    @IsQbvEnabled.setter
    def IsQbvEnabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsQbvEnabled"], value)

    def update(self, IsQbvEnabled=None):
        # type: (bool) -> Qbv
        """Updates qbv resource on the server.

        Args
        ----
        - IsQbvEnabled (bool): Enables Gate Control List configurations to be used for IEEE 802.1Qbv Traffic Shaping.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, IsQbvEnabled=None):
        # type: (bool) -> Qbv
        """Finds and retrieves qbv resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve qbv resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all qbv resources from the server.

        Args
        ----
        - IsQbvEnabled (bool): Enables Gate Control List configurations to be used for IEEE 802.1Qbv Traffic Shaping.

        Returns
        -------
        - self: This instance with matching qbv resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of qbv data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the qbv resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
