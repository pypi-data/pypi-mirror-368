from jpegdata import (
    JPEG,
    JFIF,
    EXIF,
    ByteOrder,
    Format,
    Encoding,
    Segment,
    Marker,
)

import os


def test_jpegdata_initialisation_exif_format_jpeg(path: callable):
    """Test loading a JPEG stored using the EXIF JPEG file format."""

    filepath: str = path("examples/formats/exif.jpeg")

    jpeg = JPEG(filepath=filepath)

    assert isinstance(jpeg, JPEG)
    assert isinstance(jpeg, EXIF)

    assert jpeg.filepath == filepath
    assert jpeg.filesize == os.path.getsize(filepath)
    assert jpeg.order is ByteOrder.MSB
    assert jpeg.format is Format.EXIF
    assert jpeg.encoding is Encoding.BaselineDCT
    assert jpeg.precision == 8
    assert jpeg.width == 3
    assert jpeg.height == 3

    assert len(jpeg) == 11

    for segment in jpeg:
        assert isinstance(segment, Segment)
        assert isinstance(segment.marker, Marker)


def test_jpegdata_initialisation_jfif_format_jpeg(path: callable):
    """Test loading a JPEG stored using the JFIF JPEG file format."""

    filepath: str = path("examples/formats/jfif.jpeg")

    jpeg = JPEG(filepath=filepath)

    assert isinstance(jpeg, JPEG)
    assert isinstance(jpeg, JFIF)

    assert jpeg.filepath == filepath
    assert jpeg.filesize == os.path.getsize(filepath)
    assert jpeg.order is ByteOrder.MSB
    assert jpeg.format is Format.JFIF
    assert jpeg.encoding is Encoding.BaselineDCT
    assert jpeg.precision == 8
    assert jpeg.width == 3
    assert jpeg.height == 3

    assert len(jpeg) == 14

    for segment in jpeg:
        assert isinstance(segment, Segment)
        assert isinstance(segment.marker, Marker)
