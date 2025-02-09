#/usr/bin/env python3
import csv
import os

file_path = 'sshInfo.csv'

if os.path.exists(file_path):
    try:
        with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            print(f"{file_path} is exists")
            rows=list(reader)
            if not rows:
                print(f"{file_path} is empty")

            else:
                for row in rows:
                    print(row)

    except csv.Error as e:
                print(f"Cannot read {file_path}")

else:
    print(f"{file_path} is not exists")



#
#with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
#    reader = csv.DictReader(file)
#    for row in reader:
#        print(row)
