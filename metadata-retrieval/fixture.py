"""Synthetic catalogue, frozen questions and independent Python answer key."""
from dataclasses import dataclass
from random import Random
import sqlite3

BRANDS = (
    "Aster", "Briar", "Cedar", "Dahlia", "Elm", "Fennel", "Grove", "Hazel",
    "Iris", "Juniper", "Kite", "Larch", "Maple", "Nettle", "Oak", "Pine",
    "Quince", "Rowan", "Spruce", "Thyme", "Umber", "Violet", "Willow", "Yarrow",
)
SPEC = {
    "account": ("Account", "account(acct TEXT, tier TEXT, region TEXT)",
                "CRM customer master. One row per acct. Loyalty tier and territory come from tier and region.",
                {"maps_buyer": "bridge", "opens_cases": "ticket"}),
    "bridge": ("Buyer identity bridge", "bridge(buyer TEXT, acct TEXT)",
               "Identity map. One row per commerce buyer. Multiple buyer aliases may map to the same CRM acct. Use buyer to match checkout feeds and acct to match CRM records.",
               {"resolves_account": "account", "links_checkout": "orders"}),
    "orders": ("Sales order", "orders(oid INTEGER, buyer TEXT, day TEXT, state TEXT, billed INTEGER)",
               "Transactional checkout header. One row per oid. day is YYYY-MM-DD. billed is the gross order amount in cents. Posted checkout uses state='{posted}'. Join lines, credits and the dashboard on oid.",
               {"resolves_buyer": "bridge", "contains_items": "line", "settles_with": "credit"}),
    "line": ("Order line", "line(oid INTEGER, sku TEXT, units INTEGER)",
             "Warehouse checkout items. An oid has many rows and an SKU can occur on several rows per order. Sum units for quantities. SKU membership at order grain uses an existence test.",
             {"belongs_to_order": "orders"}),
    "credit": ("Refund / credit event", "credit(oid INTEGER, cents INTEGER, state TEXT)",
               "Payment connector. Several credits may exist for an order. Settled fund movements use state='{settled}'. Aggregate matching credits per order before joining to line or dashboard data.",
               {"credits_order": "orders", "policy_defined_by": "policy"}),
    "policy": ("Finance policy memo", None,
               "Finance manual, ratified v2 for orders on or after 2025-07-01. Posted net collections use billed less the sum of settled credits, with missing credits taken as zero. The older v1 memo remains effective for orders before 2025-07-01. For those orders net collections use billed without credit offsets. Always apply the policy by checkout header day, not analysis date. Account segments still come from CRM.",
               {"uses_payment": "credit", "uses_orders": "orders"}),
    "wide": ("Sales analytics dashboard export", "wide(oid INTEGER, sku TEXT, billed INTEGER, net_snapshot INTEGER)",
             "One row per dashboard item observation. Reprocessed items may repeat. billed repeats the order header at item grain. net_snapshot is a forecasting field from an earlier policy, for dashboard use only. Use oid for unique checkout count.",
             {"sourced_from": "orders", "item_source": "line"}),
    "ticket": ("Support ticket", "ticket(caseid INTEGER, acct TEXT, kind TEXT, minutes INTEGER)",
               "Service desk. One row per caseid. Kind is setup or incident. minutes is total handling time. Match acct to the CRM customer master; case counts are separate from order and line counts.",
               {"filed_by": "account"}),
    "partner": ("Marketplace partner", "partner(partner_id TEXT, segment TEXT)",
                "Alliance registry. One row per partner_id. No buyer, account or order mapping exists in this catalogue.",
                {}),
}


def codes(brand):
    index = BRANDS.index(brand)
    return f"ok{index % 4}", f"settled{index % 5}"


def table(brand, kind):
    return f"{brand.lower()}_{kind}"


def card_id(brand, kind):
    return f"{brand.lower()}-{kind}"


def assets():
    cards = []
    for brand in BRANDS:
        for kind, (title, schema, description, links) in SPEC.items():
            posted, settled = codes(brand)
            asset_id = card_id(brand, kind)
            source = f"SQLite schema: {brand.lower()}_{schema}." if schema else "Document from Finance."
            targets = {relation: card_id(brand, dest) for relation, dest in links.items()}
            link_text = ", ".join(f"{relation.replace('_', ' ')} [{dest}](#{dest})"
                                  for relation, dest in targets.items())
            body = f"### {asset_id}\n{brand} {title}. {source} {description.format(posted=posted, settled=settled)}"
            if link_text:
                body += f"\nRelated assets: {link_text}."
            cards.append({"id": asset_id, "brand": brand, "text": body, "links": targets})
    Random(938).shuffle(cards)
    return cards


@dataclass(frozen=True)
class Question:
    id: str
    brand: str
    kind: str
    text: str
    required: list


def questions():
    templates = [
        ("single", "How many {brand} support tickets are kind incident?", ("ticket",)),
        ("single", "How many unique {brand} checkout orders appear in the sales analytics dashboard export?", ("wide",)),
        ("cross", "How many posted {brand} orders have at least one BAG item and belong to a Gold loyalty account?", ("account", "bridge", "orders", "line")),
        ("cross", "How many distinct {brand} CRM accounts in the West territory bought a PEN on a posted checkout?", ("account", "bridge", "orders", "line")),
        ("cross", "Total incident handling time in minutes for {brand} accounts that made at least one posted order. Count each incident once.", ("account", "bridge", "orders", "ticket")),
        ("policy", "What are {brand}'s total posted net collections in cents across all order dates under the effective Finance policy?", ("orders", "credit", "policy")),
        ("policy", "For Gold {brand} loyalty accounts, give posted net collections in cents with the correct historical Finance policy, on orders containing at least one BAG. Count each order once.", ("account", "bridge", "orders", "line", "credit", "policy")),
        ("missing", "What percentage of {brand} posted orders were placed by Marketplace partners?", ("partner", "orders", "bridge")),
    ]
    for brand in ("Aster", "Rowan"):
        for index, (kind, text, needed) in enumerate(templates, 1):
            yield Question(f"{brand[0]}{index:02}", brand, kind, text.format(brand=brand),
                           [card_id(brand, k) for k in needed])


def snapshot(orders_per_brand, seed):
    rng = Random(seed)
    db = sqlite3.connect(":memory:")
    keys = {}
    total_rows = 0
    for brand in BRANDS:
        posted, settled = codes(brand)
        rows = {kind: [] for kind, spec in SPEC.items() if spec[1]}
        accounts = {f"A{i}": (rng.choice(("Gold", "Silver")), rng.choice(("West", "East")))
                    for i in range(12)}
        rows["account"] = [(acct, *attrs) for acct, attrs in accounts.items()]
        buyer_accounts = {f"B{i}": f"A{i % len(accounts)}" for i in range(24)}
        rows["bridge"] = list(buyer_accounts.items())
        rows["ticket"] = [(i, rng.choice(tuple(accounts)), rng.choice(("incident", "setup")), rng.randint(5, 180))
                          for i in range(45)]
        rows["partner"] = [(f"P{i}", rng.choice(("direct", "reseller"))) for i in range(7)]
        bought_by = set()
        pen_west = set()
        gold_bags = 0
        posted_net = 0
        posted_net_gold_bags = 0
        dashboard_orders = set()
        for oid in range(1, orders_per_brand + 1):
            buyer = rng.choice(tuple(buyer_accounts))
            account = buyer_accounts[buyer]
            tier, region = accounts[account]
            day = rng.choice(("2025-02-09", "2025-06-30", "2025-07-01", "2025-10-14"))
            state = rng.choice((posted, posted, posted, "pending", "cancelled"))
            cents = rng.randint(300, 18000)
            rows["orders"].append((oid, buyer, day, state, cents))
            items = [rng.choice(("BAG", "PEN", "CLIP", "PAD")) for _ in range(rng.randint(1, 5))]
            for sku in items:
                rows["line"].append((oid, sku, rng.randint(1, 8)))
                if oid % 9:
                    row = (oid, sku, cents, cents - rng.randint(0, 250))
                    rows["wide"].extend([row] * rng.randint(1, 2))
                    dashboard_orders.add(oid)
            settled_cents = 0
            for _ in range(rng.randrange(4)):
                credit_amount = rng.randint(3, 280)
                credit_status = rng.choice((settled, settled, "requested", "void"))
                rows["credit"].append((oid, credit_amount, credit_status))
                if credit_status == settled:
                    settled_cents += credit_amount
            if state != posted:
                continue
            bought_by.add(account)
            if region == "West" and "PEN" in items:
                pen_west.add(account)
            net = cents - settled_cents if day >= "2025-07-01" else cents
            posted_net += net
            if tier == "Gold" and "BAG" in items:
                gold_bags += 1
                posted_net_gold_bags += net
        values = [
            sum(kind == "incident" for _, _, kind, _ in rows["ticket"]),
            len(dashboard_orders),
            gold_bags,
            len(pen_west),
            sum(minutes for _, acct, kind, minutes in rows["ticket"] if kind == "incident" and acct in bought_by),
            posted_net,
            posted_net_gold_bags,
            None,
        ]
        keys.update({f"{brand[0]}{i:02}": value for i, value in enumerate(values, 1)})
        for kind, data in rows.items():
            schema = SPEC[kind][1]
            db.execute(f"CREATE TABLE {brand.lower()}_{schema}")
            db.executemany(f"INSERT INTO {table(brand, kind)} VALUES ({','.join('?' for _ in data[0])})", data)
            total_rows += len(data)
    db.commit()
    db.execute("PRAGMA query_only=ON")
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}
    db.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
    return db, keys, total_rows
