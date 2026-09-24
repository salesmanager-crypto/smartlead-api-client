#!/usr/bin/env python3
"""Size an Amazon check run: how many browser workers for N brands in M minutes.

Numbers measured on the Surf Expo 2026 list (228 brands, single IP via the session proxy):
  ~3 Amazon page loads per brand, ~0.55 brands/min per worker, throttling above ~8-10 workers.

Usage: plan_run.py <unique_brands> <target_minutes> [--rate 0.55] [--cap 8]
"""
import argparse, math

p = argparse.ArgumentParser()
p.add_argument("brands", type=int)
p.add_argument("minutes", type=float)
p.add_argument("--rate", type=float, default=0.55, help="brands per minute per worker")
p.add_argument("--cap", type=int, default=8, help="max concurrent workers before Amazon throttles")
a = p.parse_args()

need = math.ceil(a.brands / (a.rate * a.minutes))
realistic = math.ceil(a.brands / (a.rate * a.cap))
print(f"brands: {a.brands}   target: {a.minutes:g} min")
print(f"workers needed: {need}   (cap {a.cap})")
if need <= a.cap:
    print(f"PLAN: run {need} worker(s) -> finish in about {a.minutes:g} min. "
          f"Split across {max(1, math.ceil(need/2))} process(es) of 2 workers.")
else:
    print(f"NOT REACHABLE at full quality. Realistic finish with {a.cap} workers: ~{realistic} min.")
    print("Options: accept the longer run | check only Sells/Listed rows | reuse earlier scrape data | SmartScout when allowance allows.")
