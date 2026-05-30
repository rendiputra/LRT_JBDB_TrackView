# LRT Jabodebek Live Tracker

A real-time visualization of Jakarta's LRT (Light Rail Transit) Jabodebek system showing train positions, schedules, and station information. The app simulates train movements based on official GAPEKA timing data.

**Live Demo:** [http://localhost:8000](http://localhost:8000) (requires local server)

![LRT Jabodebek Tracker](https://via.placeholder.com/800x400/0a0e17/00d4aa?text=LRT+Jabodebek+Live+Tracker)

## Features

- **Real-time Train Tracking** - Animated train positions along the LRT lines based on GAPEKA schedules
- **Dual-Line System** - Cibubur Line (cyan) and Bekasi Line (orange) with shared main section
- **18 Stations** - Interactive station markers with arrival information
- **Automatic Schedule Selection** - Automatically selects weekdays or weekends/holidays schedule based on current date
- **Speed Control** - Adjustable time simulation speed (0.5x to 120x)
- **Interactive Map** - Built with Leaflet.js using CartoDB dark tiles

## System Overview

The LRT Jabodebek consists of two lines sharing the main section between Dukuh Atas and Cawang:

| Line | Color | Route |
|------|-------|-------|
| Cibubur Line | Cyan `#00c8ff` | Harjamukti - Dukuh Atas |
| Bekasi Line | Orange `#ff9900` | Jatimulya - Dukuh Atas |
| Main Line | Purple `#a855f7` | Dukuh Atas - Cawang (shared) |

### Station Network

**Shared Stations (8):** Dukuh Atas, Setiabudi, Rasuna Said, Kuningan, Pancoran, Cikoko, Ciliwung, Cawang

**Cibubur Branch (4):** Taman Mini (TMII), Kampung Rambutan, Ciracas, Harjamukti

**Bekasi Branch (6):** Halim, Jatibening Baru, Cikunir 1, Cikunir 2, Bekasi Barat, Jatimulya

## Data Sources

Schedule data is sourced from official GAPEKA timing published by **LRT Jabodebek** via their official Instagram account [@lrt_jabodebek](https://www.instagram.com/lrt_jabodebek/).

Holiday calendar is sourced from Indonesian national holidays data.

## Project Structure

```
visualisasi-lrt/
├── public/                      # Static files served by web server
│   ├── index.html               # Main application
│   ├── export.geojson           # Raw OpenStreetMap track data
│   ├── rute_lrt_siap_pakai.geojson  # Processed route segments
│   ├── schedule_data.json       # Weekend schedule
│   ├── schedule_data_weekdays.json  # Weekday schedule
│   └── hari_libur/
│       └── hari_libur2026.json  # Indonesian national holidays 2026
├── build/                       # Build scripts
│   ├── build_routes.py          # Generate route segments from OSM data
│   ├── build_schedule.py       # Parse raw schedules into JSON
│   └── potong_jalur.js          # Legacy Node.js script (deprecated)
├── data/                        # Raw source data
│   ├── raw_b.txt                # Bekasi line weekend schedule
│   ├── raw_c.txt                # Cibubur line weekend schedule
│   ├── raw_d.txt                # Bekasi line weekday schedule
│   └── raw_e.txt                # Cibubur line weekday schedule
├── CLAUDE.md                    # Claude Code project documentation
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.x (for running build scripts and local server)
- Web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. Clone the repository
2. Install dependencies (optional, for legacy Node.js scripts):

```bash
npm install
```

### Running the Application

Start a local web server in the project root:

```bash
python -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### Building Schedule Data

If you need to regenerate schedule data from raw text files:

```bash
python3 build/build_schedule.py
```

### Building Route Segments

If you need to regenerate route segments from OSM data:

```bash
python3 build/build_routes.py
```

## Schedule Logic

The application automatically selects the appropriate schedule based on the current date:

| Condition | Schedule Used |
|-----------|--------------|
| Monday - Friday (non-holiday) | Weekdays schedule (430 trips) |
| Saturday or Sunday | Weekends schedule (270 trips) |
| Public Holiday | Weekends schedule (270 trips) |

## Technical Details

### Data Flow

1. Raw schedule text files (`data/raw_*.txt`) contain GAPEKA timing data
2. `build/build_schedule.py` parses raw files into JSON format
3. `public/schedule_data*.json` contains parsed schedule data
4. `index.html` loads schedule data and simulates train movements
5. Route segments are loaded from `public/rute_lrt_siap_pakai.geojson`

### Position Calculation

1. Simulation time tracked in seconds-from-midnight
2. For each train, `getTrainState()` finds current segment between station timings
3. Between stations: interpolate position along route geometry using cumulative distance
4. During dwell: snap to station coordinates

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `R` | Reset simulation to current real time |
| `-` / `+` | Decrease / Increase simulation speed |

## API Reference

The application uses Leaflet.js for mapping and does not expose a public API. All data is served as static JSON files.

## License

This project is for educational and demonstration purposes. Schedule data is sourced from official LRT Jabodebek publications.

## Acknowledgments

- **LRT Jabodebek** - Official schedule data from [@lrt_jabodebek](https://www.instagram.com/lrt_jabodebek/)
- **OpenStreetMap** - Track geometry data
- **Leaflet.js** - Interactive mapping
- **CartoDB** - Dark theme map tiles