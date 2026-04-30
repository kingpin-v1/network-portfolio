# Network Engineering Portfolio
### Adam Smith — Senior Network Engineer

A collection of self-built network labs documenting hands-on work with routing protocols, network automation, and infrastructure tooling. Labs run on Cisco IOL images in EVE-NG 6.2.0-4, hosted on a Proxmox VE 8.4 home lab.

🌐 **[View Live Portfolio](https://kingpin-v1.github.io/network-portfolio)**

---

## Labs

| Lab | Status | Topics |
|-----|--------|--------|
| [Core-Edge Ring](labs/core-edge-ring/) | ✅ Live | OSPF Multi-Area, Dual-Homing, ABR Summarization |
| Ansible Automation | 🔧 In Progress | Ansible, YAML, Network Automation |
| NetBox — Source of Truth | 📋 Planned | IPAM, DCIM, REST API |

---

## Repository Structure

```
network-portfolio/
├── index.html                  ← Portfolio landing page
├── README.md                   ← This file
├── labs/
│   └── core-edge-ring/
│       ├── index.html          ← Lab portfolio page
│       └── configs/            ← Per-node IOS configuration files
└── assets/                     ← Shared styles and resources
```

---

## Branching Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Live portfolio — what the public URL serves |
| `feature/<name>` | New lab or capability (e.g. `feature/ansible`) |
| `config/<node>-<change>` | Device configuration updates |
| `topology/<description>` | Topology or IP addressing changes |
| `fix/<description>` | Corrections to existing content |

All changes are developed on a dedicated branch and merged into `main` via Pull Request.

---

## Home Lab

| Component | Detail |
|-----------|--------|
| Hypervisor | Proxmox VE 8.4 |
| Host CPU | Intel Xeon E5-2618L v4 (20 cores) |
| Host RAM | 62 GB |
| EVE-NG | Community 6.2.0-4 — VM ID 121 |
| Router Image | Cisco IOL x86_64 (CML Free refplat) |

---

*Actively studying for CCNP ENCORE and ENARSI.*
