"""Utilities for working with BigWig files using bx-python."""
from __future__ import annotations

from typing import List, Optional, Union

import numpy as np
from bx.bbi.bigwig_file import BigWigFile


def open_bigwig(path: str) -> BigWigFile:
    """Open *path* as a :class:`~bx.bbi.bigwig_file.BigWigFile`.

    Parameters
    ----------
    path:
        Path to a BigWig file.
    """
    return BigWigFile(open(path, "rb"))


def summarize_bigwig(
    bw: Union[str, BigWigFile], chrom: str, start: int, end: int, bins: int
) -> Optional[List[float]]:
    """Return average values for *bins* equally spaced segments.

    This mimics the :meth:`CistromeAP.jianlib.BwReader.BwIO.summarize`
    interface previously used by CEAS.  If no data exist for the requested
    interval ``None`` is returned.
    """
    if isinstance(bw, str):
        bw = open_bigwig(bw)

    span = end - start
    bin_size = span / float(bins)
    results: List[float] = []
    # ``bx-python`` expects chromosome names as ``bytes`` objects under
    # Python 3.  The original CEAS code (written for Python 2) freely
    # passed ``str`` values here which in that environment were actually
    # byte strings.  When running under Python 3 this results in a
    # ``TypeError`` like ``expected bytes, str found``.  To maintain a
    # convenient ``str`` based API we encode any ``str`` chromosome names
    # before handing them off to :mod:`bx-python`.
    if isinstance(chrom, str):
        chrom_bytes = chrom.encode()
    else:
        chrom_bytes = chrom

    for i in range(bins):
        bin_start = int(start + i * bin_size)
        bin_end = int(start + (i + 1) * bin_size)
        arr = bw.get_as_array(chrom_bytes, bin_start, bin_end)
        if arr is None:
            results.append(float("nan"))
            continue
        arr = arr[~np.isnan(arr)]
        results.append(float(arr.mean()) if arr.size else float("nan"))

    if all(np.isnan(results)):
        return None
    return results
