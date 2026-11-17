"""Evaluate retrieval and compare prompt variants.
  python -m eval.run_eval --retrieval-only   # no API key needed
  python -m eval.run_eval                     # full run, needs ANTHROPIC_API_KEY
"""
import argparse, json, time
from pathlib import Path
from app.config import MODEL
from app.ingest import load_chunks
from app.llm import PROMPTS, answer
from app.retrieval import Retriever

HERE = Path(__file__).parent


def kw(text, kws):
    t = text.lower()
    return sum(k.lower() in t for k in kws) / len(kws)


def refused(text):
    t = text.lower()
    return "could not find" in t or "bulamad" in t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval-only", action="store_true")
    ap.add_argument("--top-k", type=int, default=4)
    a = ap.parse_args()

    items = json.loads((HERE / "eval_set.json").read_text(encoding="utf-8"))
    r = Retriever(load_chunks())
    ans_items = [e for e in items if e["answerable"]]
    refuse_items = [e for e in items if not e["answerable"]]
    retrieved, hits, recall = {}, 0, 0.0
    for e in items:
        ps = retrieved[e["id"]] = r.search(e["question"], a.top_k)
        if e["answerable"]:
            srcs = e["source"] if isinstance(e["source"], list) else [e["source"]]
            hits += any(p["source"] in srcs for p in ps)
            recall += kw(" ".join(p["text"] for p in ps), e["must_include"])
    n = len(ans_items)
    md = [f"# Eval results ({r.backend} retrieval, top_k={a.top_k}, {len(items)} questions)", "",
          f"- Retrieval hit@{a.top_k} (correct lecture in top results): **{hits}/{n}**",
          f"- Context recall (expected facts present in retrieved text): **{recall / n:.0%}**", ""]
    out = {"retrieval": {"hit": hits, "n": n, "context_recall": round(recall / n, 3)}, "variants": {}}

    if not a.retrieval_only:
        md += [f"Model: `{MODEL}`", "",
               "| Prompt variant | Answer accuracy | Correct refusals | Avg latency (s) |", "|---|---|---|---|"]
        fails = {}
        for v in PROMPTS:
            acc = lat = 0.0
            ref, fails[v] = 0, []
            for e in items:
                t0 = time.time()
                txt = answer(e["question"], retrieved[e["id"]], v)
                lat += time.time() - t0
                if e["answerable"]:
                    s = kw(txt, e["must_include"])
                    acc += s
                    if s < 1:
                        fails[v].append(f"{e['question']} (score {s:.0%})")
                elif refused(txt):
                    ref += 1
                else:
                    fails[v].append(f"{e['question']} (should have refused)")
            out["variants"][v] = {"accuracy": round(acc / n, 3), "refusals": f"{ref}/{len(refuse_items)}",
                                  "avg_latency_s": round(lat / len(items), 2)}
            md.append(f"| {v} | {acc / n:.0%} | {ref}/{len(refuse_items)} | {lat / len(items):.2f} |")
        md += ["", "## Missed questions per variant"]
        for v, f in fails.items():
            md += [f"**{v}**"] + ([f"- {x}" for x in f] or ["- none"]) + [""]

    (HERE / "results.md").write_text("\n".join(md), encoding="utf-8")
    (HERE / "results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
