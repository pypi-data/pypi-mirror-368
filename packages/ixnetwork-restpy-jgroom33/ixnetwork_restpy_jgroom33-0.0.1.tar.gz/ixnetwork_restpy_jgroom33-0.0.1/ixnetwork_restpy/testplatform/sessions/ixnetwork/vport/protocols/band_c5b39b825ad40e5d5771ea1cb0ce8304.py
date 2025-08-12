
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Band(Base):
    """Bands indicate a list of rate bands. It can contain any number of bands, and each band type can be repeated when it make sense. Only a single band is used at a time. If the current rate of packets exceed the rate of multiple bands, the band with the highest configured rate is used
    The Band class encapsulates a list of band resources that are managed by the user.
    A list of resources can be retrieved from the server using the Band.find() method.
    The list can be managed by using the Band.add() and Band.remove() methods.
    """

    __slots__ = ()
    _SDM_NAME = "band"
    _SDM_ATT_MAP = {
        "BurstSize": "burstSize",
        "Description": "description",
        "Experimenter": "experimenter",
        "PrecedenceLevel": "precedenceLevel",
        "Rate": "rate",
        "Type": "type",
    }
    _SDM_ENUM_MAP = {
        "type": ["drop", "dscpRemark", "experimenter"],
    }

    def __init__(self, parent, list_op=False):
        super(Band, self).__init__(parent, list_op)

    @property
    def BurstSize(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This indicates the length of the packet or byte burst to consider for applying the meter. The default value is 1.
        """
        return self._get_attribute(self._SDM_ATT_MAP["BurstSize"])

    @BurstSize.setter
    def BurstSize(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["BurstSize"], value)

    @property
    def Description(self):
        # type: () -> str
        """
        Returns
        -------
        - str: A description of the band.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Description"])

    @Description.setter
    def Description(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Description"], value)

    @property
    def Experimenter(self):
        # type: () -> int
        """
        Returns
        -------
        - number: The experimenter ID. The default value is 1.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Experimenter"])

    @Experimenter.setter
    def Experimenter(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Experimenter"], value)

    @property
    def PrecedenceLevel(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This indicates the amount by which the drop precedence of the packet should be increased if the band is exceeded. The default value is 0.
        """
        return self._get_attribute(self._SDM_ATT_MAP["PrecedenceLevel"])

    @PrecedenceLevel.setter
    def PrecedenceLevel(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["PrecedenceLevel"], value)

    @property
    def Rate(self):
        # type: () -> int
        """
        Returns
        -------
        - number: This indicates the rate value above which the corresponding band may apply to packets The default value is 1.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Rate"])

    @Rate.setter
    def Rate(self, value):
        # type: (int) -> None
        self._set_attribute(self._SDM_ATT_MAP["Rate"], value)

    @property
    def Type(self):
        # type: () -> str
        """
        Returns
        -------
        - str(drop | dscpRemark | experimenter): Select the band type from the list.
        """
        return self._get_attribute(self._SDM_ATT_MAP["Type"])

    @Type.setter
    def Type(self, value):
        # type: (str) -> None
        self._set_attribute(self._SDM_ATT_MAP["Type"], value)

    def update(
        self,
        BurstSize=None,
        Description=None,
        Experimenter=None,
        PrecedenceLevel=None,
        Rate=None,
        Type=None,
    ):
        # type: (int, str, int, int, int, str) -> Band
        """Updates band resource on the server.

        Args
        ----
        - BurstSize (number): This indicates the length of the packet or byte burst to consider for applying the meter. The default value is 1.
        - Description (str): A description of the band.
        - Experimenter (number): The experimenter ID. The default value is 1.
        - PrecedenceLevel (number): This indicates the amount by which the drop precedence of the packet should be increased if the band is exceeded. The default value is 0.
        - Rate (number): This indicates the rate value above which the corresponding band may apply to packets The default value is 1.
        - Type (str(drop | dscpRemark | experimenter)): Select the band type from the list.

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def add(
        self,
        BurstSize=None,
        Description=None,
        Experimenter=None,
        PrecedenceLevel=None,
        Rate=None,
        Type=None,
    ):
        # type: (int, str, int, int, int, str) -> Band
        """Adds a new band resource on the server and adds it to the container.

        Args
        ----
        - BurstSize (number): This indicates the length of the packet or byte burst to consider for applying the meter. The default value is 1.
        - Description (str): A description of the band.
        - Experimenter (number): The experimenter ID. The default value is 1.
        - PrecedenceLevel (number): This indicates the amount by which the drop precedence of the packet should be increased if the band is exceeded. The default value is 0.
        - Rate (number): This indicates the rate value above which the corresponding band may apply to packets The default value is 1.
        - Type (str(drop | dscpRemark | experimenter)): Select the band type from the list.

        Returns
        -------
        - self: This instance with all currently retrieved band resources using find and the newly added band resources available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._create(self._map_locals(self._SDM_ATT_MAP, locals()))

    def remove(self):
        """Deletes all the contained band resources in this instance from the server.

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        self._delete()

    def find(
        self,
        BurstSize=None,
        Description=None,
        Experimenter=None,
        PrecedenceLevel=None,
        Rate=None,
        Type=None,
    ):
        # type: (int, str, int, int, int, str) -> Band
        """Finds and retrieves band resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve band resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all band resources from the server.

        Args
        ----
        - BurstSize (number): This indicates the length of the packet or byte burst to consider for applying the meter. The default value is 1.
        - Description (str): A description of the band.
        - Experimenter (number): The experimenter ID. The default value is 1.
        - PrecedenceLevel (number): This indicates the amount by which the drop precedence of the packet should be increased if the band is exceeded. The default value is 0.
        - Rate (number): This indicates the rate value above which the corresponding band may apply to packets The default value is 1.
        - Type (str(drop | dscpRemark | experimenter)): Select the band type from the list.

        Returns
        -------
        - self: This instance with matching band resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of band data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the band resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
