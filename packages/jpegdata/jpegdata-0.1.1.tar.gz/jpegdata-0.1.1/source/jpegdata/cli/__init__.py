from jpegdata.logging import logger
from jpegdata.exceptions import JPEGDataFileError, JPEGDataParseError
from jpegdata import JPEG, Format, Encoding, __version__ as jpegdata_version

import argparse
import os
import sys
import datetime
import json

logger = logger.getChild(__name__)


def parser():
    """The CLI parser function is the entrypoint for the JPEGData command line tools."""

    parser = argparse.ArgumentParser(
        description="The JPEGData tool can be used to parse information from JPEG files.",
    )

    parser.add_argument("filename", help="The name of the file to process.")

    parser.add_argument("--verbose", action="store_true", help="show verbose output?")

    parser.add_argument("--version", action="store_true", help="show library version?")

    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="output format"
    )

    args = parser.parse_args()

    filename: str = args.filename
    filepath: str = os.path.abspath(filename)

    if not os.path.exists(filepath):
        raise JPEGDataFileError(
            f"The specified file path, '{filename}', does not exist!"
        )
    elif not os.path.isfile(filepath):
        raise JPEGDataFileError(
            f"The specified file path, '{filename}', is not a file!"
        )

    try:
        jpeg = JPEG(filepath=filepath)

        if args.format == "json":
            data: dict[str, object] = {
                "filename": filename,
                "filepath": jpeg.filepath,
                "filesize": jpeg.filesize,
                "filedate": {
                    "created": jpeg.datetime_created.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "modified": jpeg.datetime_modified.strftime("%Y-%m-%d %H:%M:%S.%f"),
                },
                "byte_oder": jpeg.order.name if jpeg.order else None,
                "encoding": jpeg.encoding.name if jpeg.encoding else None,
                "precision": jpeg.precision,
                "width": jpeg.width,
                "height": jpeg.height,
            }

            if args.verbose is True:
                data["segments"] = segments = []

                for segment in jpeg.segments:
                    segments.append(
                        {
                            "element": segment.marker.name,
                            "length": segment.length,
                            "offset": {
                                "source": segment.offset.source,
                                "target": segment.offset.target,
                            },
                        }
                    )

            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            if args.version is True:
                print("JPEGData Version:    %s" % (jpegdata_version))
            print("File Name:           %s" % (filename))
            print("File Path:           %s" % (jpeg.filepath))
            print("File Size:           %d bytes" % (jpeg.filesize))
            print("File Created Date:   %s" % (jpeg.datetime_created))
            print("File Modified Date:  %s" % (jpeg.datetime_modified))
            print("Byte Order:          %s" % (jpeg.order.name if jpeg.order else "?"))
            print(
                "Format:              %s"
                % (jpeg.format.description if jpeg.format else "?")
            )
            print(
                "Encoding:            %s"
                % (jpeg.encoding.description if jpeg.encoding else "?")
            )
            print("Precision:           %d" % (jpeg.precision))
            print("Width:               %d pixels" % (jpeg.width))
            print("Height:              %d pixels" % (jpeg.height))

            if args.verbose is True:
                jpeg.dump()
    except JPEGDataFileError as exception:
        print(str(exception))
    except JPEGDataParseError as exception:
        print(str(exception))
