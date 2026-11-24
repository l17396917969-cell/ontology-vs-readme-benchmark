"""Run the blind risk-discovery matrix. 'grade' recomputes it locally."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
import json
import math
import os
from pathlib import Path
from random import Random
import re
from time import perf_counter

from openai import OpenAI
from cases import ROOTS, KINDS, WORLDS, catalogue, markdown, scenario

HERE = Path(os.getenv("BENCH_ARTIFACT_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
ARMS = ("full_readme", "keyword_readme", "graph_neighbors")
SIZES = ("small", "large")
REPEATS = (1, 2)
LIMIT = 10
MODEL = "deepseek-flash"
SYSTEM = (
    "You review enterprise operations. Use only the records supplied. No action and no outside facts. "
    "Trace dependencies and check conditions for the named subject. Report one material issue if supported, "
    "otherwise clear only if the decisive records are available and support that conclusion, "
    "or insufficient if essential facts cannot be established. "
    "Return JSON with verdict (risk, clear or insufficient), key_ids (array of decisive object IDs; "
    "include intermediate action/object IDs needed to explain a risk), "
    "evidence_ids (all the decisive relationship record IDs, e.g. T1, including unavailable records "
    "if they affect the verdict), and explanation (one or two sentences specifying the effect)."
)
REVIEW_AREAS = {
    "sourcing": "supply continuity for this production line",
    "recovery": "the plan to bring this site back online",
    "approval": "the control over release of this payment",
}


def ranked(query, texts):
    def words(string):
        return re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", string.lower())
    chunks = {key: Counter(words(value)) for key, value in texts.items()}
    avg = sum(x.total() for x in chunks.values()) / len(chunks)
    scores = dict.fromkeys(texts, 0.0)
    for word in sorted(set(words(query))):
        freq = sum(word in vector for vector in chunks.values())
        weight = math.log1p((len(chunks) - freq + .5) / (freq + .5))
        for key, counts in chunks.items():
            count = counts[word]
            scores[key] += weight * 2.2 * count / (count + 1.2 * (.25 + .75 * counts.total() / avg))
    return sorted(texts, key=lambda key: (-scores[key], key))


def neighborhood(root, links):
    visited = []
    unseen = [root]
    for _ in range(5):   # 0–4 hops from the requested object
        current = [node for node in dict.fromkeys(unseen) if node not in visited]
        visited.extend(current)
        unseen = [dest for node in current for dest in links[node]]
    return visited[:LIMIT]


def build():
    cases = {}
    for kind, world, size in product(KINDS, WORLDS, SIZES):
        root = ROOTS[kind]
        query = f"Review {REVIEW_AREAS[kind]} for {root}. Is there a material issue to raise? Explain what the records establish."
        facts = catalogue(kind, world, size)
        texts = {r.id: markdown(r) for r in facts}
        graph = {r.id: [dest for _, _, dest in r.edges if dest] for r in facts}
        links = {key: [dest.upper() for dest in re.findall(r"\]\(#([a-z0-9-]+)\)", value)]
                 for key, value in texts.items()}
        assert graph == links
        graph_docs = neighborhood(root, graph)
        linked_docs = neighborhood(root, links)
        assert [texts[k] for k in graph_docs] == [texts[k] for k in linked_docs]
        _, decisive, witness = scenario(kind, world)
        selected = {
            "full_readme": list(texts),
            "keyword_readme": ranked(query, texts)[:LIMIT],
            "graph_neighbors": graph_docs,
        }
        for arm, nodes in selected.items():
            receipts = sorted({e for r in facts if r.id in nodes for e, _, _ in r.edges})
            material = "\n\n".join(texts[key] for key in nodes)
            cases[(kind, world, size, arm)] = {
                "scope": root, "prompt": f"{material}\n\n{query}", "nodes": nodes, "receipts": receipts,
                "asset_count": len(texts), "verdict": {"risk": "risk", "clear": "clear", "unknown": "insufficient"}[world],
                "decisive": decisive if world == "risk" else set(), "witness": witness, "question": query,
            }
    return cases


def ask(client, job, case):
    start = perf_counter()
    reply = client.chat.completions.create(
        model=MODEL, max_tokens=1100, temperature=0,
        extra_body={"thinking": {"type": "disabled"}},
        response_format={"type": "json_object"},
        messages=[{"role":"system","content":SYSTEM}, {"role":"user","content":case["prompt"]}],
    )
    choice = reply.choices[0]
    return {
        "job": job, "id": reply.id, "model": reply.model, "raw": choice.message.content,
        "finished": choice.finish_reason, "input_tokens": reply.usage.prompt_tokens,
        "output_tokens": reply.usage.completion_tokens, "model_seconds": round(perf_counter() - start, 3),
    }


def grade(row, case):
    try:
        p = json.loads(row["raw"])
        verdict = p["verdict"]
        ids = set(p["key_ids"])
        cited = set(p["evidence_ids"])
        explanation = p["explanation"]
        assert isinstance(explanation, str) and explanation.strip()
        assert isinstance(p["key_ids"], list) and isinstance(p["evidence_ids"], list)
    except (ValueError, TypeError, KeyError, AssertionError):
        verdict, ids, cited, explanation = None, set(), set(), ""
    core_ok = verdict == case["verdict"]
    evidence_ok = case["witness"] <= cited <= set(case["receipts"]) and case["decisive"] <= ids <= set(case["nodes"])
    return {**row, "asset_count": case["asset_count"], "question": case["question"],
            "selected_nodes": case["nodes"], "references_visible": case["witness"] <= set(case["receipts"]),
            "expected_verdict": case["verdict"], "expected_witness": sorted(case["witness"]),
            "verdict_correct": core_ok, "grounded_correct": core_ok and evidence_ok,
            "observed_verdict": verdict, "observed_explanation": explanation}


def report(rows):
    result = {}
    for size, arm in product(SIZES, ARMS):
        subset = [r for r in rows if tuple(r["job"][2:4]) == (size,arm)]
        if not subset:
            continue
        worlds = Counter((r["job"][0],r["job"][4]) for r in subset if r["grounded_correct"])
        result[f"{size}/{arm}"] = {
            "calls": len(subset),
            "correct_verdict": sum(r["verdict_correct"] for r in subset),
            "grounded_correct": sum(r["grounded_correct"] for r in subset),
            "complete_three_world_triads": sum(count == 3 for count in worlds.values()),
            "visible_witness": sum(r["references_visible"] for r in subset),
            "average_input_tokens": round(sum(r["input_tokens"] for r in subset)/len(subset),1),
        }
    return result


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("prepare", "run", "grade"))
    mode = p.parse_args().mode
    cases = build()
    jobs = [(*key, rep) for key, rep in product(cases, REPEATS)]
    cards = {}
    for kind, world, size in product(KINDS, WORLDS, SIZES):
        facts, _, _ = scenario(kind, world)
        cards[f"{kind}/{world}"] = [markdown(r) for r in facts]
    (HERE/"core-cards.json").write_text(json.dumps(cards, indent=2)+"\n")
    if mode == "prepare":
        print(f"{len(jobs)} calls planned; graph traversal and README link parsing select identical text for each case.")
        return
    raw_path = HERE/"raw.jsonl"
    raw = {tuple(r["job"]):r for r in map(json.loads,raw_path.read_text().splitlines())} if raw_path.exists() else {}
    if mode == "run":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Set DEEPSEEK_API_KEY to run live requests.")
        client = OpenAI(api_key=key,base_url="https://api.deepseek.com",timeout=60,max_retries=1)
        todo = [job for job in jobs if job not in raw]
        Random(235).shuffle(todo)
        with raw_path.open("a") as file, ThreadPoolExecutor(max_workers=8) as pool:
            tasks = {pool.submit(ask,client,job,cases[job[:4]]):job for job in todo}
            for call in as_completed(tasks):
                job = tasks[call]
                try:
                    row = call.result()
                except Exception as exc:
                    print(job,type(exc).__name__,getattr(exc,"status_code",""),flush=True)
                    continue
                raw[job] = row
                file.write(json.dumps(row,ensure_ascii=False)+"\n")
                file.flush()
                if len(raw) % 18 == 0:
                    print(f"Completed {len(raw)}/{len(jobs)}",flush=True)
    rows = [grade(raw[j],cases[j[:4]]) for j in jobs if j in raw]
    summary = report(rows)
    (HERE/"results.json").write_text(json.dumps({"calls":len(rows),"summary":summary,"results":rows},indent=2,ensure_ascii=False)+"\n")
    for key,value in summary.items():
        print(key,value)
    if len(rows) != len(jobs):
        raise SystemExit(f"missing {len(jobs)-len(rows)} calls")


if __name__ == "__main__":
    main()
