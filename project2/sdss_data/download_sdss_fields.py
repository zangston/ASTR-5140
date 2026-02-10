#!/usr/bin/env python3
"""
Download SDSS photometry for multiple 1°×1° fields (target + controls),
saving each field as an individual CSV.

Uses SDSS SkyServer SQL web service:
  https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch?cmd=...&format=csv
(Endpoint pattern is widely used; see examples in SDSS/SciServer docs and tutorials.)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlencode

import requests


# ---------- CONFIG ----------
DATA_RELEASE = "dr17"  # change if your class requires a specific release
BASE_URL = f"https://skyserver.sdss.org/{DATA_RELEASE}/SkyServerWS/SearchTools/SqlSearch"

OUTDIR = Path("sdss_data/fields")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Your target field center (from assignment)
RA0 = 32.405833
DEC0 = -4.642111
HALF_SIZE_DEG = 0.5  # 1°×1° box

# Controls: RA offsets (deg) at same Dec
RA_OFFSETS = [-15, -10, -5, 5, 10, 15]

# Sleep between requests so you don't hammer the server
SLEEP_SECONDS = 1.0

# Optional: add a light SQL cut to keep files smaller (uncomment if needed)
# EXTRA_WHERE = "AND p.psfMag_r BETWEEN 14 AND 22.2"
EXTRA_WHERE = ""


@dataclass(frozen=True)
class FieldBox:
    field_id: str
    ra_min: float
    ra_max: float
    dec_min: float
    dec_max: float


def make_box(field_id: str, ra_center: float, dec_center: float, half_size: float) -> FieldBox:
    return FieldBox(
        field_id=field_id,
        ra_min=ra_center - half_size,
        ra_max=ra_center + half_size,
        dec_min=dec_center - half_size,
        dec_max=dec_center + half_size,
    )


def build_sql(box: FieldBox) -> str:
    # Using PhotoPrimary is usually cleaner than PhotoObjAll for CMD work.
    # Keep the query simple; do quality cuts in Python.
    sql = f"""
SELECT
    p.objid,
    p.ra, p.dec,
    p.psfMag_u, p.psfMag_g, p.psfMag_r, p.psfMag_i, p.psfMag_z,
    p.psfMagErr_u, p.psfMagErr_g, p.psfMagErr_r, p.psfMagErr_i, p.psfMagErr_z,
    p.extinction_u, p.extinction_g, p.extinction_r, p.extinction_i, p.extinction_z,
    p.type,
    p.mode
FROM PhotoPrimary AS p
WHERE
    p.ra  BETWEEN {box.ra_min:.6f} AND {box.ra_max:.6f}
AND p.dec BETWEEN {box.dec_min:.6f} AND {box.dec_max:.6f}
AND p.type = 6
AND p.mode = 1
{EXTRA_WHERE}
"""
    # SkyServer is fine with newlines, but we'll strip extra whitespace to be safe.
    return " ".join(sql.split())


def fetch_csv(sql: str, outfile: Path, timeout: int = 300) -> None:
    params = {"cmd": sql, "format": "csv"}
    url = f"{BASE_URL}?{urlencode(params)}"

    r = requests.get(url, timeout=timeout)
    r.raise_for_status()

    # SkyServer CSV often begins with "#Table1" comment line; keep it.
    outfile.write_bytes(r.content)


def main() -> None:
    fields: List[FieldBox] = []

    # Target
    fields.append(make_box("target", RA0, DEC0, HALF_SIZE_DEG))

    # Controls (RA offsets)
    for off in RA_OFFSETS:
        tag = f"ra_{'p' if off > 0 else 'm'}{abs(off)}"
        fields.append(make_box(tag, RA0 + off, DEC0, HALF_SIZE_DEG))

    print(f"Downloading {len(fields)} fields from {BASE_URL}")
    print(f"Output directory: {OUTDIR.resolve()}")
    print()

    for i, box in enumerate(fields, start=1):
        sql = build_sql(box)
        outfile = OUTDIR / f"sdss_{box.field_id}.csv"
        print(f"[{i}/{len(fields)}] {box.field_id}: "
              f"RA[{box.ra_min:.3f},{box.ra_max:.3f}] Dec[{box.dec_min:.3f},{box.dec_max:.3f}] -> {outfile.name}")

        try:
            fetch_csv(sql, outfile)
        except requests.HTTPError as e:
            # Save the SQL that failed for debugging
            debug_sql = OUTDIR / f"FAILED_{box.field_id}.sql.txt"
            debug_sql.write_text(sql)
            print(f"  ERROR: {e}\n  Saved failing SQL to: {debug_sql.name}")
        except Exception as e:
            debug_sql = OUTDIR / f"FAILED_{box.field_id}.sql.txt"
            debug_sql.write_text(sql)
            print(f"  ERROR: {e}\n  Saved failing SQL to: {debug_sql.name}")

        time.sleep(SLEEP_SECONDS)

    print("\nDone.")


if __name__ == "__main__":
    main()