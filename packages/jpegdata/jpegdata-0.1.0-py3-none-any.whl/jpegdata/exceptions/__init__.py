class JPEGDataError(RuntimeError):
    pass


class JPEGDataFileError(JPEGDataError):
    pass


class JPEGDataFileFormatError(JPEGDataFileError):
    pass


class JPEGDataReadError(JPEGDataError):
    pass


class JPEGDataParseError(JPEGDataError):
    pass


class JPEGDataWriteError(JPEGDataError):
    pass
