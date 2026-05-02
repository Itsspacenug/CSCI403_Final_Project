import csv

month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

with open("PDO.csv", 'r', newline='') as infile:
    with open("cleaned_PDO.csv", 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=['year', 'month', 'pdo'])
        writer.writeheader()
        for row in reader:
            for i, month_name in enumerate(month_names, start=1):
                try:
                    value = float(row[month_name])
                except ValueError: 
                    continue
                if value == 99.99 or int(row['Year']) < 1980:
                    continue
                writer.writerow({'year': int(row['Year']), 'month': i, 'pdo': value })
