## 1. Downloaded isochrones according to instructions docuent
Downloaded from https://rcweb.dartmouth.edu/stellar/isolf_new.html

Isochrones downloaded:
- 13 Gyr, [Fe/H]=-1.8, [alpha/Fe]=+0.2
- 5 Gyr, [Fe/H]=-0.5, [alpha/Fe]=0.0

Both isochrones generated with cubic interpolation, default Helium mass fraction Y=0.245+1.5*Z, and color set to SDSS ugriz

## 2. Downloaded SDSS data via SQL query
Self-explanatory. Used coordinates suggested in instructions doc. First crafted a SQL query to just to download the target field.

Then, used AI to generate several random coordinates for "control" fields to compare against. Created a Jupyter notebook that converts these control field coordinates from J2000 RA/Dec to galactic coordinates to ensure same galactic latitude across all fields. This was done so as to control for the relative abundance in disk vs halo stars.

Multiple SQL queries were made via API request to SDSS server for target and control fields. Fields were saved as separate CSVs.

## 3. Plotted field data and used chi-squared filtering to compute population membership
Created Jupyter notebook. Plotted both data on CMD space separately. Then introduced dereddening to SDSS data and distance-correction to isochrone curves. This was done as a sanity check to make sure there are no readily apparent artifacts or anomalies in data.

After excluding dim stars and high-uncertainty stars, defined a function that calculates chi-squared distance in color-magnitude space from isochrone points. Plotted stars that were within 2-sigma chi-squared distances from any isochrone point. Repeated this for control fields that were taken from SDSS database with the same galactic latitude. Computed sample statistics in proportions of candidate stream stars across fields. 

This process was repeated in a separate Jupyter notebook to use a simpler metric where a candidate stream star was defined as a star that simply had its error box overlap with the the isochrone curves. Similar summary statistics were computed using this sampling method.

Both methods showed a significant overdensity in the target region, which suggests the presence of stream stars.

Additionally, code was written to generate Hess diagrams for both target and control fields. Then a residual plot was created, which reveals that there appears to be a statistical overdensity that follows the general shape of the isochrones in the MSTO region. 

Finally, AI was used to clean up code.