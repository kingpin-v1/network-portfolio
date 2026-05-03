#!/usr/bin/env python3
import socket
import time
import sys
import json
import re

host = "192.168.1.249"
port = int(sys.argv[1])
hostname = sys.argv[2]
commands = sys.argv[3:]

def clean(output):
    # remove telnet negotiation bytes
    output = re.sub(b'\xff[\xfb\xfc\xfd\xfe].', b'', output)
    # remove ANSI/terminal escape sequences
    output = re.sub(rb'\x1b\][^\x07]*\x07', b'', output)
    output = re.sub(rb'\x1b\[[0-9;]*[mGKHF]', b'', output)
    # decode and clean
    text = output.decode('ascii', errors='ignore')
    text = text.replace('\r', '')
    return text.strip()

def recv_until_prompt(s, timeout=5):
    data = b''
    s.settimeout(timeout)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = s.recv(4096)
            if chunk:
                data += chunk
                if b'#' in chunk or b'>' in chunk:
                    break
        except socket.timeout:
            break
    return data

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    
    # wake prompt
    time.sleep(2)
    s.send(b'\r\n')
    recv_until_prompt(s)

    results = {}
    for cmd in commands:
        s.send(cmd.encode('ascii') + b'\r\n')
        raw = recv_until_prompt(s, timeout=10)
        text = clean(raw)
        # remove echoed command and prompt lines
        lines = [l for l in text.split('\n')
                 if l.strip()
                 and cmd not in l
                 and not l.strip().endswith('#')
                 and not l.strip().endswith('>')]
        results[cmd] = '\n'.join(lines).strip()

    s.close()
    print(json.dumps({
        "hostname": hostname,
        "port": port,
        "results": results
    }, indent=2))

except Exception as e:
    print(json.dumps({"error": str(e), "hostname": hostname}))
    sys.exit(1)
