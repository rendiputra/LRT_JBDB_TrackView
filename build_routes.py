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
print("Loading export.geojson...")
with open("export.geojson") as f:
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
    """Chain multiple way segments into one coordinate array.
    way_specs: list of (way_id, reverse_bool)
    Skips duplicate points at junctions.
    """
    result = []
    for way_id, rev in way_specs:
        coords = get_coords(way_id, rev)
        if result:
            # Skip first point if it's very close to last point (junction)
            if haversine(result[-1][0], result[-1][1], coords[0][0], coords[0][1]) < 20:
                coords = coords[1:]
        result.extend(coords)
    return result

def densify_track(coords, max_gap=200):
    """Fill gaps in track coordinates by inserting intermediate points.
    When two consecutive points are more than max_gap meters apart,
    insert evenly-spaced intermediate points to smooth the gap.
    """
    result = [coords[0]]
    for i in range(1, len(coords)):
        d = haversine(coords[i-1][0], coords[i-1][1], coords[i][0], coords[i][1])
        if d > max_gap:
            # Insert intermediate points
            n_segments = max(2, int(d / max_gap) + 1)
            for j in range(1, n_segments):
                t = j / n_segments
                lon = coords[i-1][0] + (coords[i][0] - coords[i-1][0]) * t
                lat = coords[i-1][1] + (coords[i][1] - coords[i-1][1]) * t
                result.append([lon, lat])
        result.append(coords[i])
    return result

# ═══════════════════════════════════════════════════════════════
# TRACK CHAINS - Manually traced from connectivity analysis
# Each chain: list of (way_id, is_reversed)
#
# DUAL TRACKS:
#   Track A = generally: Dukuh Atas → east/south direction
#   Track B = generally: east/south → Dukuh Atas direction
# ═══════════════════════════════════════════════════════════════

# ── MAIN LINE ──

# Track A: Dukuh Atas → Cawang direction
# way/1422433005: DKA terminal [106.8229→106.8255]
# way/1361642970: [106.8255→106.8278] Setiabudi-Rasuna area
# way/1367621436: [106.8275→106.8278] short connector (REVERSED: 106.8278→106.8275)
# wait - 1367621436 goes S[106.8275]→E[106.8278], and 1361642970 ends at E[106.8278]
# They meet at the same end. So after 1361642970, I need to go to 1367621436's start.
# 1361642970 E → 1367621436 E (same node) → take 1367621436 reversed: E→S
# Then 1367621436 S → 1361642972 E (same node) → take 1361642972 reversed: E→S
# Then 1361642972 S → 1367621439 E (same node) → take 1367621439 reversed: E→S
# Then 1367621439 S → 497958415 E (same node) → take 497958415 reversed: E→S
# Then 497958415 S → 1364419053 E (same node) → take 1364419053 reversed: E→S
# Then 1364419053 S → 1364419051 E (same node) → take 1364419051 reversed: E→S
# 1364419051 S = Cawang junction [106.8754]

main_trackA = [  # Dukuh Atas → Cawang (going east/south)
    ("way/1422433005", False),   # S→E: [106.8229→106.8255]
    ("way/1361642970", False),   # S→E: [106.8255→106.8278]
    ("way/1367621436", True),    # E→S: [106.8278→106.8275]
    ("way/1361642972", True),    # E→S: [106.8276→106.8280] (reversed: S→E becomes E→S)
    ("way/1367621439", True),    # E→S: [106.8280→106.8284]
    ("way/497958415", True),     # E→S: [106.8284→106.8698]
    ("way/1364419053", True),    # E→S: [106.8698→106.8729]
    ("way/1364419051", True),    # E→S: [106.8729→106.8754]
]

# Track B: Cawang → Dukuh Atas direction
# way/1364419052: [106.8754→106.8729]
# way/1364419054: [106.8729→106.8698]
# way/501311233: [106.8698→106.8283]
# way/1367621438: [106.8283→106.8279]
# way/1361642973: [106.8279→106.8275]
# way/1367621437: [106.8276→106.8279] — S matches 1361642973 E
# way/1361642971: [106.8279→106.8255]
# way/1422433004: [106.8255→106.8229]

main_trackB = [  # Cawang → Dukuh Atas (going west/north)
    ("way/1364419052", False),   # S→E: [106.8754→106.8729]
    ("way/1364419054", False),   # S→E: [106.8729→106.8698]
    ("way/501311233", False),    # S→E: [106.8698→106.8283]
    ("way/1367621438", False),   # S→E: [106.8283→106.8279]
    ("way/1361642973", False),   # S→E: [106.8279→106.8275]
    ("way/1367621437", False),   # S→E: [106.8276→106.8279]
    ("way/1361642971", False),   # S→E: [106.8279→106.8255]
    ("way/1422433004", False),   # S→E: [106.8255→106.8229]
]

# ── CIBUBUR BRANCH ──

# Track A: Cawang junction → Harjamukti
# From Cawang junction [106.8754]:
# way/1332161173: [106.8754→106.8730] (southward)
# way/1332161175: [106.8730→106.8741]
# way/752898462: [106.8741→106.8957] (to Harjamukti)
# way/1422433002: [106.8957→106.8961] (past Harjamukti to terminus)

cibubur_trackA = [  # Cawang → Harjamukti
    ("way/1332161173", False),
    ("way/1332161175", False),
    ("way/752898462", False),
    ("way/1422433002", False),
]

# Track B: Harjamukti → Cawang junction
# way/1422433003: [106.8961→106.8957] (from terminus)
# way/497958416: [106.8957→106.8742] (northward)
# way/1332161176: [106.8742→106.8730]
# way/1332161174: [106.8730→106.8754]

cibubur_trackB = [  # Harjamukti → Cawang
    ("way/1422433003", False),
    ("way/497958416", False),
    ("way/1332161176", False),
    ("way/1332161174", False),
]

# ── BEKASI BRANCH ──

# Track A: Cawang junction → Jatimulya
# way/499760768: [106.8754→107.0217]
# way/1422433000: [107.0217→107.0248]
# way/1368205128: [107.0248→107.0217] — wait, this goes back! 
# Actually: way/1422433000 E[107.0248] connects to way/1368205128 S[107.0248]
# But 1368205128 goes back to 107.0217. That's a loop.
# Let me check: the Bekasi line goes from Cawang eastward.
# way/499760768 covers Cawang[106.8754] to near Jatimulya[107.0217]
# The extensions past that are for the depot/yard area.
# Jatimulya station is at [107.0183, -6.2630] which is along way/499760768.
# So we only need way/499760768 for the entire Bekasi branch Track A.

bekasi_trackA = [  # Cawang → Jatimulya
    ("way/499760768", False),
    ("way/1422433000", False),
    ("way/1368205128", False),  # extends to depot area
]

# Track B: Jatimulya → Cawang
# way/1368205129: [107.0201→107.0180]
# way/508883080: [107.0180→106.8754]
# But where does the track start from the Jatimulya side?
# way/1368205129 S[107.0201] has no connection except to 1422433001 E
# way/1422433001: [107.0217→107.0201]
# So: way/1422433001 → way/1368205129 → way/508883080

bekasi_trackB = [  # Jatimulya → Cawang
    ("way/1422433001", False),
    ("way/1368205129", False),
    ("way/508883080", False),
]

# ═══════════════════════════════════════════════════════════════
# BUILD COMPLETE TRACKS
# ═══════════════════════════════════════════════════════════════

print("Building track chains...")

tracks = {
    "main_A": chain_ways(main_trackA),      # DKA → Cawang
    "main_B": chain_ways(main_trackB),      # Cawang → DKA
    "cibubur_A": chain_ways(cibubur_trackA), # Cawang → Harjamukti
    "cibubur_B": chain_ways(cibubur_trackB), # Harjamukti → Cawang
    "bekasi_A": chain_ways(bekasi_trackA),   # Cawang → Jatimulya
    "bekasi_B": chain_ways(bekasi_trackB),   # Jatimulya → Cawang
}

# Densify all tracks to fill gaps from sparse OSM data
for name in tracks:
    tracks[name] = densify_track(tracks[name], max_gap=200)

for name, coords in tracks.items():
    length = sum(haversine(coords[i][0],coords[i][1],coords[i+1][0],coords[i+1][1]) for i in range(len(coords)-1))
    max_gap = max(haversine(coords[i][0],coords[i][1],coords[i+1][0],coords[i+1][1]) for i in range(len(coords)-1))
    print(f"  {name}: {len(coords)} pts, {length:.0f}m total, max_gap={max_gap:.0f}m")

# ═══════════════════════════════════════════════════════════════
# STATION SNAPPING
# ═══════════════════════════════════════════════════════════════

STATIONS = {
    "dukuh_atas":       [106.822929, -6.204308],
    "setiabudi":        [106.827656, -6.208157],
    "rasuna_said":      [106.830674, -6.216180],
    "kuningan":         [106.832683, -6.223643],
    "pancoran":         [106.839081, -6.242318],
    "cikoko":           [106.858286, -6.243528],
    "ciliwung":         [106.865541, -6.243775],
    "cawang":           [106.874119, -6.249003],
    "taman_mini":       [106.881601, -6.295560],
    "kampung_rambutan": [106.883756, -6.302154],
    "ciracas":          [106.886681, -6.326928],
    "harjamukti":       [106.895651, -6.373895],
    "halim":            [106.899925, -6.248720],
    "jatibening":       [106.946296, -6.256830],
    "cikunir1":         [106.959798, -6.255401],
    "cikunir2":         [106.976230, -6.248559],
    "bekasi_barat":     [106.994399, -6.254471],
    "jatimulya":        [107.018307, -6.262964],
}

def snap_to_track(station_lon, station_lat, track_coords):
    """Find nearest point on track. Returns (distance, segment_index, t)"""
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
    """Extract coordinates between two points on a track"""
    pos1 = seg1 + t1
    pos2 = seg2 + t2
    
    if pos1 > pos2:
        # Swap and reverse later
        result = extract_sub_track(track_coords, seg2, t2, seg1, t1)
        return list(reversed(result))
    
    result = [interpolate_on_line(track_coords, seg1, t1)]
    for i in range(seg1+1, seg2+1):
        result.append(track_coords[i])
    result.append(interpolate_on_line(track_coords, seg2, t2))
    return result

# ═══════════════════════════════════════════════════════════════
# ROUTE DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# Which tracks to use for each route direction
# dukuh_to_cibubur: uses main_A (DKA→Cawang) + cibubur_A (Cawang→Harjamukti)
# cibubur_to_dukuh: uses cibubur_B (Harjamukti→Cawang) + main_B (Cawang→DKA)
# dukuh_to_bekasi: uses main_A (DKA→Cawang) + bekasi_A (Cawang→Jatimulya)  
# bekasi_to_dukuh: uses bekasi_B (Jatimulya→Cawang) + main_B (Cawang→DKA)

# Main line stations (DKA → Cawang order)
main_stations = ["dukuh_atas","setiabudi","rasuna_said","kuningan","pancoran","cikoko","ciliwung","cawang"]
cibubur_stations = ["cawang","taman_mini","kampung_rambutan","ciracas","harjamukti"]
bekasi_stations = ["cawang","halim","jatibening","cikunir1","cikunir2","bekasi_barat","jatimulya"]

def build_segments_for_track(station_list, track_name, track_coords, route_name):
    """Build per-station-pair segments along a given track"""
    segments = []
    
    # Snap all stations to this track
    snaps = {}
    for st_id in station_list:
        lon, lat = STATIONS[st_id]
        d, seg, t = snap_to_track(lon, lat, track_coords)
        snaps[st_id] = (d, seg, t)
        if d > 100:
            print(f"  ⚠ {st_id} is {d:.0f}m from {track_name}")
    
    # Extract segments between consecutive stations
    for i in range(len(station_list)-1):
        st_from = station_list[i]
        st_to = station_list[i+1]
        d1, seg1, t1 = snaps[st_from]
        d2, seg2, t2 = snaps[st_to]
        
        coords = extract_sub_track(track_coords, seg1, t1, seg2, t2)
        
        # Validate
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

all_segments = []

# ── dukuh_to_cibubur: main_A + cibubur_A ──
print("\n=== dukuh_to_cibubur ===")
segs1 = build_segments_for_track(main_stations, "main_A", tracks["main_A"], "dukuh_to_cibubur")
segs2 = build_segments_for_track(cibubur_stations, "cibubur_A", tracks["cibubur_A"], "dukuh_to_cibubur")
all_segments.extend(segs1)
all_segments.extend(segs2)

# ── cibubur_to_dukuh: cibubur_B + main_B ──
print("\n=== cibubur_to_dukuh ===")
cib_rev = list(reversed(cibubur_stations))  # harjamukti → cawang
main_rev = list(reversed(main_stations))     # cawang → dukuh_atas
segs3 = build_segments_for_track(cib_rev, "cibubur_B", tracks["cibubur_B"], "cibubur_to_dukuh")
segs4 = build_segments_for_track(main_rev, "main_B", tracks["main_B"], "cibubur_to_dukuh")
all_segments.extend(segs3)
all_segments.extend(segs4)

# ── dukuh_to_bekasi: main_A + bekasi_A ──
print("\n=== dukuh_to_bekasi ===")
# Main line portion same as cibubur (reuse segs1 but with different route name)
segs5 = build_segments_for_track(main_stations, "main_A", tracks["main_A"], "dukuh_to_bekasi")
segs6 = build_segments_for_track(bekasi_stations, "bekasi_A", tracks["bekasi_A"], "dukuh_to_bekasi")
all_segments.extend(segs5)
all_segments.extend(segs6)

# ── bekasi_to_dukuh: bekasi_B + main_B ──
print("\n=== bekasi_to_dukuh ===")
bks_rev = list(reversed(bekasi_stations))
segs7 = build_segments_for_track(bks_rev, "bekasi_B", tracks["bekasi_B"], "bekasi_to_dukuh")
segs8 = build_segments_for_track(main_rev, "main_B", tracks["main_B"], "bekasi_to_dukuh")
all_segments.extend(segs7)
all_segments.extend(segs8)

# ═══════════════════════════════════════════════════════════════
# OUTPUT
# ═══════════════════════════════════════════════════════════════

features = []
for seg in all_segments:
    # Key includes route for direction-specific lookup
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
with open("rute_lrt_siap_pakai.geojson", "w") as f:
    json.dump(output, f)

print(f"\n🎉 Output: rute_lrt_siap_pakai.geojson ({len(features)} segments)")

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
