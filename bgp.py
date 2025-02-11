#!/usr/bin/env python3

import json
import csv
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor

# load ssh
def load_ssh_info(file_path="sshInfo.csv"):
    ssh_info = {}
    with open(file_path, mode="r", encoding="utf8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ssh_info[row["host"]] = {  # ip is key!
                "device_type": row["device_type"],
                "host": row["host"],
                "username": row["username"],
                "password": row["password"],
                "secret": row["password"]
            }
    print(f" ssh info: {ssh_info.keys()}")
    return ssh_info



# check ssh
def is_ssh_available(router_name, ssh_info):
    if router_name not in ssh_info:
        print(f"error no infor for  {router_name}")
        print(f"! access keys: {list(ssh_info.keys())}")
        return
    try:
        with ConnectHandler(**ssh_info[router_name]) as net_connect:
            net_connect.disconnect()
        print(f"SSH open: {router_name}")
        return True
    except Exception as e:
        print(f"error SSH for {router_name}: {e}")
        return False

# loading bgp conf
def load_bgp_config(file_path="bgp.conf"):
    with open(file_path, "r") as bgp_file:
        return json.load(bgp_file)

# Main BGP configuration
def configure_bgp(router_name, router_data, ssh_info):
    if router_name not in ssh_info:
        print(f"error no SSH info {router_name}")
        return
    print(f"! info connecting to {router_name} ({ssh_info[router_name]['host']})")
    try:
        with ConnectHandler(**ssh_info[router_name]) as net_connect:
            net_connect.enable()
            print(f"! info {router_name}:static routes")
           
            if router_name == "198.51.100.1":
                neighbor_loopback = "20.20.20.1" 
                next_hop = "198.51.100.3" 
                print(f"! info {router_name}: adding neigbors")
                net_connect.send_command(f"neighbor 198.51.100.3 remote-as 100", expect_string=r"#", delay_factor=2)
                net_connect.send_command(f"neighbor 20.20.20.1 remote-as 100", expect_string=r"#", delay_factor=2)
                net_connect.send_command(f"neighbor 22.22.22.1 remote-as 100", expect_string=r"#", delay_factor=2)

           
            elif router_name == "198.51.100.3":
                neighbor_loopback = "10.10.10.1" 
                next_hop = "198.51.100.1"  
                print(f"! info {router_name}: adding neigbors")
                net_connect.send_command(f"neighbor 198.51.100.1 remote-as 100", expect_string=r"#", delay_factor=2)
                net_connect.send_command(f"neighbor 10.10.10.1 remote-as 100", expect_string=r"#", delay_factor=2)
                net_connect.send_command(f"neighbor 11.11.11.1 remote-as 100", expect_string=r"#", delay_factor=2)

            route_cmd = f"ip route {neighbor_loopback} 255.255.255.255 {next_hop}"
            print(f"! sending command: {route_cmd}")
            net_connect.send_command("conf t", expect_string=r"#", delay_factor=2)
            net_connect.send_command(route_cmd, expect_string=r"#", delay_factor=2)
            print(f"! info {router_name}: adding routes: {route_cmd}")
            print(f"! info {router_name}: setting BGP")
            # bgp configuration
            net_connect.send_command(f"router bgp {router_data['local_asn']}", expect_string=r"#", delay_factor=2)
            net_connect.send_command(f"neighbor {router_data['neighbor_ip']} remote-as {router_data['neighbor_remote_as']}", expect_string=r"#", delay_factor=2)
            net_connect.send_command(f"neighbor {router_data['neighbor_ip']} update-source {router_data['update_source']}", expect_string=r"#", delay_factor=2)
            net_connect.send_command(f"neighbor {router_data['neighbor_ip']} next-hop-self", expect_string=r"#", delay_factor=2)
            # advertise networks
            for network in router_data["NetworkListToAdvertise"]:
                net, mask = network.split(" mask ")
                command = f"network {net} mask {mask}"
                net_connect.send_command(command, expect_string=r"#", delay_factor=2)
                print(f"! info {router_name}: {command}")
            print(f"! info {router_name}: BGP configured")
            net_connect.send_command("end", expect_string=r"#", delay_factor=2)
            net_connect.send_command("write memory", expect_string=r"#", delay_factor=2)  # Сохраняем изменения

    except Exception as e:
        print(f"error on device {router_name}: {e}")




# getting neigbors status
def get_bgp_state(router_name, router_data, ssh_info, bgp_config):
    print(f"! check {router_name}, sending ssh_info: {list(ssh_info.keys())}")
    print(f"! bgp_config: {list(bgp_config['Routers'].keys())}")

    try:
        with ConnectHandler(**ssh_info[router_name]) as net_connect:
            net_connect.enable()
            output = net_connect.send_command("show ip bgp neighbors")
            print(f"! {router_name} output of 'show ip bgp neighbors':\n{output}")  
            state = "Unknown"
            if "Established" in output:
                state = "Established"
            elif "Idle" in output:
                state = "Idle"
            elif "Active" in output:
                state = "Active"
            bgp_config["Routers"][router_name]["BGP_Neighbor_Info"] = {
                "BGP Neighbor IP": router_data["neighbor_ip"],
                "BGP Neighbor AS": router_data["neighbor_remote_as"],
                "BGP Neighbor State": state
            }
            print(f"! info {router_name}: BGP State -> {state}")

    except Exception as e:
        print(f"error getting bgp state {router_name}: {e}")


#get bgp routes
def get_bgp_routes(router_name, ssh_info):
    try:
        with ConnectHandler(**ssh_info[router_name]) as net_connect:
            net_connect.enable()
            output = net_connect.send_command("show ip bgp")
            bgp_routes = [line.split()[0] for line in output.split("\n") if "/" in line]
            print(f"{router_name} BGP Routes: {bgp_routes}")

    except Exception as e:
        print(f"error getting bgp routes {router_name}: {e}")

# save running conf
def save_running_config(router_name, ssh_info):
    try:
        with ConnectHandler(**ssh_info[router_name]) as net_connect:
            net_connect.enable()
            output = net_connect.send_command("write memory")
            filename = f"{router_name}_running_config.txt"
            with open(filename, "w") as f:
                f.write(output)
            print(f"! info saved config {filename}")

    except Exception as e:
        print(f"error during saving config {router_name}: {e}")

#run all tasks
def run_tasks(ssh_info, bgp_config):
    tasks = [configure_bgp, get_bgp_state, get_bgp_routes, save_running_config]
    with ThreadPoolExecutor() as executor:
        for router_name, router_data in bgp_config["Routers"].items():
            print(f"! configuring bgp {router_name}")  # Добавлено
            executor.submit(configure_bgp, router_name, router_data, ssh_info)  # Теперь вызывается




#Main part
if __name__ == "__main__":
    ssh_info = load_ssh_info()
    bgp_config = load_bgp_config()
    #check ssh 
    for router in ssh_info.keys():
        is_ssh_available(router, ssh_info)
    #run
    run_tasks(ssh_info, bgp_config)
    #save updated BGP 
    with open("bgp_updated.json", "w") as f:
        json.dump(bgp_config, f, indent=2)
    print("the script has been finished")
