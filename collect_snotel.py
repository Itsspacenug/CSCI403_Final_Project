"""
SNOTEL Data Collector for Colorado
====================================
CSCI 403 Final Project

Downloads daily snowpack data for all 117 active Colorado SNOTEL stations
from the NRCS Report Generator API. No API key required.

Output: snotel_all_stations.csv
Columns: station_id, station_name, date, swe_in, precip_in, snow_depth_in, temp_avg_f

Usage:
    pip install requests
    python collect_snotel.py

Load into PostgreSQL:
    \\COPY daily_observations FROM 'snotel_all_stations.csv' CSV HEADER;
"""

import requests
import time
import os

# ─────────────────────────────────────────────
# All 117 active Colorado SNOTEL stations
# Source: https://wcc.sc.egov.usda.gov/nwcc/yearcount?network=sntl&state=CO&counttype=statelist
# Accessed: April 2026
# ─────────────────────────────────────────────
STATIONS = [
    (1344, "Alta Lakes"),
    (303,  "Apishapa"),
    (1030, "Arapaho Ridge"),
    (322,  "Bear Lake"),
    (1061, "Bear River"),
    (327,  "Beartown"),
    (1041, "Beaver Ck Village"),
    (335,  "Berthoud Summit"),
    (345,  "Bison Lake"),
    (1185, "Black Mesa"),
    (1161, "Black Mountain"),
    (369,  "Brumley"),
    (938,  "Buckskin Joe"),
    (913,  "Buffalo Park"),
    (378,  "Burro Mountain"),
    (380,  "Butte"),
    (387,  "Cascade 2"),
    (1326, "Castle Peak"),
    (1101, "Chapman Tunnel"),
    (1059, "Cochetopa Pass"),
    (408,  "Columbine"),
    (409,  "Columbine Pass"),
    (904,  "Columbus Basin"),
    (412,  "Copeland Lake"),
    (415,  "Copper Mountain"),
    (426,  "Crosho"),
    (430,  "Culebra 2"),
    (431,  "Cumbres Trestle"),
    (438,  "Deadman Hill"),
    (457,  "Dry Lake"),
    (936,  "Echo Lake"),
    (465,  "El Diente Peak"),
    (467,  "Elk River"),
    (1252, "Elkhead Divide"),
    (1120, "Elliot Ridge"),
    (1325, "Elwood Pass"),
    (1186, "Fool Creek"),
    (485,  "Fremont Pass"),
    (1057, "Glen Cove"),
    (1058, "Grayback"),
    (505,  "Grizzly Peak"),
    (1102, "Hayden Pass"),
    (1187, "High Lonesome"),
    (531,  "Hoosier Pass"),
    (1122, "Hourglass Lake"),
    (538,  "Idarado"),
    (542,  "Independence Pass"),
    (547,  "Ivanhoe"),
    (935,  "Jackwhacker Gulch"),
    (551,  "Joe Wright"),
    (970,  "Jones Pass"),
    (556,  "Kiln"),
    (564,  "Lake Eldora"),
    (565,  "Lake Irene"),
    (580,  "Lily Pond"),
    (586,  "Lizard Head Pass"),
    (589,  "Lone Cone"),
    (1123, "Long Draw Resv"),
    (940,  "Lost Dog"),
    (602,  "Loveland Basin"),
    (607,  "Lynx Pass"),
    (905,  "Mancos"),
    (618,  "Mc Clure Pass"),
    (1040, "Mccoy Park"),
    (914,  "Medano Pass"),
    (622,  "Mesa Lakes"),
    (937,  "Michigan Creek"),
    (624,  "Middle Creek"),
    (1014, "Middle Fork Camp"),
    (629,  "Mineral Creek"),
    (632,  "Molas Lake"),
    (1124, "Moon Pass"),
    (658,  "Nast Lake"),
    (1031, "Never Summer"),
    (663,  "Niwot"),
    (669,  "North Lost Trail"),
    (675,  "Overland Res"),
    (680,  "Park Cone"),
    (682,  "Park Reservoir"),
    (688,  "Phantom Valley"),
    (701,  "Porphyry Creek"),
    (709,  "Rabbit Ears"),
    (1324, "Rat Creek"),
    (1032, "Rawah"),
    (713,  "Red Mountain Pass"),
    (717,  "Ripple Creek"),
    (718,  "Roach"),
    (939,  "Rough And Tumble"),
    (1100, "Saint Elmo"),
    (1128, "Sargents Mesa"),
    (1251, "Sawtooth"),
    (737,  "Schofield Pass"),
    (739,  "Scotch Creek"),
    (1060, "Sharkstooth"),
    (762,  "Slumgullion"),
    (773,  "South Colony"),
    (780,  "Spud Mountain"),
    (793,  "Stillwater Creek"),
    (797,  "Stump Lakes"),
    (802,  "Summit Ranch"),
    (825,  "Tower"),
    (827,  "Trapper Lake"),
    (829,  "Trinchera"),
    (838,  "University Camp"),
    (839,  "Upper Rio Grande"),
    (840,  "Upper San Juan"),
    (1141, "Upper Taylor"),
    (1005, "Ute Creek"),
    (842,  "Vail Mountain"),
    (843,  "Vallecito"),
    (1188, "Wager Gulch"),
    (1160, "Weminuche Creek"),
    (857,  "Whiskey Ck"),
    (1042, "Wild Basin"),
    (869,  "Willow Creek Pass"),
    (870,  "Willow Park"),
    (874,  "Wolf Creek Summit"),
    (1033, "Zirkel"),
]

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
OUTPUT_DIR  = "snowpack_data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "snotel_all_stations.csv")
DELAY_SEC   = 0.4   # polite delay between requests


def build_url(station_id):
    """
    Constructs the NRCS Report Generator URL for a single station.
    POR_BEGIN / POR_END = full period of record (no hardcoded date range needed).
    Elements requested:
        WTEQ = Snow Water Equivalent (inches)
        PREC = Precipitation Accumulation (inches)
        SNWD = Snow Depth (inches)
        TAVG = Air Temperature Average (degrees F)
    """
    return (
        "https://wcc.sc.egov.usda.gov/reportGenerator/view_csv/"
        "customSingleStationReport/daily/start_of_period/"
        f"{station_id}:CO:SNTL/"
        "POR_BEGIN,POR_END/"
        "WTEQ::value,PREC::value,SNWD::value,TAVG::value"
    )


def parse_response(response_text, station_id, station_name):
    """
    Parses the raw NRCS CSV response.

    Cleaning steps performed here:
      1. Strips all comment lines beginning with '#' (NRCS metadata/warnings)
      2. Strips the column header line ('Date,...')
      3. Skips blank lines
      4. Limits to first 5 columns (date + 4 elements) in case of extra cols
      5. Strips whitespace from each value
      6. Prepends station_id and station_name to each row

    Empty values are left as empty strings — PostgreSQL \COPY will treat
    these as NULL when the column is nullable, which is correct behavior
    for missing sensor readings.
    """
    rows = []
    for line in response_text.split("\n"):
        # Skip NRCS comment/metadata lines
        if line.startswith("#"):
            continue
        # Skip blank lines
        if not line.strip():
            continue
        # Skip the CSV header row
        if line.startswith("Date"):
            continue

        parts = line.split(",")
        # Must have at least a date field
        if not parts[0].strip():
            continue

        cleaned = [p.strip() for p in parts[:5]]
        rows.append(f"{station_id},{station_name},{','.join(cleaned)}")

    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write CSV header
    with open(OUTPUT_FILE, "w") as f:
        f.write("station_id,station_name,date,swe_in,precip_in,snow_depth_in,temp_avg_f\n")

    success, failed = 0, []
    total_stations = len(STATIONS)

    for i, (sid, name) in enumerate(STATIONS):
        url = build_url(sid)
        try:
            r = requests.get(url, timeout=45)
            r.raise_for_status()

            rows = parse_response(r.text, sid, name)

            with open(OUTPUT_FILE, "a") as f:
                for row in rows:
                    f.write(row + "\n")

            success += 1
            print(f"[{i+1}/{total_stations}] {name} ({sid}): {len(rows)} rows")

        except requests.exceptions.Timeout:
            failed.append((sid, name))
            print(f"  TIMEOUT: {name} ({sid}) — skipping")
        except requests.exceptions.HTTPError as e:
            failed.append((sid, name))
            print(f"  HTTP ERROR: {name} ({sid}): {e}")
        except Exception as e:
            failed.append((sid, name))
            print(f"  FAILED: {name} ({sid}): {e}")

        time.sleep(DELAY_SEC)

    # Final summary
    with open(OUTPUT_FILE) as f:
        total_rows = sum(1 for _ in f) - 1  # subtract header

    print("\n" + "=" * 50)
    print(f"COMPLETE")
    print(f"  Stations downloaded : {success}/{total_stations}")
    print(f"  Stations failed     : {len(failed)}")
    print(f"  Total rows          : {total_rows:,}")
    print(f"  Output file         : {OUTPUT_FILE}")
    print("=" * 50)

    if failed:
        print("\nFailed stations (re-run manually if needed):")
        for sid, name in failed:
            print(f"  {name} ({sid})")

    print("\nTo load into PostgreSQL:")
    print(f"  \\COPY daily_observations FROM '{OUTPUT_FILE}' CSV HEADER;")


if __name__ == "__main__":
    main()
