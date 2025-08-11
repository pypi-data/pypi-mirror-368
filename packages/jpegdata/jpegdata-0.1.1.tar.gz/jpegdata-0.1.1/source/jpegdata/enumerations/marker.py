from enumerific import Enumeration, anno


class Marker(Enumeration):
    """The Marker enumeration defines the markers present in JPEG files."""

    ############################ Start of Frame Markers ################################

    SOF0 = anno(
        0xC0,
        label="Start of Frame 0",
        notes="Baseline DCT",
    )

    SOF1 = anno(
        0xC1,
        label="Start of Frame 1",
        notes="Exended Sequential DCT",
    )

    SOF2 = anno(
        0xC2,
        label="Start of Frame 2",
        notes="Progressive DCT",
    )

    SOF3 = anno(
        0xC3,
        label="Start of Frame 3",
        notes="Lossless Sequential",
    )

    ############################# Huffman Table Marker #################################

    DHT = anno(
        0xC4,
        label="Define Huffman Table (DHT)",
    )

    ############################ Start of Frame Markers ################################

    SOF5 = anno(
        0xC5,
        label="Start of Frame 5",
        notes="Differential Sequential DCT",
    )

    SOF6 = anno(
        0xC6,
        label="Start of Frame 6",
        notes="Differential Progressive DCT",
    )

    SOF7 = anno(
        0xC7,
        label="Start of Frame 7",
        notes="Differential Lossless Sequential",
    )

    ############################ JPEG Extension Marker #################################

    JPG = anno(0xC8, label="JPEG Extensions")

    ############################ Start of Frame Markers ################################

    SOF9 = anno(
        0xC9,
        label="Start of Frame 7",
        notes="Extendend Sequential DCT (Arithmetic Coding)",
    )

    SOF10 = anno(
        0xCA,
        label="Start of Frame 7",
        notes="Progressive DCT (Arithmetic Coding)",
    )

    SOF11 = anno(
        0xCB,
        label="Start of Frame 7",
        notes="Lossless Sequential (Arithmetic Coding)",
    )

    ####################### Define Arithmetic Coding Marker ############################

    DAC = anno(
        0xCC,
        label="Define Arithmetic Coding",
    )

    ############################ Start of Frame Markers ################################

    SOF13 = anno(
        0xCD,
        label="Start of Frame 13",
        notes="Differential Sequential DCT (Arithmetic Coding)",
    )

    SOF14 = anno(
        0xCE,
        label="Start of Frame 14",
        notes="Differential Progressive DCT (Arithmetic Coding)",
    )

    SOF15 = anno(
        0xCF,
        label="Start of Frame 15",
        notes="Differential Lossless Sequential DCT (Arithmetic Coding)",
    )

    ################################ Restart Markers ###################################

    RST0 = anno(0xD0, label="Restart Marker 0")

    RST1 = anno(0xD1, label="Restart Marker 1")

    RST2 = anno(0xD2, label="Restart Marker 2")

    RST3 = anno(0xD3, label="Restart Marker 3")

    RST4 = anno(0xD4, label="Restart Marker 4")

    RST5 = anno(0xD5, label="Restart Marker 5")

    RST6 = anno(0xD6, label="Restart Marker 6")

    RST7 = anno(0xD7, label="Restart Marker 7")

    ################################ SOI/EOI Markers ###################################

    SOI = anno(0xD8, label="Start of Image")

    EOI = anno(0xD9, label="End of Image")

    ################################## SOS Marker ######################################

    SOS = anno(0xDA, label="Start of Scan")

    ############################ Structure Markers #####################################

    DQT = anno(0xDB, label="Define Quantization Table")

    DNL = anno(0xDC, label="Define Number of Lines")

    DRI = anno(0xDD, label="Define Restart Interval")

    DHP = anno(0xDE, label="Define Hierarchical Progression")

    ################################ Restart Markers ###################################

    EXP = anno(0xDF, label="Expand Reference Component")

    ########################### Application Segment Markers ############################

    APP0 = anno(0xE0, label="Application Segment 0")

    APP1 = anno(0xE1, label="Application Segment 1")

    APP2 = anno(0xE2, label="Application Segment 2")

    APP3 = anno(0xE3, label="Application Segment 3")

    APP4 = anno(0xE4, label="Application Segment 4")

    APP5 = anno(0xE5, label="Application Segment 5")

    APP6 = anno(0xE6, label="Application Segment 6")

    APP7 = anno(0xE7, label="Application Segment 7")

    APP8 = anno(0xE8, label="Application Segment 8")

    APP9 = anno(0xE9, label="Application Segment 9")

    APP10 = anno(0xEA, label="Application Segment 10")

    APP11 = anno(0xEB, label="Application Segment 11")

    APP12 = anno(0xEC, label="Application Segment 12")

    APP13 = anno(0xED, label="Application Segment 13")

    APP14 = anno(0xEE, label="Application Segment 14", notes="Adobe APP14 marker")

    APP15 = anno(0xEF, label="Application Segment 15")

    ########################### JPEG Extension Markers #################################

    JEX0 = anno(0xF0, label="JPEG Extension 0")

    JEX1 = anno(0xF1, label="JPEG Extension 1")

    JEX2 = anno(0xF2, label="JPEG Extension 2")

    JEX3 = anno(0xF3, label="JPEG Extension 3")

    JEX4 = anno(0xF4, label="JPEG Extension 4")

    JEX5 = anno(0xF5, label="JPEG Extension 5")

    JEX6 = anno(0xF6, label="JPEG Extension 6")

    JEX7 = anno(
        0xF7,
        label="JPEG Extension 7",
        notes="Lossless JPEG",
    )

    JEX8 = anno(
        0xF8,
        label="JPEG Extension 8",
        notes="Lossless JPEG Extension Parameters",
    )

    JEX9 = anno(0xF9, label="JPEG Extension 6")

    JEX10 = anno(0xFA, label="JPEG Extension 6")

    JEX11 = anno(0xFB, label="JPEG Extension 6")

    JEX12 = anno(0xFC, label="JPEG Extension 6")

    JEX13 = anno(0xFD, label="JPEG Extension 6")

    ################################ Comment Marker ####################################

    COM = anno(0xFE, label="Comment")
