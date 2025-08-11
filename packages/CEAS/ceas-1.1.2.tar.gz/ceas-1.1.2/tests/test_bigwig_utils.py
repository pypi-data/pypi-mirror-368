import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from CEAS.bigwig_utils import summarize_bigwig


class StubBW:
    def __init__(self):
        self.values = {
            (0, 100): 1.0,
            (100, 200): 2.0,
            (200, 300): 3.0,
        }

    def get_as_array(self, chrom, start, end):
        # The real BigWigFile implementation from ``bx-python`` requires
        # chromosome names to be provided as ``bytes``.  Mimic that
        # behaviour here so that the tests catch any accidental use of
        # ``str`` objects which would fail at runtime.
        if not isinstance(chrom, (bytes, bytearray)):
            raise TypeError("expected bytes, str found")
        arr = np.empty(end - start)
        arr[:] = np.nan
        for (s, e), v in self.values.items():
            s1 = max(s, start)
            e1 = min(e, end)
            if s1 < e1:
                arr[s1 - start : e1 - start] = v
        return arr


def test_summarize_bigwig_basic():
    bw = StubBW()
    result = summarize_bigwig(bw, "chr1", 0, 300, 3)
    assert result == [1.0, 2.0, 3.0]
