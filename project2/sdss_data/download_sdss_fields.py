#!/usr/bin/env python3
"""
Download SDSS photometry for multiple 1°×1° fields (target + controls),
saving each field as an individual CSV.

Uses SDSS SkyServer SQL web service:
  https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch?cmd=...&format=csv
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import List
from urllib.parse import urlencode

import requests


# ---------- CONFIG ----------
DATA_RELEASE = "dr17"
BASE_URL = f"https://skyserver.sdss.org/{DATA_RELEASE}/SkyServerWS/SearchTools/SqlSearch"

OUTDIR = Path("sdss_data/fields")
OUTDIR.mkdir(parents=True, exist_ok=True)

# Target field center
RA0 = 32.405833
DEC0 = -4.642111
HALF_SIZE_DEG = 0.5  # 1°×1° box

# 30 controls: 15 on each side, step 2° => ±2, ±4, ..., ±30
CONTROL_STEP_DEG = 2
N_PER_SIDE = 15  # 15 negative + 15 positive = 30 controls

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


def wrap_ra(ra: float) -> float:
    """Wrap RA into [0, 360)."""
    return ra % 360.0


def make_box(field_id: str, ra_center: float, dec_center: float, half_size: float) -> FieldBox:
    ra_center = wrap_ra(ra_center)
    ra_min = ra_center - half_size
    ra_max = ra_center + half_size

    # keep dec normal (no wrap)
    dec_min = dec_center - half_size
    dec_max = dec_center + half_size

    # store raw ra_min/ra_max (may be <0 or >360); handle in SQL
    return FieldBox(field_id=field_id, ra_min=ra_min, ra_max=ra_max, dec_min=dec_min, dec_max=dec_max)

def build_sql(box: FieldBox) -> str:
    # RA condition with wrap handling
    if box.ra_min < 0:
        # e.g. ra BETWEEN 0 and ra_max OR ra BETWEEN 360+ra_min and 360
        ra_cond = f"(p.ra BETWEEN 0 AND {box.ra_max:.6f} OR p.ra BETWEEN {360.0+box.ra_min:.6f} AND 360)"
    elif box.ra_max >= 360:
        ra_cond = f"(p.ra BETWEEN {box.ra_min:.6f} AND 360 OR p.ra BETWEEN 0 AND {box.ra_max-360.0:.6f})"
    else:
        ra_cond = f"(p.ra BETWEEN {box.ra_min:.6f} AND {box.ra_max:.6f})"

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
    {ra_cond}
AND p.dec BETWEEN {box.dec_min:.6f} AND {box.dec_max:.6f}
AND p.type = 6
AND p.mode = 1
AND p.clean = 1
{EXTRA_WHERE}
"""
    return " ".join(sql.split())


def fetch_csv(sql: str, outfile: Path, timeout: int = 300) -> None:
    params = {"cmd": sql, "format": "csv"}
    url = f"{BASE_URL}?{urlencode(params)}"
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    outfile.write_bytes(r.content)


def main() -> None:
    fields: List[FieldBox] = []

    # Target
    fields.append(make_box("target", RA0, DEC0, HALF_SIZE_DEG))

    # Controls
    '''
    offsets = [CONTROL_STEP_DEG * i for i in range(1, N_PER_SIDE + 1)]
    offsets = [-o for o in offsets] + offsets  # 15 negative + 15 positive

    for off in offsets:
        tag = f"ra_{'p' if off > 0 else 'm'}{abs(off):02d}"  # ra_m02, ra_p30, etc
        fields.append(make_box(tag, RA0 + off, DEC0, HALF_SIZE_DEG))
    '''
    # Controls chosen far away but with similar Galactic latitude (precomputed)
    CONTROL_CENTERS = [
        ("glon_080", 353.381110, -4.590060),
        ("glon_085", 355.375477, -3.178909),
        ("glon_090", 357.466454, -1.919136),
        ("glon_095", 359.644412, -0.819254),
        ("glon_100",   1.898647,  0.113008),
        ("glon_105",   4.217379,  0.870862),
        ("glon_110",   6.587807,  1.448624),
        ("glon_115",   8.996243,  1.841851),
        ("glon_120",  11.428305,  2.047465),
        ("glon_125",  13.869163,  2.063840),
        ("glon_130",  16.303813,  1.890845),
        ("glon_135",  18.717374,  1.529851),
        ("glon_140",  21.095369,  0.983691),
    ]

    for field_id, ra_c, dec_c in CONTROL_CENTERS:
        fields.append(make_box(field_id, ra_c, dec_c, HALF_SIZE_DEG))

    print(f"Downloading {len(fields)} fields ({len(fields)-1} controls) from {BASE_URL}")
    print(f"Output directory: {OUTDIR.resolve()}")
    print()

    for i, box in enumerate(fields, start=1):
        sql = build_sql(box)
        outfile = OUTDIR / f"sdss_{box.field_id}.csv"
        print(f"[{i:02d}/{len(fields):02d}] {box.field_id}: "
              f"RA[{box.ra_min:.3f},{box.ra_max:.3f}] Dec[{box.dec_min:.3f},{box.dec_max:.3f}] -> {outfile.name}")

        try:
            fetch_csv(sql, outfile)
        except requests.HTTPError as e:
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