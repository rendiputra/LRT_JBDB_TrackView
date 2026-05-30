#!/usr/bin/env python3
"""
Build clean route segments for LRT Jabodebek visualization.
Uses manually-traced track chains based on GeoJSON connectivity analysis.
Handles dual tracks (separate geometry for each direction).
"""

import json
import math

def haversine(lon1, lat1, lon2, lat2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2-lat1); dl = math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

def point_to_segment_dist(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    if dx==0 and dy==0:
        return haversine(px,py,ax,ay), 0.0
    t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / (dx*dx+dy*dy)))
    return haversine(px, py, ax+t*dx, ay+t*dy), t

def interpolate_on_line(coords, seg_idx, t):
    a, b = coords[seg_idx], coords[seg_idx+1]
    return [a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t]

# ─── Load GeoJSON ───
import os

data_dir = 'public'
output_dir = 'public'

print("Loading export.geojson...")
with open(os.path.join(data_dir, "export.geojson")) as f:
    data = json.load(f)

# Index features by way ID
way_index = {}
for feat in data["features"]:
    wid = feat["properties"].get("@id","")
    if feat["geometry"]["type"] == "LineString":
        way_index[wid] = feat["geometry"]["coordinates"]

def get_coords(way_id, reverse=False):
    """Get coordinates for a way, optionally reversed"""
    c = list(way_index[way_id])
    if reverse:
        c = list(reversed(c))
    return c

def chain_ways(way_specs):
    """Chain multiple way segments into one coordinate array."""
    result = []
    for way_id, rev in way_specs:
        coords = get_coords(way_id, rev)
        if result and coords:
            if haversine(result[-1][0], result[-1][1], coords[0][0], coords[0][1]) < 20:
                coords = coords[1:]
        result.extend(coords)
    return result

def densify_track(coords, max_gap=200):
    """Fill gaps in track coordinates."""
    if len(coords) < 2:
        return coords

    result = [coords[0]]
    for i in range(1, len(coords)):
        d = haversine(coords[i-1][0], coords[i-1][1], coords[i][0], coords[i][1])
        if d > max_gap:
            n_segments = max(2, int(d / max_gap) + 1)
            for j in range(1, n_segments):
                t = j / n_segments
                lon = coords[i-1][0] + (coords[i][0] - coords[i-1][0]) * t
                lat = coords[i-1][1] + (coords[i][1] - coords[i-1][1]) * t
                result.append([lon, lat])
        result.append(coords[i])
    return result

# ═══════════════════════════════════════════════════════════════
# TRACK CHAINS
# ═══════════════════════════════════════════════════════════════
#
# Track structure at Cawang junction area:
# - Cawang station [106.8712, -6.2459] is on the MAIN LINE
# - Junction [106.8754, -6.2479] is where branches split (east of station)
# - For continuous routes, we chain main line to branch tracks
# ═══════════════════════════════════════════════════════════════

# Main line: DKA → Junction (via cawang station)
main_trackA = [
    ("way/1422433005", False),  # DKA
    ("way/1361642970", False),  # Setiabudi area
    ("way/1367621436", True),   # continue east
    ("way/1361642972", True),
    ("way/1367621439", True),
    ("way/497958415", True),
    ("way/1364419053", True),   # passes near cawang station
    ("way/1364419051", True),   # to junction
]

main_trackB = [
    ("way/1364419052", False),  # junction → cawang area
    ("way/1364419054", False),  # continue west
    ("way/501311233", False),   # continue west
    ("way/1367621438", False),
    ("way/1361642973", False),
    ("way/1367621437", False),
    ("way/1361642971", False),
    ("way/1422433004", False),   # to DKA
]

# Cibubur branch: Junction → Harjamukti
cibubur_trackA = [
    ("way/1332161173", False),  # junction → south
    ("way/1332161175", False),
    ("way/752898462", False),
    ("way/1422433002", False),
]

cibubur_trackB = [
    ("way/1422433003", False),
    ("way/497958416", False),
    ("way/1332161176", False),
    ("way/1332161174", False),
]

# Bekasi branch: Junction → Jatimulya
bekasi_trackA = [
    ("way/499760768", False),   # junction → east
]

bekasi_trackB = [
    ("way/1422433001", False),
    ("way/1368205129", False),
    ("way/508883080", False),
]

# ═══════════════════════════════════════════════════════════════
# BUILD TRACKS
# ═══════════════════════════════════════════════════════════════

print("Building track chains...")

tracks = {
    "main_A": chain_ways(main_trackA),
    "main_B": chain_ways(main_trackB),
    "cibubur_A": chain_ways(cibubur_trackA),
    "cibubur_B": chain_ways(cibubur_trackB),
    "bekasi_A": chain_ways(bekasi_trackA),
    "bekasi_B": chain_ways(bekasi_trackB),
}

for name in tracks:
    tracks[name] = densify_track(tracks[name], max_gap=200)

for name, coords in tracks.items():
    length = sum(haversine(coords[i][0],coords[i][1],coords[i+1][0],coords[i+1][1]) for i in range(len(coords)-1))
    max_gap = max(haversine(coords[i][0],coords[i][1],coords[i+1][0],coords[i+1][1]) for i in range(len(coords)-1))
    print(f"  {name}: {len(coords)} pts, {length:.0f}m total, max_gap={max_gap:.0f}m")

# ═══════════════════════════════════════════════════════════════
# STATION COORDINATES
# ═══════════════════════════════════════════════════════════════

STATIONS = {
    "dukuh_atas":       [106.8255301, -6.2048280],
    "setiabudi":        [106.8302209, -6.2093184],
    "rasuna_said":      [106.8322373, -6.2216089],
    "kuningan":         [106.8332031, -6.2287727],
    "pancoran":         [106.8385146, -6.2421415],
    "cikoko":            [106.8570718, -6.2434846],
    "ciliwung":          [106.8639705, -6.2434461],
    "cawang":            [106.8712296, -6.2459070],
    "taman_mini":       [106.8805584, -6.2929088],
    "kampung_rambutan":  [106.8843804, -6.3095494],
    "ciracas":           [106.8866433, -6.3237693],
    "harjamukti":        [106.8956698, -6.3738926],
    "halim":             [106.8872875, -6.2458656],
    "jatibening":       [106.9279199, -6.2577476],
    "cikunir1":          [106.9518734, -6.2566001],
    "cikunir2":          [106.9632112, -6.2546502],
    "bekasi_barat":       [106.9904237, -6.2529489],
    "jatimulya":         [107.0216701, -6.2641077],
}

def snap_to_track(station_lon, station_lat, track_coords):
    """Find nearest point on track."""
    best_d = float('inf')
    best_seg = 0
    best_t = 0
    for i in range(len(track_coords)-1):
        d, t = point_to_segment_dist(
            station_lon, station_lat,
            track_coords[i][0], track_coords[i][1],
            track_coords[i+1][0], track_coords[i+1][1]
        )
        if d < best_d:
            best_d = d
            best_seg = i
            best_t = t
    return best_d, best_seg, best_t

def extract_sub_track(track_coords, seg1, t1, seg2, t2):
    """Extract coordinates between two points on a track."""
    pos1 = seg1 + t1
    pos2 = seg2 + t2

    if pos1 > pos2:
        result = extract_sub_track(track_coords, seg2, t2, seg1, t1)
        return list(reversed(result))

    result = [interpolate_on_line(track_coords, seg1, t1)]
    for i in range(seg1+1, seg2+1):
        result.append(track_coords[i])
    result.append(interpolate_on_line(track_coords, seg2, t2))
    return result

# ═══════════════════════════════════════════════════════════════
# BUILD COMPLETE ROUTES (full DKA → terminus paths)
# ═══════════════════════════════════════════════════════════════
#
# Routes:
# - dukuh_to_cibubur: DKA → cawang → junction → harjamukti
# - cibubur_to_dukuh: harjamukti → junction → cawang → DKA
# - dukuh_to_bekasi: DKA → cawang → junction → jatimulya
# - bekasi_to_dukuh: jatimulya → junction → cawang → DKA
# ═══════════════════════════════════════════════════════════════

all_segments = []

# Station lists
main_line_stations = ["dukuh_atas","setiabudi","rasuna_said","kuningan","pancoran","cikoko","ciliwung","cawang"]
cibubur_branch = ["taman_mini","kampung_rambutan","ciracas","harjamukti"]
bekasi_branch = ["halim","jatibening","cikunir1","cikunir2","bekasi_barat","jatimulya"]

def build_route_segments(route_name, station_list, track_name, track_coords):
    """Build all segments for a route."""
    segments = []

    # Snap all stations
    snaps = {}
    for st_id in station_list:
        lon, lat = STATIONS[st_id]
        d, seg, t = snap_to_track(lon, lat, track_coords)
        snaps[st_id] = (d, seg, t)

    # Extract segments between consecutive stations
    for i in range(len(station_list)-1):
        st_from = station_list[i]
        st_to = station_list[i+1]
        d1, seg1, t1 = snaps[st_from]
        d2, seg2, t2 = snaps[st_to]

        coords = extract_sub_track(track_coords, seg1, t1, seg2, t2)

        seg_len = sum(haversine(coords[j][0],coords[j][1],coords[j+1][0],coords[j+1][1]) for j in range(len(coords)-1))
        max_gap = max(haversine(coords[j][0],coords[j][1],coords[j+1][0],coords[j+1][1]) for j in range(len(coords)-1)) if len(coords)>1 else 0

        status = "✅" if max_gap < 500 else f"❌ gap={max_gap:.0f}m"
        print(f"  {status} {st_from} → {st_to}: {len(coords)} pts, {seg_len:.0f}m")

        segments.append({
            "from": st_from,
            "to": st_to,
            "route": route_name,
            "coords": coords
        })

    return segments

# ── dukuh_to_cibubur: DKA → cawang (main) → harjamukti (branch) ──
print("\n=== dukuh_to_cibubur ===")
dukuh_to_cibubur_stations = main_line_stations + cibubur_branch
# Chain: main_A + cibubur_A (continuously)
combined_cibubur_track = tracks["main_A"] + tracks["cibubur_A"]
combined_cibubur_track = densify_track(combined_cibubur_track, max_gap=200)
segs1 = build_route_segments("dukuh_to_cibubur", dukuh_to_cibubur_stations, "combined", combined_cibubur_track)
all_segments.extend(segs1)

# ── cibubur_to_dukuh: harjamukti → cawang (branch) → DKA (main) ──
print("\n=== cibubur_to_dukuh ===")
cibubur_to_dukuh_stations = list(reversed(dukuh_to_cibubur_stations))
combined_cibubur_B_track = tracks["cibubur_B"] + tracks["main_B"]
combined_cibubur_B_track = densify_track(combined_cibubur_B_track, max_gap=200)
segs2 = build_route_segments("cibubur_to_dukuh", cibubur_to_dukuh_stations, "combined", combined_cibubur_B_track)
all_segments.extend(segs2)

# ── dukuh_to_bekasi: DKA → cawang (main) → jatimulya (branch) ──
print("\n=== dukuh_to_bekasi ===")
dukuh_to_bekasi_stations = main_line_stations + bekasi_branch
combined_bekasi_track = tracks["main_A"] + tracks["bekasi_A"]
combined_bekasi_track = densify_track(combined_bekasi_track, max_gap=200)
segs3 = build_route_segments("dukuh_to_bekasi", dukuh_to_bekasi_stations, "combined", combined_bekasi_track)
all_segments.extend(segs3)

# ── bekasi_to_dukuh: jatimulya → cawang (branch) → DKA (main) ──
print("\n=== bekasi_to_dukuh ===")
bekasi_to_dukuh_stations = list(reversed(dukuh_to_bekasi_stations))
combined_bekasi_B_track = tracks["bekasi_B"] + tracks["main_B"]
combined_bekasi_B_track = densify_track(combined_bekasi_B_track, max_gap=200)
segs4 = build_route_segments("bekasi_to_dukuh", bekasi_to_dukuh_stations, "combined", combined_bekasi_B_track)
all_segments.extend(segs4)

# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════

features = []
for seg in all_segments:
    key = f"{seg['route']}:{seg['from']}_TO_{seg['to']}"
    features.append({
        "type": "Feature",
        "properties": {
            "id": key,
            "route": seg["route"],
            "from": seg["from"],
            "to": seg["to"],
        },
        "geometry": {
            "type": "LineString",
            "coordinates": seg["coords"]
        }
    })

output = {"type": "FeatureCollection", "features": features}
output_path = os.path.join(output_dir, "rute_lrt_siap_pakai.geojson")
with open(output_path, "w") as f:
    json.dump(output, f)

print(f"\n🎉 Output: {output_path} ({len(features)} segments)")

# Final validation
print("\n=== Final Validation ===")
errors = 0
for feat in features:
    coords = feat["geometry"]["coordinates"]
    fid = feat["properties"]["id"]
    for j in range(1, len(coords)):
        d = haversine(coords[j][0],coords[j][1],coords[j-1][0],coords[j-1][1])
        if d > 500:
            print(f"  ❌ {fid}: jump {d:.0f}m at pt {j}")
            errors += 1

if errors == 0:
    print("  ✅ All segments clean!")
else:
    print(f"  ❌ {errors} jumps found")