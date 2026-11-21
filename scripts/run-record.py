#!/usr/bin/env python
"""Append one timestamped event to a run's JSON event log, so a review can read the run instead of inferring it.

    python scripts/run-record.py <log.json> <event> [key=value ...]

The log is {"events": [{"t": "<UTC ISO>", "event": "<name>", ...keys}]}; created on first use. Values are
strings unless they parse as integers or floats. Any event name is accepted; the ones the commands use:

  implementation run (.audit/issue-<n>/run.json):
    start issue=<n> branch=<name> session=<transcript id if known>
    task-start id=<T> owner=<agent or orchestrator> attempt=<k>
    task-end id=<T> status=pass|fail|blocked
    critic id=<T> mode=plan|diff round=<k> verdict=PASS|FAIL blockers=<n> majors=<n>
    rework id=<T> cause=fact-missing|check-missing|rule-misapplied|defect
    run kind=build|spec|suite|record|package filter=<name> seconds=<s> total=<n> failed=<n>
    ask id=<short slug>            answer id=<same slug>
    finding source=<who found it> caught-by=<the check that caught it, or none> text=<one line>
    pr number=<n>                  compact
  planning run (.audit/plan-issue-<n>/plan.json):
    start issue=<n> session=<id>   ask id=<slug>   answer id=<slug>
    critic round=<k> verdict=PASS|FAIL blockers=<n> majors=<n>
    rewrite requirement=<k>        shape text=<one line>        ready
"""
import datetime, json, os, re, sys


def parse(v):
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v  # a commit sha like 6395e156 is not a float


# What each known event must carry. Extra keys (note=, sha=, text=) are always welcome.
REQUIRED = {
    "start": ["issue"], "task-start": ["id", "owner"], "task-end": ["id", "status"],
    "critic": ["round", "verdict"], "rework": ["id", "cause"], "run": ["kind", "seconds"],
    "ask": ["id"], "answer": ["id"], "finding": ["source", "caught-by"], "pr": ["number"],
    "rewrite": ["requirement"], "shape": ["text"], "ready": [], "compact": [],
}
CAUSES = ("fact-missing", "check-missing", "rule-misapplied", "defect")


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    path, event = argv[1], argv[2]
    rec = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "event": event}
    for kv in argv[3:]:
        k, _, v = kv.partition("=")
        rec[k] = parse(v)
    missing = [k for k in REQUIRED.get(event, []) if k not in rec]
    if missing:
        print(f"run-record: '{event}' needs {', '.join(k + '=' for k in REQUIRED[event])} - missing {', '.join(missing)}. Nothing written.", file=sys.stderr)
        return 2
    if event == "critic":
        rec["verdict"] = str(rec["verdict"]).upper()
        if rec["verdict"] not in ("PASS", "FAIL"):
            print("run-record: verdict= must be PASS or FAIL. Nothing written.", file=sys.stderr); return 2
    if event == "rework" and rec["cause"] not in CAUSES:
        print(f"run-record: cause= must be one of {', '.join(CAUSES)}. Nothing written.", file=sys.stderr); return 2
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    log = {"events": []}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            log = json.load(f)
    log["events"].append(rec)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=1)
    print(json.dumps(rec))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
