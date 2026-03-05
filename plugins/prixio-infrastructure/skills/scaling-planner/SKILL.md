---
name: scaling-planner
description: >
  Capacity planning and scaling recommendations for Prixio LLC based on traffic
  projections. Analyzes bottlenecks, recommends infrastructure tiers, and generates
  load test configurations. Triggers on: "scale", "scaling", "capacity", "how many
  users", "concurrent", "load test", "bottleneck", "performance", "traffic",
  "requests per second", "can we handle".
allowed-tools: Bash, Read
---

# Scaling Planner

Capacity planning and infrastructure scaling advisor for Prixio LLC platforms
(Lotify and Courio).

## Usage Modes

### 1. Preset Profiles

Quick capacity estimates using predefined traffic levels:

```
capacity_calc.py --preset early       # 100 concurrent users
capacity_calc.py --preset growing     # 500 concurrent users
capacity_calc.py --preset established # 2,000 concurrent users
capacity_calc.py --preset scale       # 10,000 concurrent users
```

### 2. Custom Traffic Input

Fine-grained control over planning parameters:

```
capacity_calc.py --concurrent-users 750 --platform lotify --peak-multiplier 4 --output json
capacity_calc.py --concurrent-users 3000 --platform both --output text
```

Parameters:
- `--concurrent-users N` — Target number of simultaneous users
- `--platform lotify|courio|both` — Which platform(s) to plan for (default: both)
- `--peak-multiplier N` — Burst factor applied to base load (default: 3x)
- `--output json|text` — Output format (default: text)

## What It Outputs

1. **Recommended Infrastructure Tier** — The minimum tier from `tier-benchmarks.md` that
   satisfies the traffic requirements, with headroom analysis.

2. **Bottleneck Identification** — Which resource (DB connections, WebSocket capacity,
   requests/sec, storage) hits its limit first and at what user count.

3. **Resource Breakdown** — Per-resource usage estimates:
   - Requests per second (read/write split)
   - Database connections required
   - WebSocket connections (Lotify bidding, Courio tracking)
   - Storage growth per month (GB)
   - Bandwidth estimates

4. **Warning Flags** — Any resource exceeding 80% of the recommended tier's capacity,
   signaling the need to plan for the next tier.

5. **Cost Estimate** — Monthly infrastructure cost in GEL for the recommended tier.

6. **Platform-Specific Notes** — Auction thundering-herd mitigation for Lotify,
   GPS write optimization for Courio, shared Auth/payment load considerations.

## References

- `references/load-profiles.md` — Traffic patterns and load characteristics per platform
- `references/tier-benchmarks.md` — Infrastructure tiers, capacity limits, and costs
- `scripts/capacity_calc.py` — Automated capacity calculation engine
