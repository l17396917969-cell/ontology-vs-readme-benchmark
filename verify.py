"""Re-score the archived responses offline without changing the repository."""
import json
import os
from pathlib import Path
from shutil import copyfile
from subprocess import run
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent
EXPERIMENTS = {
    "metadata-retrieval": (
        ["raw.jsonl", "follow-up-raw.jsonl"],
        [("run.py", "grade"), ("follow_up.py",), ("metric_demo.py",), ("relationship_replay.py",)],
        ["catalogue.md", "ontology.json", "questions.json", "results.json",
         "follow-up-questions.json", "follow-up-results.json", "metric-demo.json", "relationship-replay.json"],
        248,
    ),
    "object-actions": (
        ["raw.jsonl", "typed-raw.jsonl"],
        [("compare.py", "grade"), ("typed_compare.py",)],
        ["questions.json", "object-schema.json", "results.json", "typed-results.json"],
        240,
    ),
    "risk-discovery": (
        ["raw.jsonl"],
        [("run.py", "prepare"), ("run.py", "grade")],
        ["core-cards.json", "results.json"],
        108,
    ),
}


def main():
    seen = set()
    with TemporaryDirectory(prefix="ontology-readme-replay-") as scratch:
        for study, (logs, commands, results, count) in EXPERIMENTS.items():
            source = ROOT / study
            stage = Path(scratch) / study
            stage.mkdir()
            ids = []
            for log in logs:
                copyfile(source / log, stage / log)
                for line in (stage / log).read_text().splitlines():
                    response = json.loads(line)
                    ids.append(response.get("response_id", response.get("id")))
            if len(ids) != count or len(set(ids)) != count or seen.intersection(ids):
                raise SystemExit(f"Missing or duplicate API responses in {study}.")
            seen.update(ids)

            env = {**os.environ, "BENCH_ARTIFACT_DIR": str(stage), "PYTHONDONTWRITEBYTECODE": "1"}
            env.pop("DEEPSEEK_API_KEY", None)
            for filename, *arguments in commands:
                process = run([sys.executable, str(source / filename), *arguments], env=env, capture_output=True, text=True)
                if process.returncode:
                    sys.stderr.write(process.stdout + process.stderr)
                    raise SystemExit(f"Replay failed: {study}/{filename}.")
            for name in results:
                actual = (stage / name).read_text()
                expected = (source / name).read_text()
                if name.endswith(".json"):
                    matches = json.loads(actual) == json.loads(expected)
                else:
                    matches = actual == expected
                if not matches:
                    raise SystemExit(f"Replayed output changed: {study}/{name}.")
            print(f"{study}: {count} responses and all archived results verified.")
    print(f"Verified {len(seen)} responses without API calls.")


if __name__ == "__main__":
    main()
