#!/usr/bin/env python3
import socket
import time
import re
import sys
import json

HOST = "192.168.1.249"
port = int(sys.argv[1])
hostname = sys.argv[2]
commands = sys.argv[3].split("|||")

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

def send_cmd(s, cmd, timeout=5):
    s.send(cmd.encode("ascii") + b"\r\n")
    return recv_until_prompt(s, timeout)

def clean(data):
    data = re.sub(rb"\xff[\xfb\xfc\xfd\xfe].", b"", data)
    data = re.sub(rb"\x1b\][^\x07]*\x07", b"", data)
    data = re.sub(rb"\x1b\[[0-9;]*[mGKHF]", b"", data)
    return data.decode("ascii", errors="ignore").replace("\r", "")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, port))
    time.sleep(2)
    s.send(b"\r\n")
    recv_until_prompt(s)

    # enter enable mode
    send_cmd(s, "terminal length 0")
    send_cmd(s, "enable")
    send_cmd(s, "cisco123")

    # enter config mode
    send_cmd(s, "configure terminal")

    # push each command
    applied = []
    for cmd in commands:
        cmd = cmd.strip()
        if cmd:
            send_cmd(s, cmd)
            applied.append(cmd)

    # exit and save
    send_cmd(s, "end")
    send_cmd(s, "write memory")
    time.sleep(2)

    s.close()
    print(json.dumps({
        "hostname": hostname,
        "status": "success",
        "commands_applied": len(applied)
    }))

except Exception as e:
    print(json.dumps({
        "hostname": hostname,
        "status": "failed",
        "error": str(e)
    }))
    sys.exit(1)
