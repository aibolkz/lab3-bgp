import subprocess
import csv

with open('sshInfo.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        ip = row['host']
        command = ["ping", "-c", "2", ip]
        ans = subprocess.call(command)
        if ans == 0:
            print("ping was succesful.")
        else:
            print(f"Ping failed, command is {ip} with return code {ans})
