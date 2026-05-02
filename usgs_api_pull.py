import csv
import requests
import time

SITES = {
    "Colorado R at Glenwood Springs":   "09085000",
    "South Platte R at Steamboat Rock": "06710385",
    "Arkansas R at Canon City":         "07096000",
    "Rio Grande at Alamosa":            "08227000",
    "Gunnison R at Grand Junction":     "09152500",
}

with open("streamflow.csv", "w", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=["site_no", "site_name", "date", "discharge_cfs"])
    writer.writeheader()

    for site_name, site_no in SITES.items():
        print(f"Fetching {site_name}...")
        r = requests.get("https://waterservices.usgs.gov/nwis/dv/", params={
            "format":      "json",
            "sites":       site_no,
            "startDT":     "1980-10-01",
            "endDT":       "2025-09-30",
            "parameterCd": "00060",
            "statCd":      "00003",
        }, timeout=60)
        r.raise_for_status()

        values = r.json()["value"]["timeSeries"][0]["values"][0]["value"]
        for v in values:
            writer.writerow({
                "site_no":       site_no,
                "site_name":     site_name,
                "date":          v["dateTime"][:10],
                "discharge_cfs": v["value"],
            })
        print(f"  -> {len(values)} rows")
        time.sleep(0.5)

print("Done! streamflow.csv is ready.")