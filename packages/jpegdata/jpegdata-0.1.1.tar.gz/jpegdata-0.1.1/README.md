# JPEGData

The JPEGData library for Python provides a streamlined way to work with JPEG image files
offering the ability to extract certain file metadata.

### Requirements

The JPEGData library has been tested to work with Python 3.10, 3.11, 3.12 and 3.13, but
has not been tested, nor is its use supported with earlier versions of Python.

### Installation

The library is available from the PyPI repository, so may be added easily to a project's
dependencies via its `requirements.txt` file or similar by referencing the library's
name, `jpegdata`, or the library may be installed directly onto your local development
system using `pip install` by entering the following command:

	$ pip install jpegdata

### Classes, Methods & Properties

The JPEGData library's main class is the `JPEG` class through which JPEG image files can
be loaded, modified via the supported actions, and saved. The library supports reading
several common JPEG file formats including JFIF and EXIF formatted JPEG files. Currently
the library does not support more recent JPEG formats and derivations such as JPEG XL,
JPEG-2000, JPEG XR, etc.

The `JPEG` class offers the following methods:

* `JPEG(filepath: str)` – The `JPEG()` class constructor expects an absolute filepath at
a minimum for the JPEG file you wish to open. Upon initializing the class with the file,
the library will then attempt to load and parse the file. Assuming that the file is a 
valid JPEG file, the library will parse the file, identify any segments contained within
the file, and any data associated with each of the segments, and will determine several
intrinsic properties of the JPEG image including the canvas width and height.

The `JPEG` class offers the following properties:

 * `info` (`Information`) – The `info` property can be used to access the `Information`
 class instance that is created when the `JPEG` class instance is created and the file is
 parsed. The `Information` class instance contains core information about the parsed file
 including the `filepath`, `filesize`, (byte) `order`, and `format`.
 
 This property is used internally by the class to populate the corresponding top level
 properties of the same names noted below.

 * `filepath` (`str`) – The `filepath` property can be used to get the original file path
 that was specified at the time the class was initialised.

 * `filesize` (`int`) – The `filesize` property can be used to get the original file size
 of the file that was specified at the time the class was initialised.

 * `order` (`ByteOrder`) – The `order` property can be used to determine the byte order
 of the JPEG file. The property will report either `ByteOrder.MSB` for big endian files
 or `ByteOrder.LSB` for little endian files.

 * `format` (`Format`) – The `format` property can be used to determine the file format
 of the JPEG file. The property will report either `Format.JPEG` for baseline formatted
 JPEG files, `Format.JFIF` for JFIF formatted files and `Format.EXIF` for EXIF formatted
 JPEG files.

 * `encoding` (`Encoding`) – The `encoding` property can be used to determine the encoding
 used for the JPEG file, which will report a `Encoding` enumeration value which includes:

   * `Encoding.BaselineDCT` for baseline DCT encoded images;
   * `Encoding.ProgressiveDCT` for progressive DCT encoded images.

 * `width` (`int`) – The `width` property can be used to access the parsed pixel width of the image.

 * `height` (`int`) – The `height` property can be used to access the parsed pixel height of the image.
 
* `precision` (`int`) – The `precision` property can be used to access the parsed precision of the image.

### Example of Use

To create an instance of the `JPEG` class, import the `JPEG` class from the library and
specify the absolute file path to the JPEG file you wish to open as the first argument.
If the specified file can be opened successfully, the library will return an instance of
either the `JPEG`, `JFIF` or `EXIF` subclasses, depending on the file format of the
specified JPEG file; these classes are subclasses of the library's `JPEG` base class.

<!--pytest.mark.skip-->

```python
from jpegdata import JPEG, Format, Encoding

filepath = "/path/to/file.jpeg"

# Initialize the library with the absolute file path of the JPEG file to load
jpeg = JPEG(filepath=filepath)

# Use the parsed properties of the file
assert jpeg.format is Format.EXIF
assert jpeg.encoding is Encoding.BaselineDCT
assert jpeg.precision == 8
assert jpeg.width == 600
assert jpeg.height == 400

# If desired, iterate through the segments held within the file:
for segment in jpeg:
    print(segment)
```

### Command Line Tool

The `jpegdata` command line tool, installed alongside the library, provides a command
line interface to print out the information parsed from the specified JPEG file.

The tool can print out the information directly to the command line either as plain text
or as a JSON-serialised payload.

To print the help information for the tool, pass the `--help` argument.

```shell
$ jpegdata ./path/to/file.jpeg
```

The above command will generate output similar to the following:

```plain
File Name:           ./path/to/file.jpeg
File Path:           /absolute/path/to/file.jpeg
File Size:           3890 bytes
File Created Date:   2025-08-10 17:15:13.892694
File Modified Date:  2025-08-10 17:15:07.312874
Byte Order:          MSB
Format:              JPEG Extensible Image File (EXIF) format
Encoding:            Baseline DCT
Precision:           8
Width:               3 pixels
Height:              3 pixels
```

To emit the parsed information as a JSON-serialised payload, pass the `--format json`
argument to the command:

```shell
$ jpegdata ./path/to/file.jpeg --format json
```

The above command will generate output similar to the following:

```json
{
  "filename": "./path/to/file.jpeg",
  "filepath": "/absolute/path/to/file.jpeg",
  "filesize": 3890,
  "filedate": {
    "created": "2025-08-10 17:15:13.892694",
    "modified": "2025-08-10 17:15:07.312874"
  },
  "byte_oder": "MSB",
  "encoding": "BaselineDCT",
  "precision": 8,
  "width": 3,
  "height": 3
}
```

To emit the verbose form of output, pass the `--verbose` argument, which will include
information about the parsed segment markers found in the file. This is included in both
the plain text and JSON-serialised output formats.

### Disclaimer

While every effort has been made to ensure that the library works reliably with JPEG
files and embedded metadata, you must ensure that all files are backed up before using
the JPEGData library with any files, especially as the library is in early development.

Furthermore, the library may not be able to read nor preserve all metadata or other data
within a JPEG file, especially if manufacturer specific, custom or other "private" data
are present. As such, it is possible that loss of data could occur if an image is loaded
and is then overwritten by saving the file back to the same file path, _when saving is
available in future versions of the library (currently the library is read-only)_.

Use of the library is entirely at your own risk and the authors bear no responsibility
for losses of any kind. By using the software you assume all such risk and liability.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

### Credits & References

The JPEG file format, and the related EXIF, IPTC and XMP metadata model specifications
were researched across various sources. Please visit these valuable online resources to
learn more about the JPEG file format and related metadata model specifications and to
support these world class organisations and their products:

 * JPEG File Format
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000619.shtml
   * https://en.wikipedia.org/wiki/JPEG (JPEG)
   * https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format (JFIF)
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000018.shtml (JFIF)
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000147.shtml (EXIF)
   * https://cran.r-project.org/web/packages/ctypesio/vignettes/parse-jpeg.html
   * https://dev.exiv2.org/projects/exiv2/wiki/The_Metadata_in_JPEG_files

 * EXIF Metadata Model & Fields
   * https://www.cipa.jp/e/index.html
   * https://www.loc.gov/preservation/digital/formats/fdd/fdd000146.shtml
   * https://exiftool.org/TagNames/EXIF.html
   * https://www.media.mit.edu/pia/Research/deepview/exif.html
   * https://exiv2.org/tags.html

 * IPTC Metadata Model & Fields
   * https://www.iptc.org/std/photometadata/specification/IPTC-PhotoMetadata
   * https://exiftool.org/TagNames/IPTC.html

 * XMP Metadata Model & Fields
   * https://www.adobe.com/products/xmp.html
   * https://exiftool.org/TagNames/XMP.html

### Copyright & License Information

Copyright © 2025 Daniel Sissman; licensed under the MIT License.