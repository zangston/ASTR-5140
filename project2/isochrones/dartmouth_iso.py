# isochrones/dartmouth_iso.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import pandas as pd


@dataclass(frozen=True)
class DartmouthIsochrone:
    """
    Container for a single Dartmouth isochrone file:
      - meta: parsed header metadata (age, feh, afe, photometric system, etc.)
      - df:   tabular data (EEP, M/Mo, LogTeff, ... sdss_u/g/r/i/z)
    """
    meta: Dict[str, Union[str, float, int]]
    df: pd.DataFrame


def _try_parse_float(s: str) -> Optional[float]:
    try:
        return float(s)
    except Exception:
        return None


def _parse_header_meta(lines: list[str]) -> Dict[str, Union[str, float, int]]:
    """
    Parses useful metadata from Dartmouth header lines.
    Example header snippets:
      #AGE= 5.000 EEPS=272
      # 1.9380  0.2537 5.3740E-03 ...  -0.50   0.00   (Fe/H, a/Fe line)
      #**PHOTOMETRIC SYSTEM**: SDSS (AB)
    """
    meta: Dict[str, Union[str, float, int]] = {}

    # Photometric system
    for ln in lines:
        if "PHOTOMETRIC SYSTEM" in ln:
            # e.g. "#**PHOTOMETRIC SYSTEM**: SDSS (AB)"
            parts = ln.split(":", 1)
            if len(parts) == 2:
                meta["photometric_system"] = parts[1].strip()
            else:
                meta["photometric_system"] = ln.strip("#").strip()
            break

    # AGE + EEPS
    for ln in lines:
        if ln.strip().startswith("#AGE="):
            # e.g. "#AGE= 5.000 EEPS=272"
            # very forgiving parse:
            tokens = ln.replace("#", "").replace("=", " ").split()
            # tokens like: ["AGE", "5.000", "EEPS", "272"]
            for i in range(len(tokens) - 1):
                key = tokens[i].strip().lower()
                val = tokens[i + 1].strip()
                if key in ("age", "eeps"):
                    fv = _try_parse_float(val)
                    if fv is not None:
                        meta[key] = int(fv) if key == "eeps" else float(fv)
            break

    # Try to parse the "mix-len Y Z Zeff [Fe/H] [a/Fe]" numeric row
    # We locate the line after "#MIX-LEN  Y      Z ..." if present.
    for idx, ln in enumerate(lines):
        if ln.strip().startswith("#MIX-LEN"):
            # next non-empty line should be the numeric values
            for j in range(idx + 1, min(idx + 6, len(lines))):
                ln2 = lines[j].strip()
                if ln2.startswith("#") and any(ch.isdigit() for ch in ln2):
                    # Example:
                    # "# 1.9380  0.2537 5.3740E-03 5.3740E-03  -0.50   0.00"
                    vals = ln2.strip("#").split()
                    if len(vals) >= 6:
                        meta["mix_len"] = float(vals[0])
                        meta["Y"] = float(vals[1])
                        meta["Z"] = float(vals[2])
                        meta["Zeff"] = float(vals[3])
                        meta["feh"] = float(vals[4])
                        meta["afe"] = float(vals[5])
                    break
            break

    # NUMBER OF AGES, MAGS
    for ln in lines:
        if ln.strip().startswith("#NUMBER OF AGES"):
            # "#NUMBER OF AGES= 1 MAGS= 5"
            tokens = ln.replace("#", "").replace("=", " ").split()
            # tokens: ["NUMBER", "OF", "AGES", "1", "MAGS", "5"]
            # We'll just search for "ages" and "mags"
            for i in range(len(tokens) - 1):
                key = tokens[i].strip().lower()
                val = tokens[i + 1].strip()
                if key in ("ages", "mags"):
                    fv = _try_parse_float(val)
                    if fv is not None:
                        meta[key] = int(fv)
            break

    return meta


def read_dartmouth_iso(path: Union[str, Path]) -> DartmouthIsochrone:
    """
    Read a Dartmouth .iso file and return DartmouthIsochrone(meta, df).

    Assumptions (matches your example):
      - header lines begin with '#'
      - a column header line exists like:
          #EEP   M/Mo    LogTeff  LogG   LogL/Lo sdss_u  sdss_g ...
      - data rows follow as whitespace-separated values
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Isochrone file not found: {path}")

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    header_lines: list[str] = []
    colnames: Optional[list[str]] = None
    data_start_idx: Optional[int] = None

    for idx, ln in enumerate(lines):
        if ln.strip().startswith("#"):
            header_lines.append(ln)
            # Find the column names line: starts with "#EEP" in these files
            # Example: "#EEP   M/Mo    LogTeff ..."
            stripped = ln.strip("#").strip()
            if stripped.startswith("EEP"):
                colnames = stripped.split()
        else:
            # first non-header line after colnames => start of data
            if colnames is not None:
                data_start_idx = idx
                break

    if colnames is None or data_start_idx is None:
        raise ValueError(
            f"Could not find column header (#EEP ...) and data start in file: {path}"
        )

    # Read the data block with pandas
    # We use the already-determined start index and supply names.
    # Use engine='python' for slightly more forgiving whitespace parsing.
    data_str = "\n".join(lines[data_start_idx:])
    from io import StringIO
    df = pd.read_csv(
        StringIO(data_str),
        sep=r"\s+",
        names=colnames,
        comment="#",
        engine="python",
    )

    # Normalize column names to something easier (optional)
    # Keep original too if you prefer; here we just make them python-friendly.
    rename_map = {}
    for c in df.columns:
        c2 = c.strip()
        c2 = c2.replace("/", "_per_")     # LogL/Lo -> LogL_per_Lo
        c2 = c2.replace("M/Mo", "M_per_Mo")
        c2 = c2.replace("-", "_")
        rename_map[c] = c2
    df = df.rename(columns=rename_map)

    # Convert numeric columns (pandas usually does this automatically)
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    meta = _parse_header_meta(header_lines)
    meta["filename"] = path.name
    meta["path"] = str(path)

    return DartmouthIsochrone(meta=meta, df=df)


def load_isochrones(directory: Union[str, Path]) -> Dict[str, DartmouthIsochrone]:
    """
    Convenience loader: reads all *.iso files in a directory.
    Returns dict keyed by stem (e.g., '5gyr', '13gyr').
    """
    directory = Path(directory)
    out: Dict[str, DartmouthIsochrone] = {}
    for p in sorted(directory.glob("*.iso")):
        out[p.stem] = read_dartmouth_iso(p)
    return out