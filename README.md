# Toronto Road Safety Dashboard

An interactive web map analyzing traffic collision patterns in Toronto in relation to traffic signals, bike lanes, neighbourhoods, and schools  built with the **ArcGIS API for Python** and the **ArcGIS API for JavaScript**.

🔗 **[Live Demo](https://cleisonpaiva.github.io/toronto-road-safety-dashboard/)**
🇧🇷 [Versão em Português](README.pt-br.md)

---

## Overview

This project analyzes ~120,000 traffic collision records from the Toronto Police Service (last 2 years) across four spatial dimensions:

| Analysis | Method | Buffer Distance | Justification |
|---|---|---|---|
| Collisions × Traffic Signals | Point buffer + spatial join | 50m | Common range for intersection-proximity studies in road safety literature |
| Collisions × Bike Lanes | Line buffer + spatial join | 25m | Typical urban road width in Toronto; avoids false positives from parallel streets |
| Collisions × Neighbourhoods | Point-in-polygon join | N/A | Neighbourhoods are mutually exclusive administrative boundaries  no buffer needed |
| Collisions × Schools | Point buffer + spatial join | 150m | Legally defined "school safety zone" under Ontario's Highway Traffic Amendment Act (Bill 90, 2016) |

The result is published as GeoJSON layers, rendered in a Leaflet-free, pure ArcGIS JS API map using an OpenStreetMap basemap  avoiding any ArcGIS Online credit consumption.

## Why this project exists

I'm a full-stack developer (PHP/Laravel, C#/.NET, React) relocating to Toronto to work as a GIS Developer. This project served two purposes: learning the ArcGIS API for Python hands-on, and producing a demonstrable, end-to-end artifact  from raw government open data to a published interactive map  for technical interviews.

## Architecture
Data Sources (ArcGIS Hub, CKAN, live City GIS services)
↓
Ingestion (src/road_safety/ingestion/)
↓
Cleaning & Validation (bounding-box + geometry checks)
↓
Spatial Analysis (src/road_safety/analysis/)  buffers, spatial joins
↓
Export to GeoJSON (src/road_safety/export/)
↓
Static Web Map (docs/)  ArcGIS API for JavaScript + OpenStreetMap

## Data Sources

| Dataset | Source | Technology | Notes |
|---|---|---|---|
| Collisions | Toronto Police Service Public Safety Data Portal | ArcGIS Hub (Item ID lookup) | Actively updated; ~809K total records, filtered to a fixed 2-year window for reproducibility |
| Traffic Signals | City of Toronto Open Data Portal | CKAN API | The `open.toronto.ca` landing page shows "Retired," but the underlying CKAN dataset is actively maintained  verified via metadata inspection, not assumption |
| Bike Lanes | City of Toronto GIS (`gis.toronto.ca`) | Live ArcGIS FeatureServer | Chosen over the Open Data Portal's static "Cycling Network" file, which is explicitly marked "Will not be Refreshed" |
| Neighbourhoods (158) | City of Toronto Open Data Portal | CKAN API | Official current 158-neighbourhood boundary scheme |
| Schools | City of Toronto GIS (`gis.toronto.ca`) | Live ArcGIS FeatureServer | Includes all education levels (elementary through university) |

## Key Methodological Findings

This project surfaced two data-quality issues that were investigated rather than dismissed  both are documented in code (see `tests/`) as regression guards:

1. **Bounding box correction.** An initial approximate Toronto bounding box was silently discarding valid records in Scarborough (Morningside Heights, West Rouge). Root cause: the box was hand-estimated rather than derived from data. Fix: the true envelope was computed from the official 158-neighbourhood boundaries themselves.

2. **Neighbourhood boundary divergence.** A manual spatial join (point-in-polygon against current boundaries) was compared against the `NEIGHBOURHOOD_158` field already present in the collisions dataset. Agreement was only 83%. Investigation showed the divergence clusters into specific neighbourhood-pair blocks repeated hundreds of times  not random border noise  indicating the two datasets reference different vintages of the boundary scheme (boundaries have been redrawn/subdivided over time), not geometric error.

## Known Limitations

- Collision data reflects a fixed 2-year window (see `EXTRACTION_REFERENCE_DATE` in `ingestion/collisions.py`); results will not update automatically and would need re-extraction to reflect newer data.
- The `NEIGHBOURHOOD_158` field pre-existing in the collisions dataset diverges ~17% from a fresh spatial join against current boundaries (see finding #2 above). This project's neighbourhood assignment uses the current, freshly-joined boundaries as the source of truth.
- Buffer distances are reasoned estimates (or, for schools, a legislated value)  not derived from a formal traffic-engineering study.
- No publication to ArcGIS Online / Feature Layers  a deliberate decision to avoid consuming organizational credits. Results are served as static GeoJSON instead.

## Tech Stack

- **Python 3.12**, [ArcGIS API for Python](https://developers.arcgis.com/python/) 2.4.3, pandas
- **ArcGIS API for JavaScript** 4.29, OpenStreetMap basemap
- **pytest** for automated testing
- **conda** for environment management

## Project Structure
```
toronto-road-safety-dashboard/
├── config/                  # Environment variables (not committed)
├── data/
│   ├── raw/                 # Raw ingested data (gitignored)
│   ├── processed/           # Cleaned/analyzed data (gitignored)
│   └── geojson/             # Exported GeoJSON (pipeline staging)
├── docs/                    # Published static web map (GitHub Pages root)
│   ├── assets/
│   │   ├── icons/           # Custom SVG map markers
│   │   │── style            # CSS style
│   │   └── map-config.js    # Map layers, renderers, popups
│   ├── data/                # GeoJSON consumed by the map
│   └── index.html
├── notebooks/
│   └── final_verification.ipynb
├── src/road_safety/
│   ├── ingestion/            # Data source connectors + cleaning
│   ├── analysis/              # Spatial analyses (buffer, join, aggregation)
│   ├── export/                 # GeoJSON export + publish-to-docs
│   └── auth.py                 # OAuth 2.0 authentication (ArcGIS Online)
├── tests/                    # pytest suite
└── environment.yml
```

## Running the Project

```bash
# 1. Create and activate the environment
conda env create -f environment.yml
conda activate geospatial

# 2. Configure credentials
cp config/.env.example config/.env
# fill in ARCGIS_PORTAL_URL and ARCGIS_CLIENT_ID

# 3. Run the pipeline
python src/road_safety/ingestion/collisions.py
python src/road_safety/ingestion/traffic_signals.py
python src/road_safety/ingestion/bike_lanes.py
python src/road_safety/ingestion/neighbourhoods.py
python src/road_safety/ingestion/schools.py
python src/road_safety/ingestion/cleaning.py

python src/road_safety/analysis/traffic_signals.py
python src/road_safety/analysis/bike_lanes.py
python src/road_safety/analysis/neighbourhoods.py
python src/road_safety/analysis/schools.py

python src/road_safety/export/export.py

# 4. Serve the map locally
cd docs
python -m http.server 8000
# open http://localhost:8000
```

## Testing

```bash
pytest tests/ -v
```

9 tests covering geometry validation, bounding-box edge cases, spatial join logic, storage round-trips, and the neighbourhood-boundary comparison.

## Author

**Cleison Mendes Paiva**  [GitHub](https://github.com/CleisonPaiva) · [LinkedIn](https://www.linkedin.com/in/paiva-cleison)
