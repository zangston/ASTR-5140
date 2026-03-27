SELECT
    gaia.source_id,
    gaia.ra,
    gaia.dec,
    gaia.parallax,
    gaia.parallax_error,
    gaia.pmra,
    gaia.pmra_error,
    gaia.pmdec,
    gaia.pmdec_error,
    gaia.phot_g_mean_mag,
    gaia.phot_bp_mean_mag,
    gaia.phot_rp_mean_mag,
    gaia.bp_rp,
    gaia.ruwe,
    gaia.radial_velocity,
    gaia.radial_velocity_error,
    gaia.astrometric_excess_noise,
    gaia.astrometric_gof_al,
    gaia.visibility_periods_used
FROM gaiadr3.gaia_source AS gaia
WHERE 1 = CONTAINS(
    POINT('ICRS', gaia.ra, gaia.dec),
    CIRCLE('ICRS', 15.8094167, -70.8487778, 0.5)
)