import csv
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

removed = 0
kept = 0

with open(input_path, newline='') as infile, open(output_path, 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

    writer.writeheader()

    for row in reader:
        try:
            bus_v = float(row.get("bus_v", 0))
        except ValueError:
            bus_v = 0

        if bus_v == 0:
            removed += 1
            continue

        writer.writerow(row)
        kept += 1

print(f"[OK] Filtered file written to: {output_path}")
print(f"[INFO] Rows kept: {kept}")
print(f"[INFO] Rows removed (bus_v == 0): {removed}")
