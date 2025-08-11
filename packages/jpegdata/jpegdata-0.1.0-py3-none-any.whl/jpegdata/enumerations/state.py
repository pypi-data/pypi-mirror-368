from enumerific import Enumeration, auto


class State(Enumeration):
    """The State enumeration defines various states used while parsing JPEG files."""

    SOF = auto(description="Start of File")

    EOF = auto(description="End of File")

    SOI = auto(description="Start of Image")

    EOI = auto(description="End of Image")

    SOS = auto(description="Start of Scan")
