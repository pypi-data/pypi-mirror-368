
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class WriteSetFieldLearnedInfo(Base):
    """NOT DEFINED
    The WriteSetFieldLearnedInfo class encapsulates a list of writeSetFieldLearnedInfo resources that are managed by the system.
    A list of resources can be retrieved from the server using the WriteSetFieldLearnedInfo.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "writeSetFieldLearnedInfo"
    _SDM_ATT_MAP = {
        "NextTableIds": "nextTableIds",
        "Property": "property",
        "SupportedField": "supportedField",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(WriteSetFieldLearnedInfo, self).__init__(parent, list_op)

    @property
    def NextTableIds(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["NextTableIds"])

    @property
    def Property(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["Property"])

    @property
    def SupportedField(self):
        # type: () -> str
        """
        Returns
        -------
        - str: NOT DEFINED
        """
        return self._get_attribute(self._SDM_ATT_MAP["SupportedField"])

    def add(self):
        """Adds a new writeSetFieldLearnedInfo resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved writeSetFieldLearnedInfo resources using find and the newly added writeSetFieldLearnedInfo resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, NextTableIds=None, Property=None, SupportedField=None):
        # type: (str, str, str) -> WriteSetFieldLearnedInfo
        """Finds and retrieves writeSetFieldLearnedInfo resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve writeSetFieldLearnedInfo resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all writeSetFieldLearnedInfo resources from the server.

        Args
        ----
        - NextTableIds (str): NOT DEFINED
        - Property (str): NOT DEFINED
        - SupportedField (str): NOT DEFINED

        Returns
        -------
        - self: This instance with matching writeSetFieldLearnedInfo resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of writeSetFieldLearnedInfo data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the writeSetFieldLearnedInfo resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
