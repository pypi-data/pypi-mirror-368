from jpegdata.logging import logger
from jpegdata.structures.file.base import Element
from jpegdata.structures.offset import Offset
from jpegdata.enumerations.marker import Marker

logger = logger.getChild(__name__)


class Segment(Element):
    """The Segment class represents a data segment within the JPEG file."""

    _marker: Marker = None
    _data: bytes = None

    def __init__(
        self,
        marker: Marker,
        length: int = 0,
        offset: Offset | int = 0,
        data: bytes | bytearray = None,
    ):
        super().__init__(length=length, offset=offset, data=data)

        if not isinstance(marker, Marker):
            raise TypeError(
                "The 'marker' argument must reference a Marker enumeration option!"
            )

        self._marker = marker

    def __str__(self) -> str:
        return f"<Segment({self.marker.name})>"

    @property
    def marker(self) -> Marker:
        return self._marker
