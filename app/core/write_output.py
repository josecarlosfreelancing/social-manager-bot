import csv


def OutputCSV(filepath, list, header):
    myFile = open(filepath, 'w', encoding="utf-8")
    writer = csv.writer(myFile)
    writer.writerow([header])
    for l in list:
        writer.writerow([l])
