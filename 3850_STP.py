from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException,NetMikoAuthenticationException
from paramiko.ssh_exception import SSHException
from credentials import *
import sys
import time

switch_argument = sys.argv[1]
	
cisco_switch = {
	'device_type': 'cisco_ios',
	'ip': switch_argument,
	'username': username,
	'password': password,
	'port' : 22,          # optional, defaults to 22
	'secret': secret,     # optional, defaults to ''
	'verbose': False,       # optional, defaults to False
}

try: # if the switch is reponsive we do our thing, otherwise we hit the exeption below
		# this actually logs into the device
		net_connect = ConnectHandler(**cisco_switch)
		show_spanning_tree_root_command = "show spanning-tree root"
		show_spanning_tree_root = net_connect.send_command(show_spanning_tree_root_command).split("\n")

		STP_results_file = open(switch_argument + ".txt", "a")
		
		for show_spanning_tree_root_line in show_spanning_tree_root:
			if len(show_spanning_tree_root_line) > 1:
				if show_spanning_tree_root_line.split()[0] == "Root":
					continue 
				if show_spanning_tree_root_line.split()[0] == "Vlan":
					continue
				if show_spanning_tree_root_line.split()[0] == "----------------":
					continue
				vlan = int(show_spanning_tree_root_line.split()[0].split("N")[1])
				priority = int(show_spanning_tree_root_line.split()[1]) - vlan
				rootID = str(show_spanning_tree_root_line.split()[2])
				rootPort = str(show_spanning_tree_root_line.split()[7])
				currentTime = time.ctime()
				output = currentTime + "," + str(vlan) + "," + str(priority) + "," + rootID + "," + rootPort  + "\n"
				if priority < 20480:
					STP_results_file.write(output)
				elif rootID != "84b2.618f.be00":
					STP_results_file.write(output)
				elif rootPort != "Po12":
					STP_results_file.write(output)
		net_connect.disconnect()
except (NetMikoTimeoutException, NetMikoAuthenticationException):
	print switch_argument + ',no_response'

STP_results_file.close()
