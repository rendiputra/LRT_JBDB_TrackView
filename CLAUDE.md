# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LRT Jabodebek (Jakarta-Bogor-Depok-Bekasi) Live Tracker** — a web visualization of Jakarta's LRT system showing real-time train positions, schedules, and station information based on GAPEKA timing data. The app uses Leaflet for mapping and simulates train movements based on GAPEKA timing data.

## Commands

### Development
```bash
# Serve the visualization (required for fetch API to work)
python -m http.server 8000
# Then open http://localhost:8000

# Install Node.js dependencies (for legacy potong_jalur.js script)
npm install
```

### Data Processing
```bash
# Generate route segments from raw OSM data
python build_routes.py

# Build schedule data from raw text files
python build_schedule.py

# Legacy scripts (require Node.js)
node potong_jalur.js
node build_routes.js
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
1. `export.geojson` — Raw OpenStreetMap track data (dual tracks)
2. `build_routes.py` — Chains OSM ways into route segments with station snapping
3. `rute_lrt_siap_pakai.geojson` — Processed per-segment LineString features with route metadata
4. `raw_b.txt`, `raw_c.txt` — Raw schedule data (Run ID, direction, times per station)
5. `build_schedule.py` — Parses raw schedules into `schedule_data.json`
6. `index.html` — Loads GeoJSON routes, generates full-day schedule simulation

### Key Data Structures

**Route Segments** (`rute_lrt_siap_pakai.geojson`):
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

**Train Timings** (generated at runtime):
```javascript
{ id, route, line, direction, origin, dest, color,
  timings: [{ stationId, arriveAt, departAt }] } // times in seconds from midnight
```

### Position Calculation
1. Simulation time tracked in seconds-from-midnight
2. For each train, `getTrainState()` finds current segment between station timings
3. Between stations: interpolate along `ROUTE_SEGMENTS[route][segmentKey]` using cumulative distance
4. During dwell: snap to station coordinates

### Track Construction (`build_routes.py`)
Manually chains OSM way IDs into dual-track geometries. Track A = Dukuh Atas→Cawang direction, Track B = reverse. Branches split at Cawang junction.

## File Purposes

| File | Purpose |
|------|---------|
| `index.html` | Main application — map, train tracking, schedule simulation |
| `build_routes.py` | Build clean route segments from raw OSM GeoJSON |
| `build_schedule.py` | Parse raw schedule text → `schedule_data.json` |
| `potong_jalur.js` | Legacy Node.js segment cutter (replaced by Python) |
| `export.geojson` | Raw OpenStreetMap LRT track data |
| `rute_lrt_siap_pakai.geojson` | Processed route segments for map display |
| `schedule_data.json` | Parsed schedule data (generated, not source) |
| `raw_b.txt`, `raw_c.txt` | Source schedule data for Bekasi/Cibubur lines |

## Common Modifications

**Add a new station**: Update `STATIONS` object and both `ROUTES` arrays in `index.html`, plus `build_routes.py` STATIONS dict.

**Adjust travel times**: Edit `TRAVEL_TIMES` in `index.html` (keys are bidirectional, e.g., `dukuh_atas_setiabudi`).

**Change schedule interval**: Edit loop parameters in `generateSchedule()` ( Cibubur: 15min, Bekasi: 20min).

**Modify track geometry**: Update way ID chains in `build_routes.py`, then regenerate `rute_lrt_siap_pakai.geojson`.