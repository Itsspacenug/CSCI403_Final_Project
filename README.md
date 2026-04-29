# Colorado Snowpack Analysis
### CSCI 403 – Database Management | Final Project

> Analyzing historical Colorado snowpack trends using SNOTEL station data, NOAA climate indices, and USGS streamflow records stored in PostgreSQL.

---

## Project Overview

This project collects and analyzes decades of Colorado snowpack data to answer questions like:

- Is Colorado's snowpack declining over time, and does it vary by basin?
- Do El Niño and La Niña years produce measurably different snowpack levels?
- How well does April 1st snow water equivalent (SWE) predict summer river runoff?

All data is stored in a normalized PostgreSQL schema and analyzed entirely through SQL — using CTEs, window functions, and multi-table joins across four interrelated datasets.

---

## Datasets

| Source | Description | Rows (approx.) | Link |
|--------|-------------|----------------|------|
| NRCS SNOTEL | Daily SWE, precipitation, temperature, snow depth from 114 Colorado stations (1980–present) | ~1.6 million | https://wcc.sc.egov.usda.gov/reportGenerator/ |
| NOAA Climate Indices | Monthly ONI (El Niño) and PDO index values | ~1,000 | https://psl.noaa.gov/data/climateindices/list/ |
| USGS Streamflow | Daily river discharge for 5 key Colorado gauges | ~82,000 | https://waterdata.usgs.gov/co/nwis/sw |

All datasets are in the public domain and accessed free of charge.

---

## Database Schema

```
stations              (114 rows)
  station_id PK
  station_name, elevation_ft, latitude, longitude, county, huc, begin_date, end_date

daily_observations    (~1.6M rows)
  obs_id PK
  station_id FK → stations
  obs_date, swe_in, precip_in, temp_max_f, temp_min_f, temp_avg_f, snow_depth_in

climate_indices       (~1,000 rows)
  year, month PK
  oni, pdo

streamflow            (~82,000 rows)
  flow_id PK
  site_no, site_name, flow_date, discharge_cfs
```

---

## Project Structure

```
.
├── collect_snowpack_data.py   # Data collection script (downloads all CSVs)
├── schema.sql                 # PostgreSQL CREATE TABLE statements
├── example_queries.sql        # Complex queries for analysis
├── snowpack_data/
│   ├── stations.csv
│   ├── daily_observations.csv
│   ├── climate_indices.csv
│   └── streamflow.csv
└── README.md
```

---

## Setup & Installation

### 1. Install dependencies
```bash
pip install requests pandas
```

### 2. Collect all data
```bash
python collect_snowpack_data.py
```
This downloads all four datasets and writes them as CSVs to `./snowpack_data/`.

### 3. Load into PostgreSQL
```bash
psql -U <your_user> -d <your_db>
```
Then inside psql:
```sql
\i schema.sql
\COPY stations            FROM 'snowpack_data/stations.csv'            CSV HEADER;
\COPY daily_observations  FROM 'snowpack_data/daily_observations.csv'  CSV HEADER;
\COPY climate_indices     FROM 'snowpack_data/climate_indices.csv'     CSV HEADER;
\COPY streamflow          FROM 'snowpack_data/streamflow.csv'          CSV HEADER;
```

---

## Component 3 Deliverables

### Data Loading & Cleaning
SNOTEL data contains sensor malfunctions, missing values flagged with sentinel values (-99.9), and occasional duplicate records from telemetry backfill. Cleaning steps are documented in `schema.sql` and include null filtering, outlier detection by elevation band, and deduplication on `(station_id, obs_date)`.

### Database Schema Design
Four tables in 3NF with foreign key constraints, check constraints on `climate_indices.month`, and unique constraints on observation records. Schema diagram and normalization justification included in the Artifact Self-Assessment.

### Interesting / Complex Queries
Three core analyses in `example_queries.sql`:
1. **Year-over-year SWE trend by basin** — window functions for rolling 10-year averages and lag-based year-over-year change
2. **ENSO phase vs. statewide April 1 SWE** — CTE joining snowpack aggregates to winter ONI averages, classifying El Niño / La Niña / Neutral years
3. **SWE-to-streamflow lag** — identifies how many days after peak snowpack peak runoff occurs, by year

### Data Visualization
Planned visualizations:
- Line chart: statewide mean April 1 SWE by year (1980–present) with ENSO phase color-coded
- Heatmap: peak SWE by basin × decade
- Scatter plot: April 1 SWE vs. summer streamflow volume by gauge

---

## Key Questions Answered

| Question | Method |
|----------|--------|
| Is snowpack declining statewide? | Window function rolling average over `daily_observations` |
| Which basins are most affected? | GROUP BY `stations.huc`, year-over-year trend |
| Do El Niño years reduce snowpack? | JOIN `climate_indices` on year/month, compare by ENSO phase |
| Does SWE predict summer runoff? | JOIN `streamflow` on date, compute peak-to-peak lag |

---

## Data Sources & Licensing

- **NRCS SNOTEL**: Public domain, USDA Natural Resources Conservation Service. Accessed April 2026.
- **NOAA Climate Indices**: Public domain, NOAA Physical Sciences Laboratory. Accessed April 2026.
- **USGS Streamflow**: Public domain, U.S. Geological Survey. Accessed April 2026.
