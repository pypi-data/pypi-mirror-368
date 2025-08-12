
import sys
from ixnetwork_restpy.base import Base
from ixnetwork_restpy.files import Files

if sys.version_info >= (3, 5):
    from typing import List, Any, Union


class Base64CodeOptions(Base):
    """Contains the base64 encoding code generation options
    The Base64CodeOptions class encapsulates a required base64CodeOptions resource which will be retrieved from the server every time the property is accessed.
    """

    __slots__ = ()
    _SDM_NAME = "base64CodeOptions"
    _SDM_ATT_MAP = {
        "IncludeSampleCode": "includeSampleCode",
        "SampleObjectReferences": "sampleObjectReferences",
    }
    _SDM_ENUM_MAP = {}

    def __init__(self, parent, list_op=False):
        super(Base64CodeOptions, self).__init__(parent, list_op)

    @property
    def IncludeSampleCode(self):
        # type: () -> bool
        """
        Returns
        -------
        - bool: Flag to include sample code
        """
        return self._get_attribute(self._SDM_ATT_MAP["IncludeSampleCode"])

    @IncludeSampleCode.setter
    def IncludeSampleCode(self, value):
        # type: (bool) -> None
        self._set_attribute(self._SDM_ATT_MAP["IncludeSampleCode"], value)

    @property
    def SampleObjectReferences(self):
        # type: () -> List[str]
        """
        Returns
        -------
        - list(str[None]): A list of object references used to generate sample code
        """
        return self._get_attribute(self._SDM_ATT_MAP["SampleObjectReferences"])

    @SampleObjectReferences.setter
    def SampleObjectReferences(self, value):
        # type: (List[str]) -> None
        self._set_attribute(self._SDM_ATT_MAP["SampleObjectReferences"], value)

    def update(self, IncludeSampleCode=None, SampleObjectReferences=None):
        # type: (bool, List[str]) -> Base64CodeOptions
        """Updates base64CodeOptions resource on the server.

        Args
        ----
        - IncludeSampleCode (bool): Flag to include sample code
        - SampleObjectReferences (list(str[None])): A list of object references used to generate sample code

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._update(self._map_locals(self._SDM_ATT_MAP, locals()))

    def find(self, IncludeSampleCode=None, SampleObjectReferences=None):
        # type: (bool, List[str]) -> Base64CodeOptions
        """Finds and retrieves base64CodeOptions resources from the server.

        All named parameters are evaluated on the server using regex. The named parameters can be used to selectively retrieve base64CodeOptions resources from the server.
        To retrieve an exact match ensure the parameter value starts with ^ and ends with $
        By default the find method takes no parameters and will retrieve all base64CodeOptions resources from the server.

        Args
        ----
        - IncludeSampleCode (bool): Flag to include sample code
        - SampleObjectReferences (list(str[None])): A list of object references used to generate sample code

        Returns
        -------
        - self: This instance with matching base64CodeOptions resources retrieved from the server available through an iterator or index

        Raises
        ------
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._select(self._map_locals(self._SDM_ATT_MAP, locals()))

    def read(self, href):
        """Retrieves a single instance of base64CodeOptions data from the server.

        Args
        ----
        - href (str): An href to the instance to be retrieved

        Returns
        -------
        - self: This instance with the base64CodeOptions resources from the server available through an iterator or index

        Raises
        ------
        - NotFoundError: The requested resource does not exist on the server
        - ServerError: The server has encountered an uncategorized error condition
        """
        return self._read(href)
