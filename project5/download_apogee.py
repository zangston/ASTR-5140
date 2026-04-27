import requests
from tqdm import tqdm

url = "https://data.sdss.org/sas/dr17/apogee/spectro/aspcap/dr17/synspec_rev1/allStarLite-dr17-synspec_rev1.fits"
output_file = "allStarLite-dr17.fits"

# Stream download in chunks
with requests.get(url, stream=True) as r:
    r.raise_for_status()
    total_size = int(r.headers.get('content-length', 0))

    with open(output_file, "wb") as f, tqdm(
        total=total_size,
        unit='B',
        unit_scale=True,
        desc="Downloading APOGEE DR17"
    ) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

print(f"\nSaved to {output_file}")