import csv

SEAS_TO_MONTH = {
    'DJF': 1,
    'JFM': 2,
    'FMA': 3,
    'MAM': 4,
    'AMJ': 5,
    'MJJ': 6,
    'JJA': 7,
    'JAS': 8,
    'ASO': 9,
    'SON': 10,
    'OND': 11,
    'NDJ': 12,
}

with open("Monthly_ONI.csv", 'r', newline='') as infile:
    with open("cleaned_Monthly_ONI.csv", 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['year', 'month', 'oni'])
        writer.writeheader()
        for row in reader:
                if row['SEAS'] not in SEAS_TO_MONTH or int(row['YR']) < 1980:
                    continue
                writer.writerow({'year': int(row['YR']), 'month': SEAS_TO_MONTH[row['SEAS']], 'oni': float(row['ANOM'])})
