from enumerific import Enumeration, anno


class Format(Enumeration):
    """The Format enumeration defines the JPEG file formats supported by the library."""

    JPEG = anno(
        1,
        description="JPEG Interchange File (JIF) format",
    )

    JFIF = anno(
        2,
        description="JPEG File Interchange (JFIF) format",
    )

    EXIF = anno(
        3,
        description="JPEG Extensible Image File (EXIF) format",
    )
