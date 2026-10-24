"""Rebuild the SmartScout sellers / subcategory rows straight from the subagents' raw tool results, so no value
depends on an agent copying it correctly.

  python3 pipeline/ssd_from_transcripts.py      -> pipeline/work/ssd_tx/ssd_sellers_tx.jsonl, ssd_subcats_tx.jsonl

Every run_query / query_analytics result in the session's subagent transcripts whose rows carry "Brand Name" plus
"Seller Name" (sellers) or "Subcategory Context Name" (subcategories) is kept; rows are deduped on
(Brand Name, Rn). expowest_smartscout.detail_rows reads these files instead of the agents' own copies when present.
"""
import glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT

TX = os.path.expanduser("~/.claude/projects/-home-user-smartlead-api-client/14097a83-43ed-5901-b09e-9a152d499e4d/subagents")
OUT = os.path.join(ROOT, "pipeline", "work", "ssd_tx")


def results(path):
    """Yield the parsed JSON of every SmartScout tool result in one transcript."""
    smart = set()
    for line in open(path, encoding="utf-8"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (d.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if b.get("type") == "tool_use" and "SmartScout" in b.get("name", ""):
                smart.add(b["id"])
            elif b.get("type") == "tool_result" and b.get("tool_use_id") in smart:
                t = b.get("content")
                texts = [t] if isinstance(t, str) else [x.get("text", "") for x in t or [] if isinstance(x, dict)]
                for s in texts:
                    try:
                        yield json.loads(s)
                    except (json.JSONDecodeError, TypeError):
                        continue


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = {"sellers": {}, "subcats": {}}
    for path in sorted(glob.glob(os.path.join(TX, "agent-*.jsonl"))):
        for r in results(path):
            for row in r.get("result") or []:
                if not isinstance(row, dict) or "Brand Name" not in row or "Rn" not in row:
                    continue
                kind = "sellers" if "Seller Name" in row else "subcats" if "Subcategory Context Name" in row else None
                if kind:
                    seen[kind].setdefault((row["Brand Name"].lower(), row["Rn"]), row)
    for kind, rows in seen.items():
        with open(os.path.join(OUT, f"ssd_{kind}_tx.jsonl"), "w", encoding="utf-8") as fh:
            for row in rows.values():
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(kind, len(rows), "rows,", len({k[0] for k in rows}), "brands")


if __name__ == "__main__":
    main()
