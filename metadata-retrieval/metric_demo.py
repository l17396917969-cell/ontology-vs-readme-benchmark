"""A local example of a governed metric tool, separate from the model benchmark."""
import json

from fixture import BRANDS, codes, snapshot, table
from follow_up import key_for_brand
from run import HERE, SNAPSHOTS, dump, execute


def metric(db, name, brand, *, region=None, sku=None):
    if name != "posted_net_collections" or brand not in BRANDS:
        return {"status": "unsupported_metric"}
    posted, settled = codes(brand)
    query = f"""
    WITH settled_credit AS (
        SELECT oid, SUM(cents) AS amount
        FROM {table(brand, 'credit')}
        WHERE state = :settled
        GROUP BY oid
    )
    SELECT COALESCE(SUM(
        o.billed - CASE WHEN o.day >= :cutoff THEN COALESCE(c.amount, 0) ELSE 0 END
    ), 0)
    FROM {table(brand, 'orders')} o
    JOIN {table(brand, 'bridge')} b ON b.buyer = o.buyer
    JOIN {table(brand, 'account')} a ON a.acct = b.acct
    LEFT JOIN settled_credit c ON c.oid = o.oid
    WHERE o.state = :posted
      AND (:region IS NULL OR a.region = :region)
      AND (:sku IS NULL OR EXISTS (
          SELECT 1 FROM {table(brand, 'line')} i WHERE i.oid = o.oid AND i.sku = :sku
      ))
    """
    bindings = {"settled": settled, "posted": posted, "cutoff": "2025-07-01", "region": region, "sku": sku}
    return {"status": "ok", "value": db.execute(query, bindings).fetchone()[0]}


def main():
    passed = 0
    example = {}
    raw = json.loads((HERE / "results.json").read_text())["results"]["A08/enterprise/linked"]["sql"]
    for count, seed in SNAPSHOTS:
        db, _, _ = snapshot(count, seed)
        for brand in BRANDS:
            expected = key_for_brand(db, brand)
            plain = metric(db, "posted_net_collections", brand)
            filtered = metric(db, "posted_net_collections", brand, region="West", sku="PEN")
            missing = metric(db, "marketplace_posted_order_share", brand)
            assert plain == {"status": "ok", "value": expected["all_net"]}
            assert filtered == {"status": "ok", "value": expected["policy"]}
            assert missing == {"status": "unsupported_metric"}
            passed += 3
            if (count, seed, brand) == (24, 41, "Aster"):
                example = {
                    "brand": brand, "model_generated_sql": raw,
                    "model_sql_execution": execute(db, raw),
                    "registered_net_collections": plain,
                    "unregistered_marketplace_share": missing,
                }
    assert example["model_sql_execution"] == {"value": 0.0}
    dump("metric-demo.json", {
        "supported_metric_checks": passed * 2 // 3, "unsupported_checks": passed // 3,
        "example": example,
    })
    print(json.dumps(example, indent=2))
    print(f"{passed}/{passed} deterministic checks passed.")


if __name__ == "__main__":
    main()
