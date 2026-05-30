import json
import os

def time_to_sec(t_str):
    if not t_str or t_str.strip() == '':
        return 0
    parts = t_str.split(':')
    return int(parts[0]) * 3600 + int(parts[1]) * 60


def parse_bekasi(filename):
    """Parse Bekasi line schedule from raw text file"""
    trains = []

    station_headers = ['Jati_Mulya', 'Bekasi_Barat', 'Cikunir_2', 'Cikunir_1', 'Jatibening_Baru', 'Halim', 'Cawang',
                       'Ciliwung', 'Cikoko', 'Pancoran', 'Kuningan', 'Rasuna_Said', 'Setiabudi', 'Dukuh_Atas']

    station_map = {
        'Jati_Mulya': 'jatimulya',
        'Bekasi_Barat': 'bekasi_barat',
        'Cikunir_2': 'cikunir2',
        'Cikunir_1': 'cikunir1',
        'Jatibening_Baru': 'jatibening',
        'Halim': 'halim',
        'Cawang': 'cawang',
        'Ciliwung': 'ciliwung',
        'Cikoko': 'cikoko',
        'Pancoran': 'pancoran',
        'Kuningan': 'kuningan',
        'Rasuna_Said': 'rasuna_said',
        'Setiabudi': 'setiabudi',
        'Dukuh_Atas': 'dukuh_atas',
    }

    # Forward route: Jatimulya → Dukuh Atas (stations in file order)
    forward_stations = station_headers[:]  # copy
    # Reverse route: Dukuh Atas → Jatimulya (file header order reversed, plus Halim inserted)
    reverse_stations = list(reversed(station_headers))  # Dukuh_Atas → ... → Jati_Mulya

    with open(filename, 'r') as f:
        lines = f.read().strip().split('\n')

    # Skip header row
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue

        run_id = parts[0]
        arah = parts[1]
        trip = parts[2]
        times = parts[3:]

        # Pad or trim times to match station count
        while len(times) < len(station_headers):
            times.append('')
        times = times[:len(station_headers)]

        # Map station → time
        st_times = {}
        for i, h in enumerate(station_headers):
            if i < len(times):
                st_times[station_map[h]] = time_to_sec(times[i])

        if arah == 'JM_to_DA':
            route_id = 'bekasi_to_dukuh'
            direction = '→ Dukuh Atas'
            origin = 'Jatimulya'
            dest = 'Dukuh Atas 2'
            st_list = forward_stations
        else:
            route_id = 'dukuh_to_bekasi'
            direction = '→ Jatimulya'
            origin = 'Dukuh Atas 2'
            dest = 'Jatimulya'
            st_list = reverse_stations

        timings = []
        for st_name in st_list:
            st_id = station_map[st_name]
            arr = st_times.get(st_id, 0)
            dep = arr + 45  # dwell time
            timings.append({
                "stationId": st_id,
                "arriveAt": arr,
                "departAt": dep
            })

        trains.append({
            "id": f"B{run_id.replace('Run-B', '').replace('Run-D', '')}-{trip}",
            "route": route_id,
            "line": "bekasi",
            "direction": direction,
            "origin": origin,
            "dest": dest,
            "timings": timings,
            "color": "#ff9900"
        })

    return trains


def parse_cibubur(filename):
    """Parse Cibubur line schedule from raw text file"""
    trains = []

    station_headers = ['Harjamukti', 'Ciracas', 'Kampung_Rambutan', 'TMII', 'Cawang',
                       'Ciliwung', 'Cikoko', 'Pancoran', 'Kuningan', 'Rasuna_Said', 'Setiabudi', 'Dukuh_Atas']

    station_map = {
        'Harjamukti': 'harjamukti',
        'Ciracas': 'ciracas',
        'Kampung_Rambutan': 'kampung_rambutan',
        'TMII': 'taman_mini',
        'Cawang': 'cawang',
        'Ciliwung': 'ciliwung',
        'Cikoko': 'cikoko',
        'Pancoran': 'pancoran',
        'Kuningan': 'kuningan',
        'Rasuna_Said': 'rasuna_said',
        'Setiabudi': 'setiabudi',
        'Dukuh_Atas': 'dukuh_atas',
    }

    forward_stations = station_headers[:]
    reverse_stations = list(reversed(station_headers))

    with open(filename, 'r') as f:
        lines = f.read().strip().split('\n')

    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            continue

        run_id = parts[0]
        arah = parts[1]
        trip = parts[2]
        times = parts[3:]

        while len(times) < len(station_headers):
            times.append('')
        times = times[:len(station_headers)]

        st_times = {}
        for i, h in enumerate(station_headers):
            if i < len(times):
                st_times[station_map[h]] = time_to_sec(times[i])

        if arah == 'HJ_to_DA':
            route_id = 'cibubur_to_dukuh'
            direction = '→ Dukuh Atas'
            origin = 'Harjamukti'
            dest = 'Dukuh Atas 2'
            st_list = forward_stations
        else:
            route_id = 'dukuh_to_cibubur'
            direction = '→ Harjamukti'
            origin = 'Dukuh Atas 2'
            dest = 'Harjamukti'
            st_list = reverse_stations

        timings = []
        for st_name in st_list:
            st_id = station_map[st_name]
            arr = st_times.get(st_id, 0)
            dep = arr + 45
            timings.append({
                "stationId": st_id,
                "arriveAt": arr,
                "departAt": dep
            })

        trains.append({
            "id": f"C{run_id.replace('Run-C', '').replace('Run-E', '')}-{trip}",
            "route": route_id,
            "line": "cibubur",
            "direction": direction,
            "origin": origin,
            "dest": dest,
            "timings": timings,
            "color": "#00c8ff"
        })

    return trains


if __name__ == '__main__':
    # Paths - assuming script is run from project root
    data_dir = 'data'
    output_dir = 'public'

    # Generate weekdays schedule (from raw_d.txt and raw_e.txt)
    weekdays_bekasi = os.path.join(data_dir, 'raw_d.txt')
    weekdays_cibubur = os.path.join(data_dir, 'raw_e.txt')

    if os.path.exists(weekdays_bekasi) and os.path.exists(weekdays_cibubur):
        trains_b_weekdays = parse_bekasi(weekdays_bekasi)
        trains_c_weekdays = parse_cibubur(weekdays_cibubur)

        all_trains_weekdays = trains_b_weekdays + trains_c_weekdays

        bekasi_count_wd = sum(1 for t in all_trains_weekdays if t['line'] == 'bekasi')
        cibubur_count_wd = sum(1 for t in all_trains_weekdays if t['line'] == 'cibubur')

        output_path = os.path.join(output_dir, 'schedule_data_weekdays.json')
        with open(output_path, 'w') as f:
            json.dump(all_trains_weekdays, f, indent=2)

        print(f"Generated {output_path}:")
        print(f"  Bekasi: {bekasi_count_wd} trips")
        print(f"  Cibubur: {cibubur_count_wd} trips")
        print(f"  Total: {len(all_trains_weekdays)} trips")

    # Generate weekends schedule (from raw_b.txt and raw_c.txt)
    weekends_bekasi = os.path.join(data_dir, 'raw_b.txt')
    weekends_cibubur = os.path.join(data_dir, 'raw_c.txt')

    if os.path.exists(weekends_bekasi) and os.path.exists(weekends_cibubur):
        trains_b = parse_bekasi(weekends_bekasi)
        trains_c = parse_cibubur(weekends_cibubur)

        all_trains = trains_b + trains_c

        bekasi_count = sum(1 for t in all_trains if t['line'] == 'bekasi')
        cibubur_count = sum(1 for t in all_trains if t['line'] == 'cibubur')

        output_path = os.path.join(output_dir, 'schedule_data.json')
        with open(output_path, 'w') as f:
            json.dump(all_trains, f, indent=2)

        print(f"Generated {output_path} (weekends):")
        print(f"  Bekasi: {bekasi_count} trips")
        print(f"  Cibubur: {cibubur_count} trips")
        print(f"  Total: {len(all_trains)} trips")