import sys
from pathlib import Path
import numpy as np
import importlib.machinery
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
loader = importlib.machinery.SourceFileLoader("siteproBW", str(ROOT / "bin" / "siteproBW"))
spec = importlib.util.spec_from_loader(loader.name, loader)
siteproBW = importlib.util.module_from_spec(spec)
loader.exec_module(siteproBW)

from CEAS.bigwig_utils import summarize_bigwig


class StubBW:
    def __init__(self):
        self.values = {
            (0, 100): 1.0,
            (100, 200): 2.0,
            (200, 300): 3.0,
        }

    def get_as_array(self, chrom, start, end):
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


def test_siteproBW_direction(tmp_path):
    bw = StubBW()
    span = 100
    pf_res = 100
    bedlist = [
        ["chr1", "100", "200", "site1", "0", "+"],
        ["chr1", "100", "200", "site2", "0", "-"],
    ]
    siteprofs = []
    for line in bedlist:
        center = (int(line[1]) + int(line[2])) / 2
        prange = (
            center - span - pf_res / 2,
            center + span - pf_res / 2 + pf_res,
        )
        prof = summarize_bigwig(
            bw,
            line[0],
            int(prange[0]),
            int(prange[1]),
            int(2 * span / pf_res + 1),
        )
        if line[5] == "-":
            prof = prof[::-1]
        siteprofs.append(prof)

    dump = tmp_path / "dump.txt"
    siteproBW.dump(str(dump), bedlist, siteprofs)
    lines = [line.strip().split("\t")[-1] for line in dump.read_text().splitlines()]
    assert lines[0] == "1.0,2.0,3.0"
    assert lines[1] == "3.0,2.0,1.0"
