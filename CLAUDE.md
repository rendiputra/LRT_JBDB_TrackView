# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LRT Jabodebek (Jakarta-Bogor-Depok-Bekasi) Live Tracker** — a web visualization of Jakarta's LRT system showing real-time train positions, schedules, and station information based on GAPEKA timing data. The app uses Leaflet for mapping and simulates train movements based on GAPEKA timing data.

## Project Structure

```
visualisasi-lrt/
├── public/                 # Static files served by web server
│   ├── index.html          # Main application
│   ├── export.geojson      # Raw OpenStreetMap LRT track data
│   ├── rute_lrt_siap_pakai.geojson  # Processed route segments
│   ├── schedule_data.json           # Weekend schedule (270 trips)
│   ├── schedule_data_weekdays.json  # Weekday schedule (430 trips)
│   └── hari_libur/
│       └── hari_libur2026.json  # Indonesian national holidays
├── build/                 # Build scripts
│   ├── build_routes.py    # Generate route segments from OSM data
│   ├── build_schedule.py  # Parse raw schedules into JSON
│   └── potong_jalur.js   # Legacy Node.js script (deprecated)
├── data/                  # Raw data (source files)
│   ├── raw_b.txt          # Bekasi line weekend schedule
│   ├── raw_c.txt          # Cibubur line weekend schedule
│   ├── raw_d.txt          # Bekasi line weekday schedule
│   └── raw_e.txt          # Cibubur line weekday schedule
├── package.json
└── CLAUDE.md
```

## Commands

### Development
```bash
# Serve the visualization (serves public/ folder)
python -m http.server 8000
# Then open http://localhost:8000
```

### Data Processing
```bash
# Generate route segments from raw OSM data
python3 build/build_routes.py

# Build schedule data from raw text files
python3 build/build_schedule.py
```

### Testing
No formal test suite exists. Manual testing by serving the app and interacting with the map.

## Architecture

### Two-Line System
The LRT Jabodebek consists of two lines sharing the main section between Dukuh Atas and Cawang:
- **Cibubur Line** (cyan `#00c8ff`): Harjamukti ↔ Dukuh Atas via Cawang
- **Bekasi Line** (orange `#ff9900`): Jatimulya ↔ Dukuh Atas via Cawang
- **Main Line** (purple `#a855f7`): Dukuh Atas ↔ Cawang (shared by both lines)

### Station Network (18 stations)
- Shared: Dukuh Atas, Setiabudi, Rasuna Said, Kuningan, Pancoran, Cikoko, Ciliwung, Cawang
- Cibubur branch: Taman Mini (TMII), Kampung Rambutan, Ciracas, Harjamukti
- Bekasi branch: Halim, Jatibening Baru, Cikunir 1, Cikunir 2, Bekasi Barat, Jatimulya

### Data Flow
1. `data/` — Raw source files (schedule text, OSM export)
2. `build/build_routes.py` — Chains OSM ways into route segments with station snapping
3. `public/rute_lrt_siap_pakai.geojson` — Processed per-segment LineString features
4. `build/build_schedule.py` — Parses raw schedules into schedule JSON files
5. `public/schedule_data*.json` — Parsed schedule data (weekdays/weekends)
6. `public/index.html` — Main app, auto-selects weekdays/weekends based on date

### Schedule Selection Logic
The app automatically selects the appropriate schedule based on the current date:
- **Weekdays schedule**: Monday-Friday (non-holiday)
- **Weekends schedule**: Saturday, Sunday, and public holidays

Holiday data is loaded from `public/hari_libur/hari_libur2026.json`.

### Key Data Structures

**Route Segments** (`public/rute_lrt_siap_pakai.geojson`):
```json
{
  "properties": {
    "id": "dukuh_to_cibubur:dukuh_atas_TO_setiabudi",
    "route": "dukuh_to_cibubur",
    "from": "dukuh_atas",
    "to": "setiabudi"
  }
}
```

**Station Config** (inline in `index.html`):
```javascript
STATIONS = { station_id: { name, lat, lon, lines: ["main"|"cibubur"|"bekasi"] } }
ROUTES = { route_name: ["station_id", ...] }
TRAVEL_TIMES = { "station_a_station_b": minutes }
```

**Train Timings** (loaded from schedule JSON):
```javascript
{ id, route, line, direction, origin, dest, color,
  timings: [{ stationId, arriveAt, departAt }] } // times in seconds from midnight
```

### Position Calculation
1. Simulation time tracked in seconds-from-midnight
2. For each train, `getTrainState()` finds current segment between station timings
3. Between stations: interpolate along `ROUTE_SEGMENTS[route][segmentKey]` using cumulative distance
4. During dwell: snap to station coordinates

### Track Construction (`build/build_routes.py`)
Manually chains OSM way IDs into dual-track geometries. Track A = Dukuh Atas→Cawang direction, Track B = reverse. Branches split at Cawang junction.

## Common Modifications

**Add a new station**: Update `STATIONS` object and both `ROUTES` arrays in `index.html`, plus `build/build_routes.py` STATIONS dict.

**Adjust travel times**: Edit `TRAVEL_TIMES` in `index.html` (keys are bidirectional, e.g., `dukuh_atas_setiabudi`).

**Update schedule**: Edit `data/raw_*.txt` files, then run `python3 build/build_schedule.py`

**Modify track geometry**: Update way ID chains in `build/build_routes.py`, then regenerate `public/rute_lrt_siap_pakai.geojson`.
