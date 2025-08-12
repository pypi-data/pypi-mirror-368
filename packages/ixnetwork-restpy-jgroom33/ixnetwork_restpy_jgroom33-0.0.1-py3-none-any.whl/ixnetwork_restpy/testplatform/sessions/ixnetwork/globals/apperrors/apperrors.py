
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class AppErrors(Base):
    """This node holds application errors.
    The AppErrors class encapsulates a list of appErrors resources that are managed by the system.
    A list of resources can be retrieved from the server using the AppErrors.find() method.
    """

    __slots__ = ()
    _SDM_NAME = "appErrors"
    _SDM_ATT_MAP = {
        "ErrorCount": "errorCount",
        "LastModified": "lastModified",
        "WarningCount": "warningCount",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(AppErrors, self).__init__(parent, list_op)

    @property
    def Error(self):
        """
        Returns
        -------
        - obj(ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.apperrors.error.error.Error): An instance of the Error class

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        from ixnetwork_restpy.testplatform.sessions.ixnetwork.globals.apperrors.error.error import (
            Error,
        )

        if len(self._object_properties) > 0:
            if self._properties.get("Error", None) is not None:
                return self._properties.get("Error")
        return Error(self)

    @property
    def ErrorCount(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Total number of errors
        """
        return self._get_attribute(self._SDM_ATT_MAP["ErrorCount"])

    @property
    def LastModified(self):
        # type: () -> str
        """
        Returns
        -------
        - str: Time of latest logged error or warning
        """
        return self._get_attribute(self._SDM_ATT_MAP["LastModified"])

    @property
    def WarningCount(self):
        # type: () -> int
        """
        Returns
        -------
        - number: Total number of warnings
        """
        return self._get_attribute(self._SDM_ATT_MAP["WarningCount"])

    def add(self):
        """Adds a new appErrors resource on the json, only valid with batch add utility

        Returns
        -------
        - self: This instance with all currently retrieved appErrors resources using find and the newly added appErrors resources available through an iterator or index

        Raises
        ------
        - Exception: if this function is not being used with config assistance
        """
        return self._add_xpath(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, ErrorCount=None, LastModified=None, WarningCount=None):
        # type: (int, str, int) -> AppErrors
        """Finds and retrieves appErrors resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve appErrors resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all appErrors resources from the server.

        Args
        ----
        - ErrorCount (number): Total number of errors
        - LastModified (str): Time of latest logged error or warning
        - WarningCount (number): Total number of warnings

        Returns
        -------
        - self: This instance with matching appErrors resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of appErrors data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the appErrors resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
