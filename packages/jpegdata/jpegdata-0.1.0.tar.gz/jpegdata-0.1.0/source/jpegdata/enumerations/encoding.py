from enumerific import Enumeration, anno


class Encoding(Enumeration):
    """The Encoding enumeration denotes the various encoding "flavours" of JPEG."""

    BaselineDCT = anno(
        1,
        description="Baseline DCT",
    )

    ProgressiveDCT = anno(
        2,
        description="Progressive DCT",
    )
