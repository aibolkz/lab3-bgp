#/usr/bin/env python3
import csv

with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)
