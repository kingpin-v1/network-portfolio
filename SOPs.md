# Standard Operating Procedures
## Network Lab Portfolio — Kingpin

> This document defines the standard workflow for all changes to lab topology,
> device configuration, NetBox records, and this GitHub repository.
> Follow these procedures in order for every change, no matter how small.

---

## Table of Contents

1. [Branch & Commit Naming Conventions](#1-branch--commit-naming-conventions)
2. [SOP — Configuration Changes](#2-sop--configuration-changes)
3. [SOP — Topology Changes](#3-sop--topology-changes)
4. [SOP — NetBox Updates](#4-sop--netbox-updates)
5. [SOP — GitHub Workflow](#5-sop--github-workflow)
6. [Change Log](#6-change-log)

---

## 1. Branch & Commit Naming Conventions

### Branches
| Type | Format | Example |
|------|--------|---------|
| New lab feature | `feature/<name>` | `feature/ansible` |
| Config change | `config/<node>-<change>` | `config/AGG1-add-cloud-interface` |
| Topology change | `topology/<description>` | `topology/add-site-E-leg` |
| Bug fix / correction | `fix/<description>` | `fix/AGG2-wrong-area-statement` |
| Documentation | `docs/<description>` | `docs/update-sops` |

### Commit Messages
Follow this format:
```
<type>(<scope>): <short description>

<optional body — what changed and why>
```

| Type | When to use |
|------|-------------|
| `feat` | New capability added to the lab |
| `config` | Device configuration change |
| `topo` | Topology or IP addressing change |
| `docs` | Documentation or portfolio page update |
| `fix` | Correcting an error |
| `netbox` | NetBox record update |

**Examples:**
```
config(AGG1): add Ethernet1/2 cloud bridge interface

Added 192.168.1.253/24 on E1/2 for CLOUD0-LAN-BRIDGE.
Static route 192.168.100.0/24 via 192.168.1.1 added for management reach.

config(all-sites): add passive-interface default to all OSPF processes

Prevents unwanted neighborships on any interface not explicitly opened.

topo(core-edge-ring): rename lab from DWDM Ring — PHY not replicable in EVE-NG
```

---

## 2. SOP — Configuration Changes

> Follow this procedure any time a device configuration is modified in EVE-NG.

### Step 1 — Plan
- [ ] Identify which nodes are affected
- [ ] Confirm IP addressing against the topology IP plan (see portfolio Topology tab)
- [ ] Confirm the change does not conflict with existing OSPF area assignments or summarization

### Step 2 — Create a branch
```bash
git checkout main
git pull origin main
git checkout -b config/<node>-<description>
```

### Step 3 — Apply the change in EVE-NG
- Apply configuration to the device
- Verify with relevant `show` commands:

| Change type | Verification command |
|-------------|---------------------|
| Interface | `show ip interface brief` |
| OSPF neighborship | `show ip ospf neighbor` |
| Routing table | `show ip route` |
| OSPF database | `show ip ospf database` |

### Step 4 — Update the config file in the repo
- Open `labs/core-edge-ring/configs/<NODE>.txt`
- Update the relevant section to reflect the running config
- Keep the file formatted as clean IOS config — no `show` output, no timestamps

### Step 5 — Update the portfolio page
- If the change affects what is displayed in the **Node Configs** tab, update `labs/core-edge-ring/index.html` accordingly
- If a new interface was added, verify the topology SVG is still accurate

### Step 6 — Commit and push
```bash
git add labs/core-edge-ring/configs/<NODE>.txt
git add labs/core-edge-ring/index.html   # if updated
git commit -m "config(<NODE>): <description>"
git push origin config/<node>-<description>
```

### Step 7 — Open a Pull Request and merge to main
- Go to GitHub → open a Pull Request from your branch into `main`
- Add a brief description of what changed and why
- Merge once satisfied — this updates the live portfolio page

### Step 8 — Log the change
- Add an entry to the [Change Log](#6-change-log) at the bottom of this document

---

## 3. SOP — Topology Changes

> Follow this procedure for any structural change: adding/removing nodes, links, areas, or IP subnets.

### Step 1 — Plan
- [ ] Update the IP plan before touching EVE-NG — assign loopbacks, link subnets, and area membership
- [ ] Identify all nodes whose configs will need updating (not just the new node)
- [ ] Check for summarization range impacts on ABR nodes

### Step 2 — Create a branch
```bash
git checkout main
git pull origin main
git checkout -b topology/<description>
```

### Step 3 — Update NetBox first
- Follow the [NetBox SOP](#4-sop--netbox-updates) before making any changes in EVE-NG
- NetBox is the source of truth — EVE-NG follows NetBox, not the other way around

### Step 4 — Apply changes in EVE-NG
- Add/remove nodes and links in the EVE-NG topology
- Apply configurations per the NetBox IP plan

### Step 5 — Update the portfolio page
- Update the SVG topology diagram in `labs/core-edge-ring/index.html`
- Update the IP addressing table
- Update all affected node configs in the **Node Configs** tab
- Update area cards if OSPF areas changed

### Step 6 — Update config files
- Add new node config files to `labs/core-edge-ring/configs/`
- Update any existing nodes whose configs changed

### Step 7 — Commit, push, PR, merge
```bash
git add labs/core-edge-ring/
git commit -m "topo(<scope>): <description>"
git push origin topology/<description>
```
- Open PR → merge to `main`

### Step 8 — Log the change

---

## 4. SOP — NetBox Updates

> NetBox is the single source of truth for all IP addressing and device records.
> No IP should exist in EVE-NG or the portfolio that is not first recorded in NetBox.

### Device Records
When adding a new node:
- [ ] Create the device under **Devices → Devices** with the correct role (Core or Edge)
- [ ] Assign the correct site/location
- [ ] Set the platform to **Cisco IOL**

### IP Addressing
When assigning any IP:
- [ ] Ensure the parent prefix exists (e.g. `10.1.1.0/24` for Leg A links)
- [ ] Create the specific `/30` or `/32` prefix under **IPAM → Prefixes**
- [ ] Assign the IP to the correct device interface under **IPAM → IP Addresses**
- [ ] Set the role: `Loopback` for /32s, `Link` for /30s

### When to update NetBox
| Trigger | Action |
|---------|--------|
| New node added | Create device + all interfaces + IPs |
| New link added | Create /30 prefix, assign both IPs |
| IP changed | Update existing IP record, note old IP in description |
| Node removed | Set device status to **Decommissioned**, do not delete |
| Interface renamed | Update interface record |

### Verification
Before closing any topology or config change, confirm:
- [ ] All IPs in EVE-NG match NetBox
- [ ] All prefixes are assigned to the correct VRF (Global unless otherwise noted)
- [ ] No IP in NetBox is marked **Available** if it is in use in EVE-NG

---

## 5. SOP — GitHub Workflow

> Day-to-day workflow reference.

### Starting any change
```bash
git checkout main
git pull origin main                         # always pull before branching
git checkout -b <type>/<description>
```

### During work
Commit early and often — each logical step gets its own commit:
```bash
git add <file>
git commit -m "<type>(<scope>): <description>"
```

Avoid committing multiple unrelated changes in a single commit.

### Pushing and merging
```bash
git push origin <branch-name>
# Then go to GitHub and open a Pull Request into main
```

- Never push directly to `main`
- Always open a PR, even if you are the only contributor — it creates a record
- Delete the branch after merging to keep the repo clean

### Keeping branches up to date
If `main` has moved ahead while you were working on a branch:
```bash
git checkout main
git pull origin main
git checkout <your-branch>
git merge main
```

### Emergency direct fix to main
Only acceptable for typo/broken link fixes on the live portfolio:
```bash
git checkout main
git pull origin main
# Make the fix
git add <file>
git commit -m "fix: <description>"
git push origin main
```

---

## 6. Change Log

> Log every change here after merging to main. Most recent at the top.

| Date | Branch | Scope | Description | Author |
|------|--------|-------|-------------|--------|
| 2026-04-28 | — | core-edge-ring | Initial portfolio publish — OSPF multi-area, 12 nodes, full IP plan, node configs | Kingpin |

---

*This document is a living SOP — update it as the lab evolves.*
