# sdss_loader.py
from __future__ import annotations
import pandas as pd
from pathlib import Path


def load_sdss_csv(path: str | Path) -> pd.DataFrame:
    """
    Load SDSS CSV exported from SkyServer.

    Handles:
    - "#Table1" first line
    - correct numeric parsing
    - dereddened magnitudes
    - useful colors for CMD work
    """

    path = Path(path)

    # Skip first line "#Table1"
    df = pd.read_csv(path, comment="#")

    # Ensure numeric (sometimes CSV loads as strings)
    numeric_cols = [
        "ra","dec",
        "psfMag_u","psfMag_g","psfMag_r","psfMag_i","psfMag_z",
        "psfMagErr_u","psfMagErr_g","psfMagErr_r","psfMagErr_i","psfMagErr_z",
        "extinction_u","extinction_g","extinction_r","extinction_i","extinction_z"
    ]

    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------------------------------
    # Deredden magnitudes (critical step)
    # -------------------------------------------------
    df["u0"] = df["psfMag_u"] - df["extinction_u"]
    df["g0"] = df["psfMag_g"] - df["extinction_g"]
    df["r0"] = df["psfMag_r"] - df["extinction_r"]
    df["i0"] = df["psfMag_i"] - df["extinction_i"]
    df["z0"] = df["psfMag_z"] - df["extinction_z"]

    # -------------------------------------------------
    # Colors for CMDs
    # -------------------------------------------------
    df["g_r"] = df["g0"] - df["r0"]
    df["g_i"] = df["g0"] - df["i0"]
    df["r_i"] = df["r0"] - df["i0"]

    return df