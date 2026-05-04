#!/usr/bin/env python3
import socket
import time
import re
import yaml
import os

NODES = {
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

LOOPBACKS = {
    "AGG1":    "10.0.0.1",
    "AGG2":    "10.0.0.2",
    "AGG3":    "10.0.0.3",
    "AGG4":    "10.0.0.4",
    "Site-A1": "10.0.0.11",
    "Site-A2": "10.0.0.12",
    "Site-B1": "10.0.0.21",
    "Site-B2": "10.0.0.22",
    "Site-C1": "10.0.0.31",
    "Site-C2": "10.0.0.32",
    "Site-D1": "10.0.0.41",
    "Site-D2": "10.0.0.42",
}

CORE_NODES = {"AGG1", "AGG2", "AGG3", "AGG4"}
HOST = "192.168.1.249"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../inventory/host_vars")

AREA_MAP = {
    "10.1.0": "Area0",
    "10.1.1": "Area1",
    "10.1.2": "Area2",
    "10.1.3": "Area3",
    "10.1.4": "Area4",
}

def recv_until_prompt(s, timeout=5):
    data = b""
    s.settimeout(timeout)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = s.recv(4096)
            if chunk:
                data += chunk
                if b"#" in chunk or b">" in chunk:
                    break
        except socket.timeout:
            break
    return data

def send_cmd(s, cmd, timeout=8):
    s.send(cmd.encode("ascii") + b"\r\n")
    return recv_until_prompt(s, timeout)

def clean(data):
    data = re.sub(rb"\xff[\xfb\xfc\xfd\xfe].", b"", data)
    data = re.sub(rb"\x1b\][^\x07]*\x07", b"", data)
    data = re.sub(rb"\x1b\[[0-9;]*[mGKHF]", b"", data)
    return data.decode("ascii", errors="ignore").replace("\r", "")

def get_cdp(node, port):
    print(f"  Connecting to {node}...", flush=True)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, port))
    time.sleep(2)
    s.send(b"\r\n")
    recv_until_prompt(s)
    send_cmd(s, "terminal length 0")
    raw = send_cmd(s, "show cdp neighbors detail", timeout=10)
    s.close()
    return clean(raw)

def parse_cdp(output):
    neighbors = []
    for block in re.split(r"-{5,}", output):
        if "Device ID" not in block:
            continue
        nbr = {}
        m = re.search(r"Device ID:\s*(\S+)", block)
        if m:
            nbr["device"] = m.group(1).split(".")[0]
        m = re.search(r"Interface:\s*(\S+),", block)
        if m:
            nbr["local_intf"] = m.group(1).rstrip(",")
        m = re.search(r"Port ID \(outgoing port\):\s*(\S+)", block)
        if m:
            nbr["remote_intf"] = m.group(1)
        m = re.search(r"IP address:\s*(\S+)", block)
        if m:
            nbr["ip"] = m.group(1)
        if "device" in nbr and "local_intf" in nbr:
            neighbors.append(nbr)
    return neighbors

def get_subnet(ip):
    parts = ip.split(".")
    base = (int(parts[3]) // 4) * 4
    return f"{parts[0]}.{parts[1]}.{parts[2]}.{base}/30"

def get_role(local_node, remote_device):
    remote_upper = remote_device.upper().replace("-", "")
    core_upper = {n.replace("-", "") for n in CORE_NODES}
    local_core = local_node in CORE_NODES
    remote_core = remote_upper in core_upper
    if local_core and remote_core:
        return "Connect"
    elif local_core:
        return "Downlink"
    else:
        return "Uplink"

def normalise(name):
    name = re.sub(r"^agg(\d+)$", r"AGG\1", name, flags=re.IGNORECASE)
    name = re.sub(r"^site-([a-d])(\d+)$", lambda m: f"Site-{m.group(1).upper()}{m.group(2)}", name, flags=re.IGNORECASE)
    return name

def abbrev_intf(intf):
    return re.sub(r"Ethernet(\d+/\d+)", r"E\1", intf)

def generate_host_vars(node, neighbors):
    interfaces = []
    for nbr in neighbors:
        role = get_role(node, nbr["device"])
        subnet = get_subnet(nbr["ip"]) if "ip" in nbr else "unknown"
        prefix = ".".join(nbr["ip"].split(".")[:3]) if "ip" in nbr else ""
        area = AREA_MAP.get(prefix, "unknown")
        dev = normalise(nbr["device"])
        interfaces.append({
            "name": nbr["local_intf"],
            "description": f"{role} | {dev} {abbrev_intf(nbr['remote_intf'])} | {area} | {subnet}"
        })
    if node == "AGG1":
        interfaces.append({
            "name": "Ethernet1/2",
            "description": "CLOUD0-LAN-BRIDGE | 192.168.1.253/24"
        })
    interfaces.append({
        "name": "Loopback0",
        "description": f"{node} | Router-ID {LOOPBACKS[node]}"
    })
    interfaces.sort(key=lambda x: x["name"])
    return {"interfaces": interfaces}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for node, port in NODES.items():
        try:
            cdp_output = get_cdp(node, port)
            neighbors = parse_cdp(cdp_output)
            host_vars = generate_host_vars(node, neighbors)
            outfile = os.path.join(OUTPUT_DIR, f"{node}.yml")
            with open(outfile, "w") as f:
                yaml.dump(host_vars, f, default_flow_style=False, allow_unicode=True)
            print(f"  OK {node} — {len(neighbors)} neighbors")
        except Exception as e:
            print(f"  FAIL {node} — {e}")
    print("\nGenerated files:")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        print(f"  {f}")

if __name__ == "__main__":
    print("Discovering CDP neighbors...\n")
    main()
    print("\nDone.")
