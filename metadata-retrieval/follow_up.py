"""Evaluate new question forms and a domain-routed README at enterprise scope."""
from collections import Counter
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from random import Random
import re

from openai import OpenAI

from fixture import assets, card_id, codes, table
from run import HERE, MODEL, LIMIT, SNAPSHOTS, ask, dump, grade, linked, rank, snapshot

BRANDS = ("Cedar", "Fennel", "Larch", "Pine", "Violet", "Willow")
ARMS = ("full", "bm25", "linked", "routed", "oracle6")


def questions():
    for index, brand in enumerate(BRANDS):
        peer = BRANDS[(index + 1) % len(BRANDS)]
        yield brand[:1] + "11", "support", (brand,), (
            f"How many staff minutes went to incident cases for {brand} Gold customers "
            "who had at least one completed checkout? Count a case once."
        ), {card_id(brand, k) for k in ("account", "bridge", "orders", "ticket")}
        yield brand[:1] + "12", "policy", (brand,), (
            f"Under the Finance memo that applied on each checkout date, how many cents did "
            f"{brand} collect net on posted checkouts that came from West CRM accounts and included a PEN?"
        ), {card_id(brand, k) for k in ("account", "bridge", "orders", "line", "credit", "policy")}
        yield brand[:1] + "13", "two_domain", (brand, peer), (
            f"Subtract {peer}'s total posted net collections from {brand}'s total posted net collections in cents. "
            "Use the applicable policy at the time of each checkout; a negative difference is valid."
        ), {card_id(b, k) for b in (brand, peer) for k in ("orders", "credit", "policy")}
        yield brand[:1] + "14", "missing", (brand,), (
            f"How many distinct {brand} Marketplace resellers placed a posted checkout? "
            "Use the reseller classification from its marketplace registry."
        ), {card_id(brand, k) for k in ("partner", "orders", "bridge")}


def key_for_brand(db, brand):
    def rows(kind):
        return db.execute(f"SELECT * FROM {table(brand, kind)}").fetchall()

    accounts = {acct: (tier, region) for acct, tier, region in rows("account")}
    bridge = dict(rows("bridge"))
    pen_orders = {oid for oid, sku, _ in rows("line") if sku == "PEN"}
    posted, settled = codes(brand)
    refunds = Counter()
    for oid, cents, state in rows("credit"):
        if state == settled:
            refunds[oid] += cents
    west_pen_net = 0
    all_net = 0
    gold_buyers = set()
    for oid, buyer, day, state, billed in rows("orders"):
        if state != posted:
            continue
        acct = bridge[buyer]
        tier, region = accounts[acct]
        net = billed - (refunds[oid] if day >= "2025-07-01" else 0)
        all_net += net
        if tier == "Gold":
            gold_buyers.add(acct)
        if region == "West" and oid in pen_orders:
            west_pen_net += net
    incident_time = sum(minutes for _, acct, kind, minutes in rows("ticket")
                        if kind == "incident" and acct in gold_buyers)
    return {
        "support": incident_time, "policy": west_pen_net, "all_net": all_net, "missing": None,
    }


def build():
    catalogue = assets()
    docs = {card["id"]: card["text"] for card in catalogue}
    ontology = {card["id"]: list(card["links"].values()) for card in catalogue}
    tasks = {}
    testset = list(questions())
    dump("follow-up-questions.json", [{"id": q, "kind": kind, "domains": domains, "text": question,
                                     "required": sorted(required)}
                                    for q, kind, domains, question, required in testset])
    for q, kind, domains, question, required in testset:
        scores = rank(question, docs)
        lexical = sorted(docs, key=lambda key: (-scores[key], key))
        names = {card["brand"] for card in catalogue}
        routed_domains = {name for name in names if re.search(rf"\b{re.escape(name)}\b", question, flags=re.I)}
        assert routed_domains == set(domains)
        required_first = [key for key in lexical if key in required]
        assert len(required_first) <= LIMIT
        reference = required_first + [key for key in lexical if key not in required]
        choices = {
            "full": list(docs), "bm25": lexical[:LIMIT], "linked": linked(scores, ontology, lexical),
            "routed": [card["id"] for card in catalogue if card["brand"] in routed_domains],
            "oracle6": reference[:LIMIT],
        }
        for arm, ids in choices.items():
            material = "\n\n".join(docs[i] for i in ids)
            tasks[q + "/" + arm] = {
                "arm": arm, "kind": kind, "question": q, "ids": ids,
                "coverage": required <= set(ids), "prompt": f"Catalogue:\n\n{material}\n\nQuestion: {question}",
            }
    return testset, tasks


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Call the model for missing responses")
    run_live = parser.parse_args().run
    testset, tasks = build()
    databases = []
    for count, seed in SNAPSHOTS:
        db, _, size = snapshot(count, seed)
        numbers = {brand: key_for_brand(db, brand) for brand in BRANDS}
        keys = {}
        for q, kind, domains, _, _ in testset:
            if kind == "two_domain":
                keys[q] = numbers[domains[0]]["all_net"] - numbers[domains[1]]["all_net"]
            else:
                keys[q] = numbers[domains[0]][kind]
        databases.append((db, keys, size))
    assert all(len({keys[q] for _, keys, _ in databases}) > 1 for q, kind, *_ in testset if kind != "missing")
    rawfile = HERE / "follow-up-raw.jsonl"
    raw = {r["key"]: r for r in map(json.loads, rawfile.read_text().splitlines())} if rawfile.exists() else {}
    todo = [key for key in tasks if key not in raw]
    Random(712).shuffle(todo)
    if todo and run_live:
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise SystemExit("Set DEEPSEEK_API_KEY to run live requests.")
        client = OpenAI(api_key=key, base_url="https://api.deepseek.com", timeout=95, max_retries=2)
        with rawfile.open("a") as file, ThreadPoolExecutor(max_workers=16) as pool:
            jobs = {pool.submit(ask, client, tasks[job]): job for job in todo}
            for future in as_completed(jobs):
                job = jobs[future]
                try:
                    result = {"key": job, **future.result()}
                except Exception as error:
                    print(f"{job}: {type(error).__name__} {getattr(error, 'status_code', '')}", flush=True)
                    continue
                file.write(json.dumps(result, ensure_ascii=False) + "\n")
                file.flush()
                raw[job] = result
                if len(raw) % 24 == 0:
                    print(f"Completed {len(raw)}/{len(tasks)}", flush=True)

    results = {}
    for key, task in tasks.items():
        if key not in raw:
            continue
        assessed, sql = grade(raw[key], task["question"], databases)
        results[key] = {k: v for k, v in task.items() if k != "prompt"}
        results[key].update(assessed, sql=sql, input_tokens=raw[key]["input_tokens"])
    report = {}
    for arm in ARMS:
        items = [r for r in results.values() if r["arm"] == arm]
        report[arm] = {
            "correct": sum(x["score"] == "correct" for x in items),
            "total": len(items),
            "coverage": sum(x["coverage"] for x in items),
            "average_input_tokens": round(sum(x["input_tokens"] for x in items) / len(items), 1) if items else None,
            "by_kind": {kind: dict(Counter(x["score"] for x in items if x["kind"] == kind))
                        for kind in sorted({x["kind"] for x in items})},
        }
    dump("follow-up-results.json", {
        "request_model": MODEL, "response_models": sorted({v["model"] for v in raw.values()}),
        "calls": len(results), "planned": len(tasks), "summary": report, "results": results,
    })
    for arm, score in report.items():
        print(arm, score)
    if len(results) != len(tasks):
        raise SystemExit(f"Missing {len(tasks) - len(results)} answers.")


if __name__ == "__main__":
    main()
