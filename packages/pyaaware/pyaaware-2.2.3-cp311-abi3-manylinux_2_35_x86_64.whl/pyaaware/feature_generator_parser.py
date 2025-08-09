from dataclasses import dataclass
from itertools import pairwise

from .constants import GF_BE
from .constants import MF_BE
from .constants import ML_BE
from .constants import STACKED_BIN_TYPES


class FeatureMode:
    def __init__(self, feature_mode: str):
        if len(feature_mode) < 8:
            raise ValueError("Invalid feature mode")

        self.name = feature_mode
        self.type = feature_mode[0:2]
        self.twin = feature_mode[2]
        self.bands = feature_mode[3:5]
        self.bwin = feature_mode[5]
        self.rctype = feature_mode[6]
        self.rcval = int(feature_mode[7:])

        if self.name != f"{self.type}{self.twin}{self.bands}{self.bwin}{self.rctype}{self.rcval}":
            raise ValueError("Invalid feature mode")

    def __str__(self):
        return f"{self.name:<9}: {self.type}, {self.twin}, {self.bands:<2}, {self.bwin}, {self.rctype}, {self.rcval}"


@dataclass
class FeatureTransform:
    length: int
    overlap: int
    ttype: str


@dataclass(frozen=True)
class Feature:
    feature_mode: FeatureMode
    eftransform: FeatureTransform
    ftransform: FeatureTransform
    itransform: FeatureTransform
    bin_start: int
    bin_end: int
    bins: int
    bwin: str
    twin: str
    decimation: int
    stride: int
    step: int
    cmptype: str
    bandedge: list[int]
    num_bandedges: int
    feature_parameters: int
    hbandsize: list[int]


def _get_length_overlap(feature_mode: FeatureMode) -> tuple[int, int]:
    if feature_mode.type in ("cm", "hm", "pm"):
        return 256, 128
    if feature_mode.type in ("cn", "hn", "pn"):
        return 256, 64
    if feature_mode.type in ("c8", "h8", "p8"):
        return 256, 32
    if feature_mode.type in ("cf", "hf", "pf"):
        return 256, 16
    if feature_mode.type in ("cq", "hq", "pq"):
        return 320, 160
    if feature_mode.type in ("cr", "hr", "pr"):
        return 320, 80
    if feature_mode.type in ("cs", "hs", "ps"):
        return 320, 40
    if feature_mode.type in ("ct", "ht", "pt"):
        return 400, 200
    if feature_mode.type in ("cu", "hu", "pu"):
        return 400, 100
    if feature_mode.type in ("cv", "hv", "pv"):
        return 400, 50
    if feature_mode.type in ("ce", "he", "pe"):
        return 512, 256
    if feature_mode.type in ("cd", "hd", "pd"):
        return 512, 128
    if feature_mode.type in ("ca", "ha", "pa"):
        return 512, 64
    if feature_mode.type in ("cb", "hb", "pb"):
        return 512, 32
    if feature_mode.type in ("cc", "hc", "pc"):
        return 512, 16
    if feature_mode.type in ("cj", "hj", "pj"):
        return 1024, 128
    if feature_mode.type in ("ck", "hk", "pk"):
        return 1024, 64
    if feature_mode.type in ("cl", "hl", "pl"):
        return 1024, 32
    return 256, 64


def _get_twin_ttype(feature_mode: FeatureMode) -> tuple[str, str]:
    if feature_mode.twin == "r":
        return "none", "stft-olsa-hanns"
    if feature_mode.twin == "m":
        return "none", "stft-olsa-hammd"
    if feature_mode.twin == "n":
        return "none", "stft-olsa-hannd"
    if feature_mode.twin == "h":
        return "hann", "stft-olsa-hann"
    if feature_mode.twin == "t":
        return "none", "tdac"
    if feature_mode.twin == "o":
        return "none", "tdac-co"

    raise ValueError("Invalid feature mode")


def _get_bwin(feature_mode: FeatureMode) -> str:
    if feature_mode.bwin == "t":
        return "tri"
    if feature_mode.bwin == "r":
        return "rect"
    if feature_mode.bwin == "n":
        return "none"

    raise ValueError("Invalid feature mode")


def _get_rate_change(feature_mode: FeatureMode) -> tuple[int, int, int]:
    if feature_mode.rctype == "d":
        decimation = feature_mode.rcval
        stride = 1
        step = 1
        return decimation, stride, step
    if feature_mode.rctype == "s":
        decimation = 1
        stride = feature_mode.rcval
        step = feature_mode.rcval
        return decimation, stride, step
    if feature_mode.rctype == "b":
        decimation = 2
        stride = feature_mode.rcval
        step = feature_mode.rcval
        return decimation, stride, step
    if feature_mode.rctype == "v":
        decimation = 1
        stride = feature_mode.rcval
        step = feature_mode.rcval // 2
        return decimation, stride, step
    if feature_mode.rctype == "o":
        decimation = 2
        stride = feature_mode.rcval
        step = feature_mode.rcval // 2
        return decimation, stride, step
    if feature_mode.rctype == "t":
        decimation = 1
        stride = feature_mode.rcval
        step = 2 * feature_mode.rcval // 3
        return decimation, stride, step
    if feature_mode.rctype == "f":
        decimation = 1
        stride = feature_mode.rcval
        step = 3 * feature_mode.rcval // 4
        return decimation, stride, step
    if feature_mode.rctype == "e":
        decimation = 1
        stride = feature_mode.rcval
        step = 4 * feature_mode.rcval // 5
        return decimation, stride, step

    raise ValueError("Invalid feature mode")


def parse_feature_mode(feature_mode: str) -> Feature:
    fm = FeatureMode(feature_mode)
    length, overlap = _get_length_overlap(fm)
    twin, ttype = _get_twin_ttype(fm)

    eftransform = FeatureTransform(length, overlap, ttype)
    ftransform = FeatureTransform(length, overlap, "stft-olsa" if twin == "hann" else ttype)
    itransform = FeatureTransform(length, overlap, ttype)

    if fm.type[0] == "y":
        if (fm.rctype == "b" and fm.rcval > 1) or (fm.rctype != "b" and fm.rcval > 2):
            raise ValueError("Invalid feature mode")
        itransform.overlap = itransform.length // 2
        itransform.ttype = "stft-olsa-hann"

        if fm.rctype != "s":
            eftransform.overlap = eftransform.length // 2
            eftransform.ttype = "stft-olsa-hann"

    bin_start = 0
    if ttype in ("tdac", "tdac-co"):
        bin_end = ftransform.length // 2 - 1
    else:
        bin_end = ftransform.length // 2

    bins = bin_end - bin_start + 1

    bwin = _get_bwin(fm)
    decimation, stride, step = _get_rate_change(fm)

    cmptype = "cbrte"

    if fm.type == "gf":
        if fm.bands in GF_BE:
            bandedge = GF_BE[fm.bands]
            num_bandedges = len(bandedge)
        else:
            raise ValueError("Invalid feature mode")
        feature_parameters = num_bandedges

    elif fm.type == "mf":
        if feature_mode[2:5] == "cdd":
            bandedge = MF_BE
            num_bandedges = len(bandedge)
            twin = "hann"
            bwin = "tri"
            cmptype = "loge"
            decimation = 2
            stride = 1
            step = 1
            feature_parameters = 39
        else:
            raise ValueError("Invalid feature mode")

    elif fm.type == "ml":
        cmptype = "loge"
        if fm.bands in ML_BE:
            bandedge = ML_BE[fm.bands]
            num_bandedges = len(bandedge)
        else:
            raise ValueError("Invalid feature mode")
        feature_parameters = num_bandedges

    elif fm.type in ("bc", "yc"):
        bandedge = list(range(bin_start, bin_end + 1))
        num_bandedges = len(bandedge)
        feature_parameters = num_bandedges
        if bwin != "none":
            raise ValueError("Invalid feature mode")

    elif fm.type in ("bl", "yl"):
        bandedge = list(range(bin_start, bin_end + 1))
        num_bandedges = len(bandedge)
        feature_parameters = num_bandedges
        cmptype = "loge"
        if bwin != "none":
            raise ValueError("Invalid feature mode")

    elif fm.type in STACKED_BIN_TYPES:
        bandedge = list(range(bin_start, bin_end + 1))
        num_bandedges = len(bandedge)
        if ttype == "tdac-co":
            feature_parameters = num_bandedges
        else:
            feature_parameters = 2 * num_bandedges

        if fm.type[0] == "h":
            cmptype = "plcd3"
        elif fm.type[0] == "p":
            cmptype = "plcd3p"
        elif fm.type[0] == "c":
            cmptype = "none"

        if bwin != "none":
            raise ValueError("Invalid feature mode")

    else:
        raise ValueError("Invalid feature mode")

    if bandedge[-1] > bin_end:
        bandedge[-1] = bin_end

    if bandedge[0] < bin_start:
        bandedge[0] = bin_start

    hbandsize = [bandedge[0] - bin_start] + [b - a for a, b in pairwise(bandedge)] + [bin_end - bandedge[-1] + 1]

    return Feature(
        feature_mode=fm,
        eftransform=eftransform,
        ftransform=ftransform,
        itransform=itransform,
        bwin=bwin,
        twin=twin,
        bin_start=bin_start,
        bin_end=bin_end,
        bins=bins,
        decimation=decimation,
        stride=stride,
        step=step,
        cmptype=cmptype,
        bandedge=bandedge,
        num_bandedges=num_bandedges,
        feature_parameters=feature_parameters,
        hbandsize=hbandsize,
    )


def feature_parameters(feature_mode: str) -> int:
    """Get the number of feature parameters for the given feature mode."""
    return parse_feature_mode(feature_mode).feature_parameters


def feature_forward_transform_config(feature_mode: str) -> dict:
    """Get the forward transform config for the given feature mode."""
    feature = parse_feature_mode(feature_mode)
    return {
        "length": feature.ftransform.length,
        "overlap": feature.ftransform.overlap,
        "bin_start": feature.bin_start,
        "bin_end": feature.bin_end,
        "ttype": feature.ftransform.ttype,
    }


def feature_inverse_transform_config(feature_mode: str) -> dict:
    """Get the inverse transform config for the given feature mode."""
    feature = parse_feature_mode(feature_mode)
    return {
        "length": feature.itransform.length,
        "overlap": feature.itransform.overlap,
        "bin_start": feature.bin_start,
        "bin_end": feature.bin_end,
        "ttype": feature.itransform.ttype,
        "gain": 1,
    }
