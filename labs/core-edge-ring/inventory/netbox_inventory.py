#!/usr/bin/env python3
"""
Dynamic Ansible inventory from NetBox.
Usage: ansible-playbook -i netbox_inventory.py playbook.yml
"""
import json
import sys
import warnings
import pynetbox

warnings.filterwarnings('ignore')

NETBOX_URL   = "https://192.168.1.185"
NETBOX_TOKEN = "76aef8bdcf0d04e9b0a27b54e00463a9f9fd419b"

# EVE-NG telnet port mapping — keyed by device name
EVE_PORTS = {
    "AGG1":    32769,
    "AGG2":    32770,
    "AGG3":    32771,
    "AGG4":    32772,
    "Site-A1": 32773,
    "Site-A2": 32774,
    "Site-B1": 32775,
    "Site-B2": 32776,
    "Site-C1": 32778,
    "Site-C2": 32777,
    "Site-D1": 32780,
    "Site-D2": 32779,
}

def get_inventory():
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
    nb.http_session.verify = False

    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"children": ["core", "edge"]},
        "core": {"hosts": [], "vars": {}},
        "edge": {"children": ["edge_a", "edge_b", "edge_c", "edge_d"]},
        "edge_a": {"hosts": []},
        "edge_b": {"hosts": []},
        "edge_c": {"hosts": []},
        "edge_d": {"hosts": []},
    }

    # common vars for all hosts
    common_vars = {
        "ansible_connection":       "network_cli",
        "ansible_network_os":       "cisco.ios.ios",
        "ansible_host":             "192.168.1.249",
        "ansible_user":             "admin",
        "ansible_password":         "cisco123",
        "ansible_enable_password":  "cisco123",
        "ansible_become":           True,
        "ansible_become_method":    "enable",
        "ansible_command_timeout":  60,
    }

    devices = nb.dcim.devices.all()

    for device in devices:
        name = device.name
        role = device.role.slug if device.role else ""
        port = EVE_PORTS.get(name)

        if not port:
            continue

        # build host vars
        hostvars = {**common_vars, "ansible_port": port}

        # add NetBox metadata
        hostvars["netbox_id"]     = device.id
        hostvars["netbox_role"]   = device.role.name if device.role else ""
        hostvars["netbox_status"] = str(device.status)
        if device.primary_ip:
            hostvars["netbox_primary_ip"] = str(device.primary_ip)

        inventory["_meta"]["hostvars"][name] = hostvars

        # assign to group based on role
        if role == "agg-router":
            inventory["core"]["hosts"].append(name)
        elif name.startswith("Site-A"):
            inventory["edge_a"]["hosts"].append(name)
        elif name.startswith("Site-B"):
            inventory["edge_b"]["hosts"].append(name)
        elif name.startswith("Site-C"):
            inventory["edge_c"]["hosts"].append(name)
        elif name.startswith("Site-D"):
            inventory["edge_d"]["hosts"].append(name)

    return inventory

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(get_inventory(), indent=2))
    elif len(sys.argv) == 2 and sys.argv[1] == "--host":
        print(json.dumps({}))
    else:
        print(json.dumps(get_inventory(), indent=2))
