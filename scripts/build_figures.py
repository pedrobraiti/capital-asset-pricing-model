"""Generate every figure into ``output/figures/``.

    python scripts/build_figures.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
warnings.filterwarnings("ignore")

from capm.reporting import generate_all_figures  # noqa: E402


def main() -> None:
    figdir = ROOT / "output" / "figures"
    paths = generate_all_figures(figdir)
    for path in paths:
        print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
