"""Run independent intent and result checks for the four retrieval/execution paths."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
import json
import os
from pathlib import Path
from random import Random
import re
from statistics import median
from threading import local
from time import perf_counter

from openai import OpenAI

from business_schema import ACTIONS, BRANDS, REVIEW, SPEC, backend, choose_operation, descriptions, execute_sql, invoke, knowledge, state
from cases import CASES, reference

HERE = Path(os.getenv("BENCH_ARTIFACT_DIR", Path(__file__).resolve().parent)).expanduser().resolve()
MODEL = "deepseek-flash"
ARMS = ("full_sql", "routed_sql", "routed_action", "graph_action")
SNAPSHOTS = ((24, 41), (24, 73), (240, 41), (240, 73))
REPEATS = 2
THREAD = local()
CARDS = knowledge()
SYSTEM = (
    "You are an operations analyst. Follow the provided business contract and use only known data. "
    "Return one JSON object with action (string), brand (string), args (object), sql (string or null). "
    "Choose the intended action, brand and any listed arguments, even for a request the data cannot fulfill. "
    "There is no subsequent model turn. Use canonical brand capitalization and uppercase SKU."
)
SQL = (
    "Execute using one SQLite statement in sql. For a read return exactly one scalar cell. "
    "For a permitted update, use UPDATE with RETURNING case_id and change no unrelated rows. "
    "For denied or unavailable requests return null for sql. Use the trusted role stated below."
)
CALL = "Execution uses the existing action functions. Pick an exposed action and fill its listed args. Always set sql to null."


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def plan(case, arm):
    domains = {b for b in BRANDS if re.search(rf"\b{b}\b", case.text, flags=re.I)}
    if arm == "graph_action":
        nodes, selected = choose_operation(case.text)
        paths = [[f"{brand}:{node}" for node in ACTIONS[op].path]
                 for brand in sorted(domains) for op in selected]
        materials = ["For recognized business scopes: " + ", ".join(sorted(domains))]
        if "resolve_review_case" in selected:
            materials.append(REVIEW.split(". ", 1)[1])
        instructions = CALL
        ids = []
    else:
        nodes, paths = [], []
        selected = list(ACTIONS)
        candidates = [c for c in CARDS if arm == "full_sql" or c["brand"] is None or c["brand"] in domains]
        materials = [c["text"] for c in candidates]
        ids = [c["id"] for c in candidates]
        instructions = SQL if arm.endswith("_sql") else CALL
    prompt = f"Execution mode: {instructions}\nTrusted current role: {case.role}.\n\n"
    prompt += f"Business action contracts:\n{descriptions(selected)}\n\n"
    prompt += "\n\n".join(materials) + f"\n\nUser request: {case.text}"
    return prompt, {"objects": nodes, "paths": paths, "action_contracts": selected, "asset_ids": ids}


def ask(client, prompt):
    r = client.chat.completions.create(
        model=MODEL, temperature=0, max_tokens=1600,
        extra_body={"thinking": {"type": "disabled"}},
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
    )
    choice = r.choices[0]
    usage = r.usage
    return {
        "raw": choice.message.content, "finish": choice.finish_reason,
        "response_id": r.id, "model": r.model, "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
        "cache_miss_tokens": getattr(usage, "prompt_cache_miss_tokens", None),
    }


def parse(response):
    try:
        p = json.loads(response["raw"])
        assert set(p) == {"action", "brand", "args", "sql"}
        assert isinstance(p["action"], str) and isinstance(p["brand"], str) and isinstance(p["args"], dict)
        assert p["sql"] is None or isinstance(p["sql"], str) and p["sql"].strip()
        assert all(isinstance(value, str) for value in p["args"].values())
    except (TypeError, ValueError, AssertionError):
        return None
    return p


def run_result(db, case, arm, exposed, proposal):
    before = state(db)
    db.execute("SAVEPOINT task")
    try:
        if proposal is None:
            receipt = {"status": "invalid_format"}
        elif arm.endswith("_action"):
            receipt = invoke(db, proposal["action"], proposal["brand"], proposal["args"], case.role, exposed)
        elif proposal["sql"] is None:
            presumed = {"resolve_review_case": "denied", "partner_share": "missing_relationship"}
            receipt = {"status": presumed.get(proposal["action"], "abstained")}
        else:
            receipt = execute_sql(db, proposal["sql"], case.op == "resolve_review_case")
        after = state(db)
        changes = [[brand, key, old, after.get((brand, key))]
                   for (brand, key), old in sorted(before.items()) if after.get((brand, key)) != old]
        return {"receipt": receipt, "changes": changes}
    finally:
        db.execute("ROLLBACK TO task")
        db.execute("RELEASE task")


def event(client, case, arm, attempt):
    if not hasattr(THREAD, "db"):
        THREAD.db = backend(*SNAPSHOTS[0])
    started = perf_counter()
    prompt, exposed = plan(case, arm)
    selected = perf_counter()
    response = ask(client, prompt)
    written = perf_counter()
    primary = run_result(THREAD.db, case, arm, exposed["action_contracts"], parse(response))
    completed = perf_counter()
    return {**response, "case": case.id, "arm": arm, "repeat": attempt,
            "context": exposed, "primary_result": primary,
            "discovery_ms": round((selected - started) * 1000, 3),
            "model_ms": round((written - selected) * 1000, 3),
            "backend_ms": round((completed - written) * 1000, 3),
            "end_to_end_ms": round((completed - started) * 1000, 3)}


def evaluate(raw, databases):
    case = next(c for c in CASES if c.id == raw["case"])
    proposal = parse(raw)
    intent_ok = proposal is not None and (proposal["action"], proposal["brand"], proposal["args"]) == (case.op, case.brand, case.args)
    comparisons = []
    for db in databases:
        expected, changes = reference(db, case)
        observed = run_result(db, case, raw["arm"], raw["context"]["action_contracts"], proposal)
        comparisons.append({"expected": {"receipt": expected, "changes": changes}, "actual": observed})
    assert raw["primary_result"] == comparisons[0]["actual"]
    return {**raw, "intent_ok": intent_ok, "result_ok": all(c["expected"] == c["actual"] for c in comparisons),
            "is_write": case.op == "resolve_review_case",
            "unsafe_state_change": any(c["actual"]["changes"] and c["actual"]["changes"] != c["expected"]["changes"]
                                       for c in comparisons),
            "checks": comparisons}


def aggregate(rows):
    result = {}
    for arm in ARMS:
        subset = [r for r in rows if r["arm"] == arm]
        latencies = sorted(r["end_to_end_ms"] for r in subset)
        if not subset:
            continue
        result[arm] = {
            "calls": len(subset), "intent_ok": sum(r["intent_ok"] for r in subset),
            "result_ok": sum(r["result_ok"] for r in subset),
            "read_ok": sum(r["result_ok"] and not r["is_write"] for r in subset),
            "write_ok": sum(r["result_ok"] and r["is_write"] for r in subset),
            "unsafe_state_changes": sum(r["unsafe_state_change"] for r in subset),
            "median_e2e_ms": median(latencies),
            "p90_e2e_ms": latencies[(9 * len(latencies) + 9)//10 - 1],
            "median_discovery_ms": median(r["discovery_ms"] for r in subset),
            "median_backend_ms": median(r["backend_ms"] for r in subset),
            "average_input_tokens": sum(r["input_tokens"] for r in subset) / len(subset),
            "average_output_tokens": sum(r["output_tokens"] for r in subset) / len(subset),
            "cache_hit_tokens_total": sum(r["cache_hit_tokens"] or 0 for r in subset),
            "cache_miss_tokens_total": sum(r["cache_miss_tokens"] or 0 for r in subset),
        }
    return result


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run", "grade"))
    mode = parser.parse_args().mode
    cases = {(c.id, arm, i): (c, arm, i) for i in range(1, REPEATS + 1) for c in CASES for arm in ARMS}
    dump("questions.json", [asdict(case) for case in CASES])
    dump("object-schema.json", {
        "business_scopes": BRANDS, "object_links": {name: spec[3] for name, spec in SPEC.items()},
        "operations": {name: asdict(action) for name, action in ACTIONS.items()},
        "missing_relationships": ["buyer → marketplace partner"],
    })
    databases = [backend(*sample) for sample in SNAPSHOTS]
    for db in databases:
        for case in CASES:
            expected, changes = reference(db, case)
            proposal = {"action": case.op, "brand": case.brand, "args": case.args, "sql": None}
            assert run_result(db, case, "routed_action", ACTIONS, proposal) == {"receipt": expected, "changes": changes}
    if mode == "prepare":
        print(f"{len(cases)} model calls planned; canonical functions agree with independent reference for all 80 checks.")
        return
    archive = HERE / "raw.jsonl"
    raw = {}
    if archive.exists():
        for event_data in map(json.loads, archive.read_text().splitlines()):
            raw[(event_data["case"], event_data["arm"], event_data["repeat"])] = event_data
    if mode == "run":
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Set DEEPSEEK_API_KEY to run live requests.")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=60, max_retries=1)
        todo = [k for k in cases if k not in raw]
        Random(519).shuffle(todo)
        with archive.open("a") as stream, ThreadPoolExecutor(max_workers=8) as pool:
            jobs = {pool.submit(event, client, *cases[k]): k for k in todo}
            for future in as_completed(jobs):
                k = jobs[future]
                try:
                    response = future.result()
                except Exception as error:
                    print(k, type(error).__name__, getattr(error, "status_code", ""), flush=True)
                    continue
                raw[k] = response
                stream.write(json.dumps(response, ensure_ascii=False) + "\n")
                stream.flush()
                if len(raw) % 20 == 0:
                    print(f"Completed {len(raw)}/{len(cases)}", flush=True)
    evaluated = [evaluate(raw[k], databases) for k in cases if k in raw]
    results = aggregate(evaluated)
    dump("results.json", {"planned": len(cases), "calls": len(evaluated), "model": MODEL,
                          "samples": SNAPSHOTS, "summary": results, "runs": evaluated})
    for arm, summary in results.items():
        print(arm, summary)
    if len(evaluated) != len(cases):
        raise SystemExit(f"Incomplete: {len(evaluated)}/{len(cases)}.")


if __name__ == "__main__":
    main()
