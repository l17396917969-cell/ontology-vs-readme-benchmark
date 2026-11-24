"""Frozen task intents and a reference implementation over raw records."""
from dataclasses import dataclass
from collections import Counter

from business_schema import codes, table

@dataclass(frozen=True)
class Case:
    id: str
    text: str
    op: str
    brand: str
    args: dict
    role: str = "analyst"


CASES = [
    Case("01", "How many incidents are recorded in Hazel's service desk?", "incident_count", "Hazel", {}),
    Case("02", "Count Violet's trouble tickets tagged incident.", "incident_count", "Violet", {}),
    Case("03", "How much staff time in minutes went to incident tickets of Briar Gold customers who had a completed sale? Count each ticket once.",
         "incident_minutes", "Briar", {"tier": "Gold"}),
    Case("04", "For Pine Silver clients who placed a posted order, give total incident handling time in minutes.",
         "incident_minutes", "Pine", {"tier": "Silver"}),
    Case("05", "How many distinct sales are visible in the Iris dashboard export?", "dashboard_orders", "Iris", {}),
    Case("06", "Ignore duplicate rows on the Willow sales board. How many unique checkout IDs are there?",
         "dashboard_orders", "Willow", {}),
    Case("07", "How many posted Cedar checkouts contained at least one PAD and were made by a Gold loyalty customer?",
         "posted_item_orders", "Cedar", {"sku": "PAD", "tier": "Gold"}),
    Case("08", "Count Larch posted orders with a CLIP for Silver accounts. One order can contain several.",
         "posted_item_orders", "Larch", {"sku": "CLIP", "tier": "Silver"}),
    Case("09", "What did Quince actually collect in cents across all posted sales, with refunds under the applicable Finance policy?",
         "net_collections", "Quince", {}),
    Case("10", "Give Maple's posted net collections in cents. Respect the rules that applied on each order date.",
         "net_collections", "Maple", {}),
    Case("11", "For Spruce transactions, what are posted collections in cents net of credits according to the policy in force at purchase?",
         "net_collections", "Spruce", {}),
    Case("12", "Add up the cents Nettle collected net on posted checkouts using the historical policy, not its dashboard's forecast.",
         "net_collections", "Nettle", {}),
    Case("13", "By how many cents do Grove's posted net collections exceed Juniper's, after applying each order's Finance policy? Return Grove minus Juniper.",
         "collections_delta", "Grove", {"other_brand": "Juniper"}),
    Case("14", "Subtract Thyme's total posted net collections from Umber's in cents, with the relevant rules at order date.",
         "collections_delta", "Umber", {"other_brand": "Thyme"}),
    Case("15", "What percent of Oak posted orders are from marketplace partners?", "partner_share", "Oak", {}),
    Case("16", "For Yarrow, how much of the posted checkout volume, as a percentage of orders, came from the partner channel?",
         "partner_share", "Yarrow", {}),
    Case("17", "Resolve Rowan incident review R101.", "resolve_review_case", "Rowan", {"case_id": "R101"}, "supervisor"),
    Case("18", "Close Kite review case R101 as resolved, please.", "resolve_review_case", "Kite", {"case_id": "R101"}, "analyst"),
    Case("19", "Set Elm incident review R102 to resolved.", "resolve_review_case", "Elm", {"case_id": "R102"}, "supervisor"),
    Case("20", "Please mark Dahlia workflow case R101 resolved.", "resolve_review_case", "Dahlia", {"case_id": "R101"}, "supervisor"),
]


def reference(db, case):
    def rows(kind, brand=case.brand):
        return db.execute(f"SELECT * FROM {table(brand, kind)}").fetchall()

    op, params = case.op, case.args
    if op == "resolve_review_case":
        case_id = params["case_id"]
        lookup = db.execute("SELECT state, approved FROM review_case WHERE brand=? AND case_id=?",
                            (case.brand, case_id)).fetchone()
        allowed = case.role == "supervisor" and lookup == ("open", 1)
        return {"status": "resolved" if allowed else "denied"}, (
            [[case.brand, case_id, "open", "resolved"]] if allowed else []
        )
    if op == "partner_share":
        return {"status": "missing_relationship"}, []
    if op == "incident_count":
        return {"status": "ok", "value": sum(kind == "incident" for _, _, kind, _ in rows("ticket"))}, []
    if op == "dashboard_orders":
        return {"status": "ok", "value": len({row[0] for row in rows("wide")})}, []

    def reference_net(brand):
        posted, settled = codes(brand)
        credits = Counter()
        for oid, cents, state in rows("credit", brand):
            if state == settled:
                credits[oid] += cents
        return sum(billed - (credits[oid] if day >= "2025-07-01" else 0)
                   for oid, _, day, state, billed in rows("orders", brand) if state == posted)

    if op in {"net_collections", "collections_delta"}:
        value = reference_net(case.brand)
        if op == "collections_delta":
            value -= reference_net(params["other_brand"])
    else:
        tier_accounts = {acct for acct, tier, _ in rows("account") if tier == params["tier"]}
        buyers = {buyer: acct for buyer, acct in rows("bridge") if acct in tier_accounts}
        posted, _ = codes(case.brand)
        order_list = [(oid, buyers[buyer]) for oid, buyer, _, state, _ in rows("orders")
                      if state == posted and buyer in buyers]
        if op == "incident_minutes":
            qualifying = {acct for _, acct in order_list}
            value = sum(minutes for _, acct, kind, minutes in rows("ticket")
                        if kind == "incident" and acct in qualifying)
        elif op == "posted_item_orders":
            eligible = {oid for oid, sku, _ in rows("line") if sku == params["sku"]}
            value = sum(oid in eligible for oid, _ in order_list)
    return {"status": "ok", "value": value}, []
