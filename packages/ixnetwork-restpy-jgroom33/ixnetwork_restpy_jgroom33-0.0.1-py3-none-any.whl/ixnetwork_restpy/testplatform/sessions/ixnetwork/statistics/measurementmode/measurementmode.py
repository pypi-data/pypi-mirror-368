
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class MeasurementMode(Base):
    """Signifies the measurement mode.
    The MeasurementMode class encapsulates a required measurementMode resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "measurementMode"
    _SDM_ATT_MAP = {
        "MeasurementMode": "measurementMode",
    }
    _SDM_ENUM_MAP = {
        "measurementMode": ["cumulativeMode", "instantaneousMode", "mixedMode"],
    }

    def __init__(self, parent, list_op=False):
        super(MeasurementMode, self).__init__(parent, list_op)

    @property
    def MeasurementMode(self):
        # type: () -> str
        """
        Returns
        -------
        - str(cumulativeMode | instantaneousMode | mixedMode): Mode of the measurement: mixed, instantaneous, cumulative
        """
        return self._get_attribute(self._SDM_ATT_MAP["MeasurementMode"])

    @MeasurementMode.setter
    def MeasurementMode(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["MeasurementMode"], value)

    def update(self, MeasurementMode=None):
        # type: (str) -> MeasurementMode
        """Updates measurementMode resource on the server.

        Args
        ----
        - MeasurementMode (str(cumulativeMode | instantaneousMode | mixedMode)): Mode of the measurement: mixed, instantaneous, cumulative

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, MeasurementMode=None):
        # type: (str) -> MeasurementMode
        """Finds and retrieves measurementMode resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve measurementMode resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all measurementMode resources from the server.

        Args
        ----
        - MeasurementMode (str(cumulativeMode | instantaneousMode | mixedMode)): Mode of the measurement: mixed, instantaneous, cumulative

        Returns
        -------
        - self: This instance with matching measurementMode resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of measurementMode data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the measurementMode resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
