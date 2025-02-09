import subprocess
import csv

with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        ip = reader['host']

ans = subprocess.call(["ping", {host}])
if ans == 0:
    print("Command executed.")
else:
    print("Command failed.", return_code)
