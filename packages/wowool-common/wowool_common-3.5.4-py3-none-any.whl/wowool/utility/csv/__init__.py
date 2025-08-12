def to_csv(csvfile, headers, data):
    import csv
    from io import TextIOBase

    if isinstance(csvfile, TextIOBase):
        csvfile_hd = csvfile
    else:
        csvfile_hd = open(str(csvfile), "w")

    csvwriter = csv.writer(csvfile_hd)
    csvwriter.writerow(headers)

    # writing the data rows
    rows = []
    for row in data:
        csv_row = []
        for field in headers:
            if field in row:
                csv_row.append(row[field])
            else:
                csv_row.append("")
        rows.append(csv_row)
    csvwriter.writerows(rows)

    if not isinstance(csvfile, TextIOBase):
        csvfile_hd.close()
