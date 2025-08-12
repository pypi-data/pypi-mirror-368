
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class QueueProperty(Base):
    """The property of the queue.
    The QueueProperty class encapsulates a required queueProperty resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "queueProperty"
    _SDM_ATT_MAP = {
        "MinimumDataRateGuaranteed": "minimumDataRateGuaranteed",
        "IsNone": "none",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(QueueProperty, self).__init__(parent, list_op)

    @property
    def MinimumDataRateGuaranteed(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, indicates that a minimum data rate is guaranteed.
        """
        return self._get_attribute(self._SDM_ATT_MAP["MinimumDataRateGuaranteed"])

    @MinimumDataRateGuaranteed.setter
    def MinimumDataRateGuaranteed(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["MinimumDataRateGuaranteed"], value)

    @property
    def IsNone(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, indicates that no property is defined for the queue.
        """
        return self._get_attribute(self._SDM_ATT_MAP["IsNone"])

    @IsNone.setter
    def IsNone(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IsNone"], value)

    def update(self, MinimumDataRateGuaranteed=None):
        # type: (bool) -> QueueProperty
        """Updates queueProperty resource on the server.

        Args
        ----
        - MinimumDataRateGuaranteed (bool): If true, indicates that a minimum data rate is guaranteed.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, MinimumDataRateGuaranteed=None, IsNone=None):
        # type: (bool, bool) -> QueueProperty
        """Finds and retrieves queueProperty resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve queueProperty resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all queueProperty resources from the server.

        Args
        ----
        - MinimumDataRateGuaranteed (bool): If true, indicates that a minimum data rate is guaranteed.
        - IsNone (bool): If true, indicates that no property is defined for the queue.

        Returns
        -------
        - self: This instance with matching queueProperty resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of queueProperty data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the queueProperty resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
