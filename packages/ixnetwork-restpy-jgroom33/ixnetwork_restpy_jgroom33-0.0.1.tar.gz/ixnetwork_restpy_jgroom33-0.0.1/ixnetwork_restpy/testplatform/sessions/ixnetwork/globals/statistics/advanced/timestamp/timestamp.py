
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Timestamp(Base):
    """This node contains Timestamp settings.
    The Timestamp class encapsulates a required timestamp resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "timestamp"
    _SDM_ATT_MAP = {
        "TimestampPrecision": "timestampPrecision",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Timestamp, self).__init__(parent, list_op)

    @property
    def TimestampPrecision(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The timestamp precision allows you to change the timestamp precision from microseconds to nanoseconds for specific StatViewer statistics and features. The timestamp precision can be set to have the statistics display values with decimals ranging from 0 to 9.
        """
        return self._get_attribute(self._SDM_ATT_MAP["TimestampPrecision"])

    @TimestampPrecision.setter
    def TimestampPrecision(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["TimestampPrecision"], value)

    def update(self, TimestampPrecision=None):
        # type: (int) -> Timestamp
        """Updates timestamp resource on the server.

        Args
        ----
        - TimestampPrecision (number): The timestamp precision allows you to change the timestamp precision from microseconds to nanoseconds for specific StatViewer statistics and features. The timestamp precision can be set to have the statistics display values with decimals ranging from 0 to 9.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, TimestampPrecision=None):
        # type: (int) -> Timestamp
        """Finds and retrieves timestamp resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve timestamp resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all timestamp resources from the server.

        Args
        ----
        - TimestampPrecision (number): The timestamp precision allows you to change the timestamp precision from microseconds to nanoseconds for specific StatViewer statistics and features. The timestamp precision can be set to have the statistics display values with decimals ranging from 0 to 9.

        Returns
        -------
        - self: This instance with matching timestamp resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of timestamp data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the timestamp resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
