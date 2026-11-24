"""Shared synthetic object catalogue, action contracts and execution backend."""
from dataclasses import dataclass
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "metadata-retrieval"))
from fixture import BRANDS, SPEC, assets, codes, snapshot, table

OBJECTS = {
    "ticket": ("support ticket incident case helpdesk handling staff minutes outage trouble"),
    "account": ("account crm client customer member loyalty tier gold silver territory region"),
    "bridge": ("buyer customer identity alias match account crosswalk"),
    "orders": ("order posted completed sale checkout purchase purchases transactions traded"),
    "line": ("sku product item bag pen clip pad basket bought units"),
    "credit": ("refund chargeback credit payment settlement reimbursement deduction"),
    "policy": ("policy finance memo rules effective historical period cutoff net"),
    "wide": ("dashboard wide export analytics report unique observed duplicate checkout"),
    "partner": ("marketplace channel partner reseller alliance share percentage"),
    "case_review": ("resolve close triage review incident workflow case fix status"),
}

@dataclass(frozen=True)
class Action:
    description: str
    args: tuple
    path: tuple


ACTIONS = {
    "incident_count": Action("Count incident tickets in the service desk.", (), ("ticket",)),
    "incident_minutes": Action("Total incident handling minutes for a loyalty tier of customers having at least one posted order. Count each ticket once.",
                               ("tier",), ("ticket", "account", "bridge", "orders")),
    "dashboard_orders": Action("Count unique order IDs observed in the dashboard export, where item observations can repeat.",
                               (), ("wide", "orders")),
    "posted_item_orders": Action("Count posted orders that contain an SKU and whose customer belongs to a loyalty tier.",
                                 ("sku", "tier"), ("line", "orders", "bridge", "account")),
    "net_collections": Action("Compute posted net collections in cents under the Finance policy effective on the date of each order. Subtract settled credits only under v2.",
                              (), ("policy", "orders", "credit")),
    "collections_delta": Action("Difference in posted net collections between the first brand and then other_brand. A negative difference is valid.",
                                ("other_brand",), ("policy", "orders", "credit")),
    "partner_share": Action("Share of posted orders placed by marketplace partners as a percentage. An unavailable buyer to partner mapping yields missing_relationship.",
                            (), ("partner", "orders", "bridge")),
    "resolve_review_case": Action("Set an open incident review case to resolved. Only supervisor with approved case can perform this action. A closed case stays closed.",
                                  ("case_id",), ("case_review",)),
}
REVIEW = (
    "Incident review workflow SQLite table: review_case(brand TEXT, case_id TEXT, state TEXT, approved INTEGER). "
    "Primary key (brand, case_id). To resolve, state must be open and approved must be 1, and the trusted current role must be supervisor. "
    "Change only the selected brand and case_id to state resolved. If any condition fails, deny and change nothing."
)


def knowledge():
    cards = assets()
    cards.append({"id": "review-workflow", "brand": None, "text": REVIEW, "links": {}})
    return cards


def descriptions(names):
    return "\n".join(
        f"- {name}(brand, {', '.join(ACTIONS[name].args) or 'no other arguments'}). "
        f"{ACTIONS[name].description} Path: {' → '.join(ACTIONS[name].path)}."
        for name in names
    )


def words(text):
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return {w.removesuffix("s") if len(w) > 4 else w for w in text.split()}


def choose_operation(text):
    tokens = words(text)
    object_scores = {name: len(tokens & words(terms)) for name, terms in OBJECTS.items()}
    nodes = sorted(OBJECTS, key=lambda name: -object_scores[name])[:3]
    # The term index selects object types. Expand actual catalogue edges before searching actions.
    visited = {node: 0 for node in nodes if object_scores[node]}
    frontier = set(visited)
    for depth in (1, 2):
        frontier = {dest for node in frontier if node in SPEC
                    for dest in SPEC[node][3].values() if dest not in visited}
        visited.update(dict.fromkeys(frontier, depth))
    def priority(name):
        action = ACTIONS[name]
        lexical = len(tokens & words(action.description + " " + name))
        return (2 * lexical + 2 * object_scores[action.path[0]]
                + sum(object_scores[node] for node in action.path) - visited.get(action.path[0], 3))
    ranked = sorted(ACTIONS, key=lambda name: (ACTIONS[name].path[0] not in visited, -priority(name), name))
    return nodes, ranked[:4]


def backend(count, seed):
    db, _, _ = snapshot(count, seed)
    db.set_authorizer(None)
    db.execute("PRAGMA query_only=OFF")
    db.execute("CREATE TABLE review_case(brand TEXT, case_id TEXT, state TEXT, approved INTEGER, PRIMARY KEY (brand, case_id))")
    db.executemany("INSERT INTO review_case VALUES (?, ?, ?, ?)",
                   [(b, case, state, approval) for b in BRANDS
                    for case, state, approval in (("R101", "open", 1), ("R102", "open", 0), ("R103", "resolved", 1))])
    db.commit()
    return db


def state(db):
    return dict(((b, case), v) for b, case, v in db.execute("SELECT brand, case_id, state FROM review_case"))


def net(db, b):
    posted, settled = codes(b)
    return db.execute(f"""
        SELECT COALESCE(SUM(o.billed - CASE WHEN o.day >= '2025-07-01'
          THEN COALESCE((SELECT SUM(c.cents) FROM {table(b, 'credit')} c WHERE c.oid=o.oid AND c.state=?),0)
          ELSE 0 END),0)
        FROM {table(b, 'orders')} o WHERE o.state=?""", (settled, posted)).fetchone()[0]


def invoke(db, op, b, args, role, exposed):
    if op not in exposed or b not in BRANDS or set(args) != set(ACTIONS[op].args):
        return {"status": "invalid_call"}
    if op == "partner_share":
        return {"status": "missing_relationship"}
    if op == "resolve_review_case":
        case = args["case_id"]
        if role != "supervisor":
            return {"status": "denied"}
        count = db.execute(
            "UPDATE review_case SET state='resolved' WHERE brand=? AND case_id=? AND state='open' AND approved=1",
            (b, case),
        ).rowcount
        return {"status": "resolved" if count else "denied"}
    if op == "net_collections":
        return {"status": "ok", "value": net(db, b)}
    if op == "collections_delta":
        peer = args["other_brand"]
        if peer not in BRANDS:
            return {"status": "invalid_call"}
        return {"status": "ok", "value": net(db, b) - net(db, peer)}
    if op == "incident_count":
        sql, params = f"SELECT COUNT(*) FROM {table(b, 'ticket')} WHERE kind='incident'", ()
    elif op == "dashboard_orders":
        sql, params = f"SELECT COUNT(DISTINCT oid) FROM {table(b, 'wide')}", ()
    else:
        orders = table(b, "orders")
        account = table(b, "account")
        bridge = table(b, "bridge")
        posted, _ = codes(b)
        if op == "incident_minutes":
            sql = f"""SELECT COALESCE(SUM(t.minutes),0) FROM {table(b, 'ticket')} t
                JOIN {account} a ON a.acct=t.acct
                WHERE t.kind='incident' AND a.tier=?
                AND EXISTS (SELECT 1 FROM {bridge} b JOIN {orders} o ON o.buyer=b.buyer
                            WHERE b.acct=a.acct AND o.state=?)"""
            params = (args["tier"], posted)
        elif op == "posted_item_orders":
            sql = f"""SELECT COUNT(*) FROM {orders} o JOIN {bridge} b ON o.buyer=b.buyer
                JOIN {account} a ON a.acct=b.acct WHERE a.tier=? AND o.state=?
                AND EXISTS (SELECT 1 FROM {table(b, 'line')} l WHERE l.oid=o.oid AND l.sku=?)"""
            params = (args["tier"], posted, args["sku"])
    return {"status": "ok", "value": db.execute(sql, params).fetchone()[0]}


def execute_sql(db, sql, writing):
    operations = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, sqlite3.SQLITE_RECURSIVE}

    def authorizer(op, table_name, column, *_):
        permitted_update = writing and op == sqlite3.SQLITE_UPDATE and table_name == "review_case" and column == "state"
        system_read = op == sqlite3.SQLITE_READ and table_name in {"sqlite_master", "sqlite_schema"}
        return sqlite3.SQLITE_OK if (op in operations and not system_read) or permitted_update else sqlite3.SQLITE_DENY

    steps = iter(range(501))
    db.set_progress_handler(lambda: 0 if next(steps, None) is not None else 1, 1000)
    db.set_authorizer(authorizer)
    try:
        rows = db.execute(sql).fetchmany(2)
        if writing:
            return {"status": "resolved" if rows else "denied"}
        if len(rows) == 1 and len(rows[0]) == 1:
            return {"status": "ok", "value": rows[0][0]}
        return {"status": "invalid_shape"}
    except sqlite3.Error as error:
        return {"status": "sql_error", "error": str(error)}
    finally:
        db.set_authorizer(None)
        db.set_progress_handler(None, 0)
