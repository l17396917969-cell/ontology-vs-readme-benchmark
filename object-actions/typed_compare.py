"""Paired doc/graph replay with the same native strict function-call interface."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from random import Random
import re
from time import perf_counter

from openai import OpenAI

from business_schema import ACTIONS, BRANDS, backend
from compare import CASES, HERE, MODEL, REPEATS, SNAPSHOTS, THREAD, aggregate, dump, evaluate, plan, run_result

ARMS = ("routed_action", "graph_action")


def exposed_tools(names):
    parameters = {
        "brand": {"type": "string", "enum": list(BRANDS), "description": "Primary business scope."},
        "other_brand": {"type": "string", "enum": list(BRANDS), "description": "Other scope to subtract."},
        "tier": {"type": "string", "enum": ["Gold", "Silver"]},
        "sku": {"type": "string", "enum": ["BAG", "PEN", "CLIP", "PAD"]},
        "case_id": {"type": "string", "pattern": "^R[0-9]+$"},
    }
    return [{
        "type": "function",
        "function": {
            "name": name, "description": ACTIONS[name].description, "strict": True,
            "parameters": {
                "type": "object", "additionalProperties": False,
                "properties": {key: parameters[key] for key in ("brand", *ACTIONS[name].args)},
                "required": ["brand", *ACTIONS[name].args],
            },
        },
    } for name in names]


def event(client, case, arm, retry):
    if not hasattr(THREAD, "db"):
        THREAD.db = backend(*SNAPSHOTS[0])
    start = perf_counter()
    prompt, context = plan(case, arm)
    # Keep discovery and evidence. Replace the old duplicated textual signature with native tools.
    lines = re.split(r"\n\n", prompt, maxsplit=2)
    user = f"Trusted current role: {case.role}.\n\n" + lines[2]
    tools = exposed_tools(context["action_contracts"])
    selected = perf_counter()
    r = client.chat.completions.create(
        model=MODEL, max_tokens=1600, temperature=0,
        extra_body={"thinking": {"type": "disabled"}}, tools=tools, tool_choice="auto",
        messages=[
            {"role": "system", "content": "Interpret the operation request and call exactly one appropriate listed tool. "
                                             "Even if policy may deny execution or source data may be missing, call the "
                                             "appropriate tool so the backend can return a factual status. Do not write SQL."},
            {"role": "user", "content": user},
        ],
    )
    answer = r.choices[0]
    message = answer.message
    calls = message.tool_calls or []
    proposal = None
    if len(calls) == 1 and calls[0].type == "function":
        name = calls[0].function.name
        args = json.loads(calls[0].function.arguments)
        brand = args.pop("brand", "")
        proposal = {"action": name, "brand": brand, "args": args, "sql": None}
    returned = perf_counter()
    primary = run_result(THREAD.db, case, arm, context["action_contracts"], proposal)
    end = perf_counter()
    usage = r.usage
    return {
        "case": case.id, "arm": arm, "repeat": retry, "raw": json.dumps(proposal),
        "tool_calls": [c.model_dump() for c in calls], "content": message.content,
        "finish": answer.finish_reason, "response_id": r.id, "model": r.model,
        "input_tokens": usage.prompt_tokens, "output_tokens": usage.completion_tokens,
        "cache_hit_tokens": getattr(usage, "prompt_cache_hit_tokens", None),
        "cache_miss_tokens": getattr(usage, "prompt_cache_miss_tokens", None),
        "context": context, "primary_result": primary,
        "discovery_ms": round((selected - start)*1000, 3), "model_ms": round((returned - selected)*1000, 3),
        "backend_ms": round((end - returned)*1000, 3), "end_to_end_ms": round((end - start)*1000, 3),
    }


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Call the model for missing responses")
    run_live = parser.parse_args().run
    tasks = {(c.id, arm, trial): (c, arm, trial) for c in CASES for arm in ARMS for trial in range(1, REPEATS + 1)}
    path = HERE / "typed-raw.jsonl"
    raw = {(e["case"],e["arm"],e["repeat"]): e for e in map(json.loads, path.read_text().splitlines())} if path.exists() else {}
    todo = [key for key in tasks if key not in raw]
    Random(711).shuffle(todo)
    if todo and run_live:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Set DEEPSEEK_API_KEY to run live requests.")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com/beta", timeout=60, max_retries=1)
        # Run one request before queueing the remaining paid calls to validate the API schema.
        first = todo.pop(0)
        with path.open("a") as file:
            raw[first] = event(client, *tasks[first])
            file.write(json.dumps(raw[first], ensure_ascii=False) + "\n")
            file.flush()
            with ThreadPoolExecutor(max_workers=8) as pool:
                jobs = {pool.submit(event, client, *tasks[key]): key for key in todo}
                for future in as_completed(jobs):
                    key = jobs[future]
                    try:
                        result = future.result()
                    except Exception as error:
                        print(key, type(error).__name__, getattr(error, "status_code", ""), flush=True)
                        continue
                    raw[key] = result
                    file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    file.flush()
                    if len(raw) % 20 == 0:
                        print(f"Completed {len(raw)}/{len(tasks)}", flush=True)
    databases = [backend(*s) for s in SNAPSHOTS]
    evaluated = [evaluate(raw[key], databases) for key in tasks if key in raw]
    results = aggregate(evaluated)
    dump("typed-results.json", {"planned": len(tasks), "calls": len(evaluated), "model": MODEL,
                                "samples": SNAPSHOTS, "summary": results, "runs": evaluated})
    for arm, result in results.items():
        print(arm, result)
    if len(evaluated) != len(tasks):
        raise SystemExit(f"Incomplete: {len(evaluated)}/{len(tasks)}.")


if __name__ == "__main__":
    main()
