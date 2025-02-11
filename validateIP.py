#/usr/bin/env python3

import ipaddress
import csv


#check all unacceptable ip addresses like loopback broadcast etc
def check_wrong_ips(file_path="wrong_ips.csv"):
    try:
        with open(file_path, mode="r", encoding="utf8") as file:
            reader = csv.reader(file)
            return{row[0] for row in reader}

    except FileNotFoundError:
        return set()


#check ip with ipaddress library
def validate_ip(ip):
    wrong_ips = check_wrong_ips()
    if ip in wrong_ips:
        return False
    try:
        ipaddress.ip_address(str(ip))
        return True
    except ValueError:
        return False
#debug
print(validate_ip("255.255.255.255"))
print(validate_ip("127.0.0.1"))
print(validate_ip("8.8.4.4"))
print(validate_ip("301.11.11.11"))
print(validate_ip("3a.11.11.11"))