from jpegdata.logging import logger
from jpegdata.structures.offset import Offset

logger = logger.getChild(__name__)


class Element(object):
    """The Element class provides base functionality for the JPEG structure subclasses."""

    _length: int = None
    _offset: Offset = None
    _data: bytes = None
    _label: str = None

    def __init__(
        self,
        length: int = 0,
        offset: Offset | int = 0,
        data: bytes = None,
        label: str = None,
    ):
        self.length = length
        self.offset = offset
        self.data = data
        self.label = label

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}({self.label})>"

    @property
    def klass(self) -> str:
        return self.__class__.__name__

    @property
    def label(self) -> str:
        return self._label or "?"

    @label.setter
    def label(self, label: str):
        if label is None:
            self._label = None
        elif isinstance(label, str):
            self._label = label
        else:
            raise TypeError(
                "The 'label' argument, if specified, must have a string value!"
            )

    @property
    def length(self) -> int:
        """Support getting the element's data length."""

        return self._length

    @length.setter
    def length(self, length: int):
        """Support setting the element's data length."""

        if not isinstance(length, int):
            raise TypeError("The 'length' argument must have an integer value!")
        elif not length >= 0:
            raise ValueError(
                "The 'length' argument must have a positive integer value!"
            )
        else:
            self._length = length

    @property
    def offset(self) -> Offset:
        """Support getting the node's source and later target offsets within the file"""

        return self._offset

    @offset.setter
    def offset(self, offset: Offset | int):
        """Support setting the node's source and later target offsets within the file"""

        if isinstance(offset, Offset):
            self._offset = offset
        elif isinstance(offset, int):
            if not offset >= 0:
                raise ValueError(
                    "The 'offset' argument must have a positive integer value!"
                )
            self._offset = Offset(source=offset)
        else:
            raise TypeError(
                "The 'offset' argument must have a positive integer value or reference an Offset class instance!"
            )

    @property
    def data(self) -> bytes | None:
        return self._data

    @data.setter
    def data(self, data: bytes | bytearray):
        if data is None:
            self._data = None
        elif isinstance(data, (bytes, bytearray)):
            self._data = bytes(data)
        else:
            raise TypeError("The 'data' argument must have a bytes or bytearray value!")
