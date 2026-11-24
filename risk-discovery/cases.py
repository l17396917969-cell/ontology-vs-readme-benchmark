"""Make the same business facts available as Markdown cards and a typed graph."""
from dataclasses import dataclass
from random import Random

KINDS = ("sourcing", "recovery", "approval")
WORLDS = ("risk", "clear", "unknown")
ROOTS = {"sourcing": "LINE-ORION", "recovery": "SITE-SABLE", "approval": "PAY-VELA"}

@dataclass(frozen=True)
class Record:
    id: str
    kind: str
    note: str
    edges: tuple = ()


def scenario(kind, world):
    if kind == "sourcing":
        target = {"risk": "MILL-9", "clear": "MILL-4", "unknown": None}[world]
        records = [
            Record("LINE-ORION", "Production line", "Two orders cover the same sole certified input; each listed delivery alone covers line volume.",
                   (("S1", "sources_through", "VEND-H"), ("S2", "sources_through", "VEND-K"))),
            Record("VEND-H", "Direct vendor", "Has one approved processing site for this order.", (("S3", "processed_at", "MILL-9"),)),
            Record("VEND-K", "Direct vendor", "Has one approved processing site for this order.", (("S4", "processed_at", target),)),
            Record("MILL-9", "Factory", "One physical processing site.", ()),
            Record("MILL-4", "Factory", "A distinct physical processing site.", ()),
        ]
        affected = {"MILL-9"}
        witness = {"S1", "S2", "S3", "S4"}
    elif kind == "recovery":
        target = {"risk": "STEP-X", "clear": "CHECK-P", "unknown": None}[world]
        records = [
            Record("SITE-SABLE", "Dispatch site", "Current state: off. Restoration proceeds only through the listed action.",
                   (("R1", "restart_action", "STEP-X"),)),
            Record("STEP-X", "Restoration action", "Incomplete. Must wait for its listed prerequisite.", (("R2", "requires_completion_of", "STEP-Y"),)),
            Record("STEP-Y", "Validation action", "Incomplete. Must wait for its listed prerequisite.", (("R3", "requires_completion_of", "STEP-Z"),)),
            Record("STEP-Z", "Authorisation action", "Incomplete. Must wait for its listed prerequisite.", (("R4", "requires_completion_of", target),)),
            Record("CHECK-P", "Independent check", "Already passed and has no prerequisite.", ()),
        ]
        affected = {"STEP-X", "STEP-Y", "STEP-Z"}
        witness = {"R1", "R2", "R3", "R4"}
    else:
        target = {"risk": "UNIT-M", "clear": "UNIT-N", "unknown": None}[world]
        records = [
            Record("PAY-VELA", "Pending payment", "Policy requires the requesting and approving authority to originate from different accountable units.",
                   (("P1", "requested_by", "ACT-Q"), ("P2", "assigned_approval_to", "ACT-W"))),
            Record("ACT-Q", "Requestor account", "Raises purchase payments for one accountable unit.", (("P3", "authority_origin", "UNIT-M"),)),
            Record("ACT-W", "Named approval delegate", "A distinct login. Authority follows its delegation, irrespective of login ID.",
                   (("P4", "authority_origin", target),)),
            Record("UNIT-M", "Accountable unit", "Holds delegated spending authority.", ()),
            Record("UNIT-N", "Accountable unit", "A separate accountable unit.", ()),
        ]
        affected = {"UNIT-M"}
        witness = {"P1", "P2", "P3", "P4"}
    return records, affected, witness


def catalogue(kind, world, size):
    core, _, _ = scenario(kind, world)
    context = []
    repeats = 2 if size == "small" else 50
    for i in range(repeats):
        for j, other in enumerate(KINDS):
            # Keep distractor vocabulary close; their exact IDs and components are separate.
            foreign, _, _ = scenario(other, "clear")
            suffix = f"-D{i:02d}{j}"
            context.extend(Record(r.id+suffix, r.kind, r.note, tuple(
                (proof+suffix, rel, dest+suffix if dest else None) for proof, rel, dest in r.edges
            )) for r in foreign)
    cards = core + context
    Random(715).shuffle(cards)
    return cards


def markdown(record):
    lines = [f"### {record.id}", f"{record.kind}. {record.note}"]
    for evidence, rel, dest in record.edges:
        link = f"[{dest}](#{dest.lower()})" if dest else "record unavailable"
        lines.append(f"- {evidence}: {rel} {link}")
    return "\n".join(lines)
