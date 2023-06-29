import csv


def extractInputCSV(filepath):
    input = []
    with open(str(filepath), encoding="utf-8") as File:
        reader = csv.DictReader(File)
        for row in reader:
            input.append(row)
    return input
