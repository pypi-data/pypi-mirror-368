
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class LearnedSgState(Base):
    """The number of Source Groups for which information has been learned.
    The LearnedSgState class encapsulates a list of learnedSgState resources that are managed by the system.
    A list of resources can be retrieved from the server using the LearnedSgState.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "learnedSgState"
    _SDM_ATT_MAP = {
        "Group": "group",
        "Source": "source",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(LearnedSgState, self).__init__(parent, list_op)

    @property
    def Group(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The first IPv4 multicast group address in the range of group addresses included in the Register message. (default = 255.0.0.0)
        """
        return self._get_attribute(self._SDM_ATT_MAP["Group"])

    @property
    def Source(self):
        # type: () -> str
        """
        Returns
        -------
        - str: The first source address to be included in the Register messages. (default = 0.0.0.1)
        """
        return self._get_attribute(self._SDM_ATT_MAP["Source"])

    def add(self):
        """Adds a new learnedSgState resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved learnedSgState resources using find and the newly added learnedSgState resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, Group=None, Source=None):
        # type: (str, str) -> LearnedSgState
        """Finds and retrieves learnedSgState resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve learnedSgState resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all learnedSgState resources from the server.

        Args
        ----
        - Group (str): The first IPv4 multicast group address in the range of group addresses included in the Register message. (default = 255.0.0.0)
        - Source (str): The first source address to be included in the Register messages. (default = 0.0.0.1)

        Returns
        -------
        - self: This instance with matching learnedSgState resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of learnedSgState data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the learnedSgState resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
