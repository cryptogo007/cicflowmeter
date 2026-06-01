import logging
import uuid
from itertools import islice, zip_longest
from pathlib import Path

import numpy


def get_logger(debug=False):
    logger = logging.getLogger("cicflowmeter")
    if not logger.hasHandlers():
        logging.basicConfig()
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    return logger


def grouper(iterable, n, max_groups=0, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""

    if max_groups > 0:
        iterable = islice(iterable, max_groups * n)

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def random_string():
    return uuid.uuid4().hex[:6].upper().replace("0", "X").replace("O", "Y")


def live_csv_rotated_path(base_output: str, segment_index: int) -> str:
    """Path for live-capture CSV rotation.

    segment_index 0 → base path (e.g. livepacket.csv)
    segment_index 1 → livepacket1.csv
    segment_index 2 → livepacket2.csv
    """
    path = Path(base_output)
    if segment_index <= 0:
        return str(path)
    return str(path.parent / f"{path.stem}{segment_index}{path.suffix}")


def get_statistics(alist: list):
    """Get summary statistics of a list"""
    iat = dict()
    alist = [float(x) for x in alist]

    if len(alist) > 1:
        iat["total"] = sum(alist)
        iat["max"] = max(alist)
        iat["min"] = min(alist)
        iat["mean"] = numpy.mean(alist)
        iat["std"] = numpy.sqrt(numpy.var(alist))
    else:
        iat["total"] = 0
        iat["max"] = 0
        iat["min"] = 0
        iat["mean"] = 0
        iat["std"] = 0

    return iat
