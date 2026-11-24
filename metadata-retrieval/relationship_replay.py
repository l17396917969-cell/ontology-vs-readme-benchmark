"""Replay A08 and calculate two possible outcomes using the same observed records."""
import hashlib
import json

from fixture import codes, snapshot
from run import HERE, dump, execute

QUERY = """
WITH partner_buyers(buyer, partner_id) AS (SELECT ?, ? WHERE ?)
SELECT COUNT(*) AS posted_orders,
       COUNT(*) FILTER (WHERE p.partner_id IS NOT NULL) AS partner_orders
FROM aster_orders AS o
LEFT JOIN partner_buyers AS x ON x.buyer = o.buyer
LEFT JOIN aster_partner AS p ON p.partner_id = x.partner_id
WHERE o.state = ?
"""


def main():
    results = json.loads((HERE / "results.json").read_text())["results"]
    linked = results["A08/enterprise/linked"]
    full = results["A08/enterprise/full"]
    db, _, _ = snapshot(24, 41)
    posted, _ = codes("Aster")
    sources = {}
    for table in ("orders", "bridge", "account", "partner"):
        sources[table] = db.execute(f"SELECT * FROM aster_{table} ORDER BY 1").fetchall()
    buyer = "B5"
    partner = "P0"
    assert any(row[0] == partner for row in sources["partner"])
    assert any(row[0] == buyer for row in sources["bridge"])
    worlds = []
    for known_link in (False, True):
        all_orders, matched = db.execute(QUERY, (buyer, partner, known_link, posted)).fetchone()
        worlds.append({
            "hypothetical_complete_mapping": [[buyer, partner]] if known_link else [],
            "posted_orders": all_orders,
            "partner_orders": matched,
            "percentage": 100 * matched / all_orders,
        })
    assert [item["posted_orders"] for item in worlds] == [16, 16]
    assert [item["partner_orders"] for item in worlds] == [0, 3]
    model_output = execute(db, linked["sql"])
    assert model_output == {"value": 0.0}
    assert full["sql"] is None and full["score"] == "correct"
    card = (HERE / "catalogue.md").read_text().split("### aster-partner\n", 1)[1].split("\n\n", 1)[0]
    dump("relationship-replay.json", {
        "case": "A08",
        "dataset": {"orders_per_domain": 24, "seed": 41},
        "observed_records_sha256": hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest(),
        "observed_records_note": "Both hypothetical outcomes use the same visible synthetic records.",
        "catalogue_declaration": card,
        "model_evidence_ids": linked["ids"],
        "model_generated_sql": linked["sql"],
        "replayed_model_output": model_output,
        "full_readme_model_output": {"sql": full["sql"]},
        "hypothetical_outcomes": worlds,
    })
    print(f"Archived relation-retrieval SQL: {model_output['value']:.1f}%")
    for world in worlds:
        print(f"Complete mapping {world['hypothetical_complete_mapping']}: "
              f"{world['partner_orders']}/{world['posted_orders']} = {world['percentage']:.2f}%")


if __name__ == "__main__":
    main()
