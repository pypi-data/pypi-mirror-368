from __future__ import annotations

from jpegdata.logging import logger
from jpegdata.exceptions import (
    JPEGDataFileError,
    JPEGDataParseError,
)
from jpegdata.enumerations import (
    Format,
    Encoding,
    Marker,
    State,
)
from jpegdata.structures import (
    Information,
    Segment,
    Offset,
)

from deliciousbytes import ByteOrder, UInt8, UInt16
from deliciousbytes.utilities import hexbytes

from tabulicious import tabulate

import os
import io


__all__ = [
    "JPEG",
    "JFIF",
    "EXIF",
    "JPEGDataFileError",
    "JPEGDataParseError",
    "Format",
    "Encoding",
    "Marker",
    "State",
    "Information",
    "Segment",
    "Offset",
]


class JPEG(object):
    """The JPEG class represents JPEG format files and their raw data."""

    _info: Information = None
    _filepath: str = None
    _filehandle = None
    _order: ByteOrder = ByteOrder.MSB  # All JPEG files are encoded using big-endian
    _format: Format = None
    _encoding: Encoding = None
    _precision: int = None
    _width: int = None
    _height: int = None
    _segments: list[Segment] = None
    _index: int = 0

    def __new__(cls, filepath: str, **kwargs) -> JPEG:
        """Handle creating new instances of the JPEG class, which based on the format of
        the JPEG file, will result in the creation of a JPEG, JFIF or EXIF subclass
        instance. Thiis is achived by parsing the header bytes of the file, from which
        the byte order and file format can be determined; this information is then used
        to determine which JPEG subclass to create an instance of."""

        logger.debug(
            "%s.__new__(cls: %s, filepath: %s, kwargs: %s)",
            cls.__name__,
            cls,
            filepath,
            kwargs,
        )

        if not isinstance(filepath, str):
            raise TypeError("The 'filepath' argument must have a string value!")
        elif not len(filepath := filepath.strip()) > 0:
            raise ValueError("The 'filepath' argument must be a non-empty string!")
        elif not os.path.exists(filepath):
            raise JPEGDataFileError(
                "The 'filepath' argument must reference a file that exists!"
            )
        elif not os.path.isfile(filepath):
            raise JPEGDataFileError(
                "The 'filepath' argument must reference a file, not another filesystem object like a directory!"
            )

        jpegclass: JPEG = cls

        if cls is JPEG:
            # Parse the first few header bytes to determine the JPEG file format
            if isinstance(info := cls._parse_header(filepath, new=True), Information):
                # Based on the format, create the appropriate subclass instance
                if info.format is Format.JPEG:
                    pass
                elif info.format is Format.JFIF:
                    jpegclass = JFIF
                elif info.format is Format.EXIF:
                    jpegclass = EXIF
                else:
                    raise JPEGDataParseError(
                        f"The specified file, '{filepath}', is not a valid JPEG file!"
                    )
            else:
                raise JPEGDataParseError(
                    f"The specified file, '{filepath}', is not a valid JPEG file!"
                )

        return super().__new__(jpegclass)

    def __init__(self, filepath: str, **kwargs):
        """Handle initialising the JPEG class."""

        logger.debug(
            "%s.__init__(self: %s, filepath: %s, kwargs: %s)",
            self.__class__.__name__,
            self,
            filepath,
            kwargs,
        )

        if isinstance(info := self._parse_header(filepath), Information):
            self._info = info
        else:
            raise JPEGDataParseError(
                f"The specified file, '{filepath}', is not a valid JPEG file!"
            )

        self._segments: list[Segment] = []

        self._parse()

    def __del__(self):
        """The __del__() method is called when the current instance is manually deleted
        or when the garbage collector automatically removes it from memory once all the
        references have gone out of scope. We can take advantage of this to do perform
        clean-up, which may not have been performed manually, such as closing files."""

        logger.debug("%s.__del__()", self.__class__.__name__)

        self._close()

    def __enter__(self):
        """Support use of the JPEG class via the 'with' context manager."""

        logger.debug("%s.__enter__()", self.__class__.__name__)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Support use of the JPEG class via the 'with' context manager."""

        logger.debug("%s.__exit__()", self.__class__.__name__)

        self._close()

    def __len__(self) -> int:
        """Support use of the JPEG class as an iterator."""

        return len(self._segments)

    def __iter__(self) -> JPEG:
        """Support use of the JPEG class as an iterator."""

        self._index: int = 0

        return self

    def __next__(self) -> Segment:
        """Support use of the JPEG class as an iterator."""

        if self._index >= len(self._segments):
            raise StopIteration

        segment = self._segments[self._index]

        self._index += 1

        return segment

    @classmethod
    def _parse_header(cls, filepath: str, new: bool = False):
        """Parse the header of the file to determine if it is a valid JPEG image."""

        if not isinstance(filepath, str):
            raise TypeError("The 'filepath' argument must have a string value!")
        elif not os.path.exists(filepath):
            raise ValueError(
                "The 'filepath' argument must reference a file that exists!"
            )

        info = Information()

        with open(filepath, "rb") as handle:
            # Store the file path for reference
            info.filepath = filepath

            # Determine the size of the file
            handle.seek(0, os.SEEK_END)  # Seek to last byte (0) from the end
            info.filesize = handle.tell()  # Record the current position – the file size
            handle.seek(0, os.SEEK_SET)  # Seek to the first byte (0) from the start

            # All JPEG files are encoded using big-endian (MSB first)
            info.order = ByteOrder.MSB

            # Determine the subtype of the provided JPEG file
            if isinstance(header := handle.read(4), bytes) and len(header) == 4:
                # The first two bytes of all JPEG files must be 0xFF 0xD8
                if header[0:2] == bytes([0xFF, 0xD8]):
                    # The next two bytes of JFIF JPEG format files must be 0xFF 0xE0
                    if header[2:4] == bytes([0xFF, 0xE0]):  # JFIF JPEG
                        info.format = Format.JFIF

                    # The next two bytes of EXIF JPEG format files must be 0xFF 0xE1
                    elif header[2:4] == bytes([0xFF, 0xE1]):  # EXIF JPEG
                        info.format = Format.EXIF

                    # The next two bytes of Adobe APP14 format files must be 0xFF 0xEE
                    elif header[2:4] == bytes([0xFF, 0xEE]):
                        info.format = Format.APP14

                    # The next two bytes of DQT format files must be 0xFF 0xEE
                    elif header[2:4] == bytes([0xFF, 0xDB]):
                        info.format = Format.DQT

                    else:
                        raise JPEGDataParseError(
                            f"The provided file, '{filepath}', does not appear to be a valid JPEG file!"
                        )
                # JPEG-2000 files have one of two headers, either 0xFF 0x4F 0xFF 0x51
                elif header == bytes([0xFF, 0x4F, 0xFF, 0x51]):
                    raise JPEGDataParseError(
                        f"The provided file, '{filepath}', is a JPEG-2000 file, which is currently not supported!"
                    )

                # JPEG-2000 files have one of two headers, either 0x00 0x00 0x00 0x0C
                elif header == bytes([0x00, 0x00, 0x00, 0x0C]):
                    if isinstance(extra := handle.read(8), bytes) and len(extra) == 8:
                        if extra == bytes(
                            [0x6A, 0x50, 0x20, 0x20, 0x0D, 0x0A, 0x87, 0x0A]
                        ):
                            raise JPEGDataParseError(
                                f"The provided file, '{filepath}', is a JPEG-2000 file, which is currently not supported!"
                            )
                        else:
                            raise JPEGDataParseError(
                                f"The provided file, '{filepath}', may be a JPEG-2000 file, which is currently not supported!"
                            )
                    else:
                        raise JPEGDataParseError(
                            f"The provided file, '{filepath}', may be a JPEG-2000 file, which is currently not supported!"
                        )
                else:
                    raise JPEGDataParseError(
                        f"The provided file, '{filepath}', does not appear to be a JPEG file of any known type!"
                    )
            else:
                raise JPEGDataParseError(
                    f"The provided file, '{filepath}', does not appear to be a JPEG file of any known type!"
                )

        return info

    def _open(self) -> io.BufferedReader:
        """Open the JPEG file handle."""

        logger.debug(
            "%s._open() filepath => %s",
            self.__class__.__name__,
            self.filepath,
        )

        if not self._filehandle is None:
            return self._filehandle

        self._filehandle = open(self.filepath, "rb")

        return self._filehandle

    def _handle(self) -> io.BufferedReader:
        """Return the JPEG file handle."""

        if self._filehandle is None:
            self._open()

        return self._filehandle

    def _close(self):
        """Close the JPEG file handle."""

        logger.debug(
            "%s._close() filepath => %s" % (self.__class__.__name__, self.filepath),
        )

        if not self._filehandle is None:
            self._filehandle.close()
            self._filehandle = None

    def _parse(self):
        """Parse the provided JPEG file to determine its structure and contents."""

        handle = self._handle()

        handle.seek(0)

        self._parse_segments()

    def _parse_segments(self):
        """Parse the provided JPEG file's marker segments."""

        logger.debug("%s._parse_segments()", self.__class__.__name__)

        handle = self._handle()

        handle.seek(0)

        def _read_marker(offset: int) -> tuple[Marker | None, int]:
            """The read_marker method assists with parsing and reconciling markers."""

            if not handle.seek(offset) == offset:
                raise JPEGDataParseError("Unable to seek to specified file offset!")

            # The first byte of ever marker is 0xFF; as such when the parser encounters
            # cases where this is not so, the data at the current offset may be image
            # or other types of encoded data, rather than JPEG markers, so we return
            if isinstance(data := handle.read(1), bytes) and not data[0] == 0xFF:
                return (None, offset)

            # While the data byte is 0xFF, read the next data byte in the file
            while isinstance(data, bytes) and data[0] == 0xFF:
                data = handle.read(1)
                offset += 1

            if not (marker := Marker.reconcile(data[0])):
                raise JPEGDataParseError(
                    f"Unable to reconcile JPEG marker, {hexbytes(data)}, to a known marker!"
                )

            return (marker, offset + 1)

        encoding: Encoding = None
        precision: int = None
        width: int = None
        height: int = None

        # Start the offset at 2, skipping the SOI marker (0xFF 0xD8) as it has been verified
        offset: int = 0
        length: int = 0
        data: bytes = None

        while offset < self.filesize:
            (marker, offset) = _read_marker(offset)

            if marker is None:
                break

            logger.debug(
                " > offset: %06d; marker => [0xFF 0x%02X] %s (%s)",
                offset,
                marker.value,
                marker,
                marker.label,
            )

            if marker is Marker.EOI:  # 0xD9 EOI (End of Image) marker
                # The End of Image marker indicates there are no more markers to parse
                break
            elif marker is Marker.SOI:  # 0xD8 (Start of Image) marker
                # The Start of Image marker has no data, so we need to skip data parsing
                pass
            else:
                # All other markers should have data, where the next two bytes indicate
                # data length, encoded as a two byte, 16-bit unsigned integer:
                rawlength: bytes = handle.read(2)

                logger.debug(" > length (raw) => %s" % (hexbytes(rawlength)))

                length: int = UInt16.decode(rawlength, order=ByteOrder.MSB)

                logger.debug(" > length (value) => %r" % (length))

                # The data then should follow the length, and be of the expected length
                data: bytes = handle.read(length)

                if not len(data) == length:
                    raise JPEGDataParseError(
                        "Unable to read the expected number of data bytes from the file!"
                    )

                # logger.debug(" > data => %r" % (data))

                # Image precision, width and height are stored at the beginning of the
                # Baseline DCT and Progressive DCT markers:
                if marker in [
                    Marker.SOF0,  # Baseline DCT
                    Marker.SOF2,  # Progressive DCT
                ]:
                    if marker is Marker.SOF0:
                        encoding = Encoding.BaselineDCT
                    elif marker is Marker.SOF2:
                        encoding = Encoding.ProgressiveDCT

                    precision = UInt8.decode(data[0:1], order=ByteOrder.MSB)
                    height = UInt16.decode(data[1:3], order=ByteOrder.MSB)
                    width = UInt16.decode(data[3:5], order=ByteOrder.MSB)

            self._segments.append(
                Segment(
                    marker=marker,
                    offset=Offset(source=offset),
                    length=length,
                    # data=data,
                )
            )

            offset += length

        self._encoding = encoding
        self._precision = precision
        self._width = width
        self._height = height

    @property
    def info(self) -> Information:
        """Returns the JPEG image's parsed information."""

        return self._info

    @property
    def filepath(self) -> str:
        """Returns the JPEG image's file path."""

        return self.info.filepath

    @property
    def filesize(self) -> int:
        """Returns the JPEG image's file size in bytes."""

        return self.info.filesize

    @property
    def order(self) -> ByteOrder:
        """Returns the JPEG image's byte order (always big-endian)."""

        return self.info.order

    @property
    def format(self) -> Format:
        """Returns the JPEG image's format: JPEG, JFIF, EXIF, etc."""

        return self.info.format

    @property
    def encoding(self) -> Encoding | None:
        """Returns the JPEG image's encoding: baseline or progressive DCT."""

        return self._encoding

    @property
    def precision(self) -> int | None:
        """Returns the JPEG image's precision."""

        return self._precision

    @property
    def width(self) -> int:
        """Returns the JPEG image's width."""

        return self._width

    @property
    def height(self) -> int:
        """Returns the JPEG image's height."""

        return self._height

    @property
    def segments(self) -> list[Segment]:
        return self._segments

    def dump(self):
        """Generates and prints a plaintext formatted tabular informational dump for the
        structure of the file, listing its elements, their offsets, lengths and data."""

        headers: list[str] = [
            "Index",
            "Element",
            "Legnth",
            "Offset Source",
            "Offset Target",
            "Data",
        ]

        rows: list[list[object]] = []

        for index, segment in enumerate(self.segments, start=1):
            rows.append(
                [
                    index,
                    segment,
                    segment.length,
                    segment.offset.source,
                    segment.offset.target,
                    None,
                ]
            )

        print()
        print(tabulate(rows=rows, headers=headers, style="curved"))


class JFIF(JPEG):
    """The JFIF class represents JFIF format JPEG files and their raw data."""

    pass


class EXIF(JPEG):
    """The EXIF class represents EXIF format JPEG files and their raw data."""

    pass
