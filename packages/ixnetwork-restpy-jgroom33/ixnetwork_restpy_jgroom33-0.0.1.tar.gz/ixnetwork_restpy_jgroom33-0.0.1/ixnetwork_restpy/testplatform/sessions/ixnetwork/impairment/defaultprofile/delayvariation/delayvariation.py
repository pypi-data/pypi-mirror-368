
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class DelayVariation(Base):
    """Randomly vary packet delay.  Can only be used on a profile with delay enabled.
    The DelayVariation class encapsulates a required delayVariation resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "delayVariation"
    _SDM_ATT_MAP = {
        "Distribution": "distribution",
        "Enabled": "enabled",
        "ExponentialMeanArrival": "exponentialMeanArrival",
        "GaussianStandardDeviation": "gaussianStandardDeviation",
        "UniformSpread": "uniformSpread",
        "Units": "units",
    }
    _SDM_ENUM_MAP = {
        "distribution": [
            "exponential",
            "gaussian",
            "kExponential",
            "kGaussian",
            "kUniform",
            "uniform",
        ],
        "units": [
            "kilometers",
            "kKilometers",
            "kMicroseconds",
            "kMilliseconds",
            "kSeconds",
            "microseconds",
            "milliseconds",
            "seconds",
        ],
    }

    def __init__(self, parent, list_op=False):
        super(DelayVariation, self).__init__(parent, list_op)

    @property
    def Distribution(self):
        # type: () -> str
        """
        Returns
        -------
        - str(exponential | gaussian | kExponential | kGaussian | kUniform | uniform): Specify the distribution of the random variation.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Distribution"])

    @Distribution.setter
    def Distribution(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Distribution"], value)

    @property
    def Enabled(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: If true, randomly vary the packet delay.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Enabled"])

    @Enabled.setter
    def Enabled(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["Enabled"], value)

    @property
    def ExponentialMeanArrival(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Mean arrival time for the exponential distribution.
        """
        return self._get_attribute(self._SDM_ATT_MAP["ExponentialMeanArrival"])

    @ExponentialMeanArrival.setter
    def ExponentialMeanArrival(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["ExponentialMeanArrival"], value)

    @property
    def GaussianStandardDeviation(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Standard deviation for the Gaussian distribution.
        """
        return self._get_attribute(self._SDM_ATT_MAP["GaussianStandardDeviation"])

    @GaussianStandardDeviation.setter
    def GaussianStandardDeviation(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["GaussianStandardDeviation"], value)

    @property
    def UniformSpread(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Spread for the uniform distribution.
        """
        return self._get_attribute(self._SDM_ATT_MAP["UniformSpread"])

    @UniformSpread.setter
    def UniformSpread(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["UniformSpread"], value)

    @property
    def Units(self):
        # type: () -> str
        """
        Returns
        -------
        - str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds): Specify the units for the value of the spread, standard deviation, or mean arrival time.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Units"])

    @Units.setter
    def Units(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Units"], value)

    def update(
        self,
        Distribution=None,
        Enabled=None,
        ExponentialMeanArrival=None,
        GaussianStandardDeviation=None,
        UniformSpread=None,
        Units=None,
    ):
        # type: (str, bool, int, int, int, str) -> DelayVariation
        """Updates delayVariation resource on the server.

        Args
        ----
        - Distribution (str(exponential | gaussian | kExponential | kGaussian | kUniform | uniform)): Specify the distribution of the random variation.
        - Enabled (bool): If true, randomly vary the packet delay.
        - ExponentialMeanArrival (number): Mean arrival time for the exponential distribution.
        - GaussianStandardDeviation (number): Standard deviation for the Gaussian distribution.
        - UniformSpread (number): Spread for the uniform distribution.
        - Units (str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds)): Specify the units for the value of the spread, standard deviation, or mean arrival time.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(
        self,
        Distribution=None,
        Enabled=None,
        ExponentialMeanArrival=None,
        GaussianStandardDeviation=None,
        UniformSpread=None,
        Units=None,
    ):
        # type: (str, bool, int, int, int, str) -> DelayVariation
        """Finds and retrieves delayVariation resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve delayVariation resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all delayVariation resources from the server.

        Args
        ----
        - Distribution (str(exponential | gaussian | kExponential | kGaussian | kUniform | uniform)): Specify the distribution of the random variation.
        - Enabled (bool): If true, randomly vary the packet delay.
        - ExponentialMeanArrival (number): Mean arrival time for the exponential distribution.
        - GaussianStandardDeviation (number): Standard deviation for the Gaussian distribution.
        - UniformSpread (number): Spread for the uniform distribution.
        - Units (str(kilometers | kKilometers | kMicroseconds | kMilliseconds | kSeconds | microseconds | milliseconds | seconds)): Specify the units for the value of the spread, standard deviation, or mean arrival time.

        Returns
        -------
        - self: This instance with matching delayVariation resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of delayVariation data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the delayVariation resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
