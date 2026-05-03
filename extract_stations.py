import csv

with open('snowpack_data\\snotel_all_stations_test.csv', 'r', newline='') as infile:
    with open('stations.csv', 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['station_id', 'station_name'])
        writer.writeheader()
        seen = set()
        for row in reader:
            if row['station_id'] in seen:
                continue
            writer.writerow({'station_id' : row['station_id'], 'station_name' : row['station_name']})
            seen.add(row['station_id'])

