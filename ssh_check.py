import subprocess
import csv

with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        ip = row['host']

ans = subprocess.call(["ping", "-c", "2", [ip])
if ans == 0:
    print("ping was succesful.")
else:
    print("Ping failed, command is {ip} with return code {ans}|)
