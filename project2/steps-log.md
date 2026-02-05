## 1. Downloaded isochrones according to instructions docuent
Downloaded from https://rcweb.dartmouth.edu/stellar/isolf_new.html

Isochrones downloaded:
- 13 Gyr, [Fe/H]=-1.8, [alpha/Fe]=+0.2
- 5 Gyr, [Fe/H]=-0.5, [alpha/Fe]=0.0

Both isochrones generated with cubic interpolation, default Helium mass fraction Y=0.245+1.5*Z, and color set to SDSS ugriz

## 2. Downloaded SDSS data via SQL query
Self-explanatory. Used coordinates suggested in instructions doc

Created Jupyter notebook. Used AI to generate code that reads in isochrone files and SDSS data. Plotted both data on CMD space separately. Then introduced dereddening to SDSS data and distance-correction to isochrone curves.