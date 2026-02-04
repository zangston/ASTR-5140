-- 1° x 1° box centered on (RA,Dec) = (32.405833, -4.642111)
-- RA range:  [31.905833, 32.905833]
-- Dec range: [-5.142111, -4.142111]

SELECT
    p.objid,
    p.ra, p.dec,
    p.psfMag_u, p.psfMag_g, p.psfMag_r, p.psfMag_i, p.psfMag_z,     -- Magnitudes
    p.psfMagErr_u, p.psfMagErr_g, p.psfMagErr_r, p.psfMagErr_i, p.psfMagErr_z,      -- Errors
    p.extinction_u, p.extinction_g, p.extinction_r, p.extinction_i, p.extinction_z,     -- Extinction
    p.type,      -- 6 = STAR
    p.mode       -- 1 = PRIMARY (unique object)
FROM PhotoObjAll AS p
WHERE 
    p.ra BETWEEN 31.905833 AND 32.905833 
    AND p.dec BETWEEN -5.142111 AND -4.142111
    AND p.type = 6
    AND p.mode = 1
    AND p.clean = 1