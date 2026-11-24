"""Run the frozen catalogue experiment; use 'prepare' or 'grade' offline."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
from random import Random
import re
import sqlite3
import time

from openai import OpenAI

from fixture import assets, questions, snapshot

HERE = Path(os.getenv("BENCH_ARTIFACT_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
MODEL = "deepseek-flash"
LIMIT = 6
SYSTEM = ("You are an analyst querying synthetic enterprise records. Use only the catalogue below. "
          "Return a JSON object with a single key sql. For a question supported by the catalogue, "
          "set sql to one read-only SQLite query returning one row and one scalar column. "
          "For a question that cannot be answered from the available assets, set sql to null. "
          "There is no interactive database tool or opportunity to retry. "
          "Do not invent relationships, definitions, fields or tables.")
ARMS = ("full", "bm25", "linked", "oracle")
SCOPES = ("domain", "enterprise")
SNAPSHOTS = ((24, 41), (24, 73), (240, 41), (240, 73))
TOKENIZE = re.compile(r"[a-z]+[0-9]*|[0-9]+")


def tokens(text):
    return TOKENIZE.findall(text.lower())


def rank(query, cards):
    counts = {key: Counter(tokens(text)) for key, text in cards.items()}
    avg = sum(map(lambda v: v.total(), counts.values())) / len(counts)
    scores = dict.fromkeys(cards, 0.0)
    for token in sorted(set(tokens(query))):
        df = sum(token in count for count in counts.values())
        idf = math.log1p((len(cards) - df + 0.5) / (df + 0.5))
        for key, count in counts.items():
            f = count[token]
            normalizer = 1.2 * (0.25 + 0.75 * count.total() / avg)
            scores[key] += idf * f * 2.2 / (f + normalizer)
    return scores


def linked(scores, relations, anchors):
    # One lexical entry per query, then best-first traversal of its business relationships.
    seed = anchors[0]
    selected = [seed]
    frontier = {k for k in relations[seed] if k in scores}
    while frontier and len(selected) < LIMIT:
        key = min(frontier, key=lambda key: (-scores[key], key))
        selected.append(key)
        frontier.remove(key)
        frontier.update(k for k in relations[key] if k in scores and k not in selected)
    selected.extend(k for k in anchors if k not in selected)
    return selected[:LIMIT]


def prepare():
    catalogue = assets()
    ontology = {card["id"]: list(card["links"].values()) for card in catalogue}
    readme = "\n\n".join(card["text"] for card in catalogue)
    # Parse published Markdown, independent of the typed edge list.
    chunks = readme.split("\n\n")
    text_by_id = {chunk.splitlines()[0].removeprefix("### "): chunk for chunk in chunks}
    assert set(text_by_id) == set(ontology)
    md_links = {key: re.findall(r"\]\(#([a-z]+-[a-z]+)\)", text) for key, text in text_by_id.items()}
    assert md_links == ontology

    tasks = {}
    testset = list(questions())
    for question in testset:
        for scope in SCOPES:
            docs = {c["id"]: text_by_id[c["id"]] for c in catalogue
                    if scope == "enterprise" or c["brand"] == question.brand}
            scores = rank(question.text, docs)
            lexical = sorted(docs, key=lambda key: (-scores[key], key))
            choice = {
                "full": list(docs),
                "bm25": lexical[:LIMIT],
                "linked": linked(scores, ontology, lexical),
                "oracle": sorted(question.required, key=lexical.index),
            }
            assert choice["linked"] == linked(scores, md_links, lexical)
            for arm, ids in choice.items():
                material = "\n\n".join(docs[i] for i in ids)
                key = "/".join((question.id, scope, arm))
                tasks[key] = {
                    "scope": scope, "arm": arm, "question": question.id, "kind": question.kind,
                    "ids": ids, "coverage": set(question.required) <= set(ids),
                    "prompt": f"Catalogue:\n\n{material}\n\nQuestion: {question.text}",
                }

    (HERE / "catalogue.md").write_text("# Synthetic asset descriptions\n\n" + readme + "\n")
    dump("ontology.json", {c["id"]: {"domain": c["brand"], "relations": c["links"]} for c in catalogue})
    dump("questions.json", [asdict(q) for q in testset])
    return tasks


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def ask(client, task):
    started = time.monotonic()
    response = client.chat.completions.create(
        model=MODEL, temperature=0, max_tokens=1600,
        extra_body={"thinking": {"type": "disabled"}},
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": task["prompt"]}],
    )
    answer = response.choices[0]
    usage = response.usage
    return {
        "raw": answer.message.content, "finish": answer.finish_reason,
        "model": response.model, "response_id": response.id,
        "input_tokens": usage.prompt_tokens, "output_tokens": usage.completion_tokens,
        "cached_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
        "seconds": round(time.monotonic() - started, 3),
    }


def execute(db, query):
    callbacks = 0

    def budget():
        nonlocal callbacks
        callbacks += 1
        return int(callbacks > 3000)

    db.set_progress_handler(budget, 1000)
    try:
        output = db.execute(query).fetchmany(2)
        if len(output) != 1 or len(output[0]) != 1:
            return {"error": "expected one row and one column"}
        return {"value": output[0][0]}
    except sqlite3.Error as error:
        return {"error": str(error)}
    finally:
        db.set_progress_handler(None, 0)


def grade(answer, question, databases):
    expected = [keys[question] for _, keys, _ in databases]
    try:
        value = json.loads(answer["raw"])
        assert isinstance(value, dict) and set(value) == {"sql"}
        sql = value["sql"]
        assert sql is None or isinstance(sql, str) and sql.strip()
    except (TypeError, ValueError, AssertionError):
        return {"score": "invalid_json", "expected": expected}, None
    if sql is None:
        return {"score": "correct" if all(x is None for x in expected) else "wrong_abstain", "expected": expected}, sql
    execution = [execute(db, sql) for db, _, _ in databases]
    if all(x is None for x in expected):
        score = "wrong_answer_when_missing"
    elif any("error" in result for result in execution):
        score = "sql_error"
    elif all(result["value"] == key for result, key in zip(execution, expected)):
        score = "correct"
    else:
        score = "wrong_value"
    return {"score": score, "expected": expected, "execution": execution}, sql


def local_checks(databases):
    for db, keys, _ in databases:
        assert execute(db, "SELECT COUNT(*) FROM aster_ticket WHERE kind='incident'") == {"value": keys["A01"]}
        assert execute(db, "SELECT COUNT(DISTINCT oid) FROM rowan_wide") == {"value": keys["R02"]}
        assert "error" in execute(db, "DELETE FROM rowan_wide")
    assert all(len({keys[q.id] for _, keys, _ in databases}) > 1 for q in questions() if q.kind != "missing")
    assert grade({"raw": "{}"}, "A08", databases)[0]["score"] == "invalid_json"
    assert grade({"raw": '{"sql":null}'}, "A08", databases)[0]["score"] == "correct"


def summary(results):
    summary = {}
    for scope in SCOPES:
        for arm in ARMS:
            items = [r for r in results.values() if r["scope"] == scope and r["arm"] == arm]
            n = len(items)
            summary[f"{scope}/{arm}"] = {
                "total": n, "correct": sum(x["score"] == "correct" for x in items),
                "full_reference_coverage": sum(x["coverage"] for x in items),
                "scores": dict(Counter(x["score"] for x in items)),
                "by_kind": {kind: {
                    "correct": sum(x["score"] == "correct" and x["kind"] == kind for x in items),
                    "total": sum(x["kind"] == kind for x in items),
                } for kind in sorted({x["kind"] for x in items})},
                "average_input_tokens": round(sum(x["input_tokens"] for x in items) / n, 1) if n else None,
            }
    return summary


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run", "grade"))
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    tasks = prepare()
    dbs = [snapshot(count, seed) for count, seed in SNAPSHOTS]
    local_checks(dbs)
    if args.mode == "prepare":
        print(f"{len(tasks)} model calls planned; fixture and README link equivalence checks passed.")
        print(f"Total table rows per snapshot: {[size for _, _, size in dbs]}")
        return

    rawfile = HERE / "raw.jsonl"
    raw = {r["key"]: r for r in map(json.loads, rawfile.read_text().splitlines())} if rawfile.exists() else {}
    if args.mode == "run":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Set DEEPSEEK_API_KEY to run live requests.")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=95, max_retries=2)
        todo = [job for job in tasks if job not in raw]
        Random(410).shuffle(todo)
        with rawfile.open("a") as file, ThreadPoolExecutor(max_workers=args.workers) as pool:
            jobs = {job: pool.submit(ask, client, tasks[job]) for job in todo}
            reverse = {future: job for job, future in jobs.items()}
            for future in as_completed(reverse):
                job = reverse[future]
                try:
                    result = {"key": job, **future.result()}
                except Exception as error:
                    print(f"{job}: {type(error).__name__} {getattr(error, 'status_code', '')}", flush=True)
                    continue
                file.write(json.dumps(result, ensure_ascii=False) + "\n")
                file.flush()
                raw[job] = result
                if len(raw) % 16 == 0:
                    print(f"Completed {len(raw)}/{len(tasks)}", flush=True)

    results = {}
    for key, task in tasks.items():
        if key not in raw:
            continue
        answer = raw[key]
        assessed, sql = grade(answer, task["question"], dbs)
        results[key] = {k: v for k, v in task.items() if k != "prompt"}
        results[key].update(assessed, sql=sql, input_tokens=answer["input_tokens"])
    overview = summary(results)
    dump("results.json", {
        "request_model": MODEL, "response_models": sorted({v["model"] for v in raw.values()}),
        "snapshot_rows": [{"orders_per_domain": count, "seed": seed, "rows": size}
                          for (count, seed), (_, _, size) in zip(SNAPSHOTS, dbs)],
        "calls": len(results), "planned": len(tasks), "summary": overview, "results": results,
    })
    for key, values in overview.items():
        print(key, values)
    if len(results) != len(tasks):
        raise SystemExit(f"Missing {len(tasks) - len(results)} answers.")


if __name__ == "__main__":
    main()
