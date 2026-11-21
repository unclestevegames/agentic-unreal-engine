#!/usr/bin/env python
"""Measure how an agentic development process performed, from Claude Code transcripts and run folders.

Project-agnostic: everything that belongs to one project arrives as an argument. Reads
  - the Claude Code transcripts for a project (~/.claude/projects/<slug>/*.jsonl and their subagents/),
  - optionally a run-folder tree (<audit>/<prefix><n>/briefs/*.md, state.md) for churn,
  - optionally the PRs as `gh pr list --json number,state,createdAt,mergedAt,additions,deletions,title,closingIssuesReferences`
    writes them, for size per issue: a PR belongs to the issues it closes, whatever its title says.

Transcript facts this relies on (Claude Code 2.1.x):
  - one record per content block, the message's usage repeated on each: usage is counted once per message id;
  - sub-agent transcripts carry partial usage per block: the per-message maximum is taken;
  - context size of a call = input + cache_read + cache_creation tokens of its usage;
  - a compaction is a `system` record with subtype `compact_boundary`; `/compact` typed by the user is a
    user record naming the command.
  - a prompt command the user types (a command file, not a built-in like /clear or /model) is a user string
    opening `<command-message>`, then `<command-name>`, then `<command-args>` only when arguments were given;
  - a run begun without one shows only as its shell call writing a `start` event to its record: the record's
    events carry no session, so that call, never the event's timestamp, says where in a transcript the run began.

Usage (see --help): python session-stats.py --transcripts DIR [--since YYYY-MM-DD] [--weeks 4]
    [--audit DIR --audit-prefix issue-] [--prs prs.json] [--kinds kinds.json] [--top-fill 3] [--json out.json]
"""
import argparse, collections, datetime, glob, json, os, re, statistics, sys

sys.stdout.reconfigure(encoding="utf-8")


def parse_ts(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else 0


def union_hours(spans):
    """Hours covered by (start, end) spans, overlaps counted once: questions open together are one wait."""
    total, reach = 0.0, None
    for a, b in sorted(spans):
        if reach is None or a > reach: total += (b - a).total_seconds(); reach = b
        elif b > reach: total += (b - reach).total_seconds(); reach = b
    return total / 3600


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""


COMMAND = re.compile(r"<command-name>(/[\w:-]+)</command-name>(?:\s*<command-args>(.*?)</command-args>)?", re.S)
RUN_START = re.compile(r"(?:^|[;&|]\s*)python[\d.]*(?:\s+-\w+)*\s+\S*run-record\.py\s+\S+\s+start\b[^\n]*?\bissue=(\d+)", re.M)


def typed(text):
    """Whether the text of a user record is the owner's own, not something the harness wrote."""
    return not text.startswith(("<", "[Request interrupted"))


def new_segment(path, cmd=None, arg=None):
    return dict(path=path, first=None, last=None, calls=0, usage=collections.Counter(), maxctx=0, tools=collections.Counter(),
                agents=collections.Counter(), asks=0, cmd=cmd, arg=arg, version=None, model=None, compactions=0, manual_compacts=0,
                branch=collections.Counter(), tools_total=0, ask_spans=[], wait_text=0.0, owner=[],
                ctx_series=[], fill=collections.Counter(), fill_items=[], images=0, verdicts=collections.Counter(), status=None,
                handbacks=[], seen={})


def report_of(text):
    """The STATUS: and VERDICT: a report carries, either None."""
    st, vd = re.search(r"STATUS:\s*([A-Z_]+)", text), re.search(r"VERDICT:\s*(PASS|FAIL)", text)
    return st and st.group(1), vd and vd.group(1)


def issue_of(cmd, arg, implement_cmd):
    """The issue a segment builds, None if it is not an implementation run."""
    m = re.match(r"\s*(\d+)", arg or "") if cmd == implement_cmd else None
    return int(m.group(1)) if m else None


def run_started(r):
    """The issue whose implementation run this record's shell call starts, else None. A planning record's start names a plan.json."""
    content = r["message"].get("content") if r.get("type") == "assistant" else None
    for b in content if isinstance(content, list) else []:
        command = str((b.get("input") or {}).get("command", "")) if b.get("type") == "tool_use" else ""
        m = RUN_START.search(command)
        if m and f"{m.group(1)}/run.json" in command:
            return int(m.group(1))
    return None


def read_transcript(path, implement_cmd, sub=False):
    """One pass over a transcript. Returns its segments, each a dict of everything the tables need: a new
    segment starts wherever the issue being worked changes, at a prompt command the owner types or at the call
    that starts another issue's run, so a session that ran several issues charges each only for its own part.
    A sub-agent transcript is one segment."""
    segs = [new_segment(path)]
    s = segs[0]
    pending_ask = {}
    last_asst_text_only = None
    idmap = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        t = r.get("type")
        ts = r.get("timestamp")
        if not sub and t == "user" and isinstance(r["message"].get("content"), str) and r["message"]["content"].lstrip().startswith("<command-message>"):
            mm = COMMAND.search(r["message"]["content"])
            if mm:
                s = new_segment(path, mm.group(1), (mm.group(2) or "").strip())
                segs.append(s)
                if re.search(r"[^\W\d_]", s["arg"]):  # a bare command, or one given only an issue number, says nothing
                    s["owner"].append((ts, f"{s['cmd']} {s['arg']}"))
        started = None if sub else run_started(r)
        if started and started != issue_of(s["cmd"], s["arg"], implement_cmd):
            mid = r["message"].get("id")
            if mid in s["seen"]:  # the old segment charged this message for its earlier blocks; it moves whole
                del s["seen"][mid]; s["calls"] -= 1; s["ctx_series"].pop()
            s = new_segment(path, implement_cmd, str(started))
            segs.append(s)
        seen = s["seen"]
        if ts:
            s["first"] = s["first"] or ts
            s["last"] = ts
        if r.get("version"):
            s["version"] = r["version"]
        if r.get("gitBranch"):
            s["branch"][r["gitBranch"]] += 1
        if t == "system" and r.get("subtype") == "compact_boundary":
            s["compactions"] += 1
        elif t == "attachment":
            a = r.get("attachment", {})
            prompt = a.get("prompt") if isinstance(a.get("prompt"), str) else ""
            if a.get("type") == "prompt_snapshot":
                pass  # the system prompt, logged at the start and at each compaction; not context the run added
            elif a.get("type") == "queued_command" and (prompt.startswith("<agent-message") or "<result>" in prompt):
                s["fill"]["result:Agent"] += len(prompt)  # a sub-agent's report, handed back
                s["fill_items"].append((len(prompt), "Agent", "hand-back"))
            else:
                s["fill"]["attachment:" + str(a.get("type"))] += len(json.dumps(a))
                if a.get("type") == "queued_command" and (a.get("origin") or {}).get("kind") == "human" and ts and prompt:
                    s["owner"].append((ts, prompt))
        elif t == "assistant":
            m = r["message"]
            u = m.get("usage") or {}
            mid = m.get("id")
            s["model"] = m.get("model") or s["model"]
            blocks = m.get("content", []) if isinstance(m.get("content"), list) else []
            for b in blocks:
                if b.get("type") == "tool_use":
                    s["tools"][b["name"]] += 1
                    s["tools_total"] += 1
                    inp = b.get("input") or {}
                    idmap[b["id"]] = (b["name"], str(inp.get("description") or inp.get("file_path") or str(inp.get("command", ""))[:60]))
                    s["fill"]["output:tool_use:" + b["name"]] += len(json.dumps(inp))
                    if b["name"] == "AskUserQuestion":
                        s["asks"] += 1
                        if ts: pending_ask[b["id"]] = parse_ts(ts)
                    if b["name"] == "Agent":
                        s["agents"][inp.get("subagent_type")] += 1
                    if b["name"] == "SubagentHandback":
                        s["handbacks"].append(report_of(str(inp.get("message", ""))))
                elif b.get("type") == "text":
                    s["fill"]["output:text"] += len(b["text"])
                    st, vd = report_of(b["text"])
                    if vd: s["verdicts"][vd] += 1
                    if st: s["status"] = st
            if u:
                vals = {k: u.get(k, 0) for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
                if mid not in seen:
                    seen[mid] = vals
                    s["calls"] += 1
                    ctx = vals["input_tokens"] + vals["cache_read_input_tokens"] + vals["cache_creation_input_tokens"]
                    s["maxctx"] = max(s["maxctx"], ctx)
                    s["ctx_series"].append((ts[11:16] if ts else "", ctx))
                elif sub:
                    seen[mid] = {k: max(seen[mid][k], vals[k]) for k in vals}
            if ts and all(b.get("type") != "tool_use" for b in blocks) and blocks:
                last_asst_text_only = parse_ts(ts)
        elif t == "user":
            m = r["message"]
            c = m.get("content")
            if isinstance(c, str):
                if "<command-name>/compact</command-name>" in c:
                    s["manual_compacts"] += 1
                if not r.get("isMeta") and not r.get("isCompactSummary") and not c.startswith("<"):
                    if ts and typed(c): s["owner"].append((ts, c))
                    if last_asst_text_only and ts:
                        s["wait_text"] += (parse_ts(ts) - last_asst_text_only).total_seconds()
                    last_asst_text_only = None
                s["fill"]["user:" + ("meta" if r.get("isMeta") else "message")] += len(c)
            elif isinstance(c, list):
                for b in c:
                    if b.get("type") == "tool_result":
                        cc = b.get("content")
                        if isinstance(cc, list) and any(isinstance(x, dict) and x.get("type") == "image" for x in cc):
                            s["images"] += 1
                        txt = text_of(cc)
                        name, desc = idmap.get(b.get("tool_use_id"), ("?", ""))
                        s["fill"]["result:" + name] += len(txt)
                        s["fill_items"].append((len(txt), name, desc))
                        if b.get("tool_use_id") in pending_ask and ts:
                            s["ask_spans"].append((pending_ask.pop(b["tool_use_id"]), parse_ts(ts)))
                    elif b.get("type") == "text":
                        s["fill"]["user:text"] += len(b["text"])
                        if not r.get("isMeta") and not r.get("isCompactSummary") and typed(b["text"]) and ts:
                            s["owner"].append((ts, b["text"]))
    for s in segs:
        for v in s.pop("seen").values():
            for k in v:
                s["usage"][k] += v[k]
        # an agent that hands its report back through a tool call reports once per call (a resumed agent reports
        # again), and its text then only mentions STATUS:/VERDICT:; an agent that ends in text reports in its last one
        hb = s.pop("handbacks"); last = s.pop("status")
        if hb:
            s["verdicts"] = collections.Counter(vd for st, vd in hb if vd)
        s["statuses"] = collections.Counter(st for st, vd in hb if st) if hb else collections.Counter([last] if last else [])
    return [s for s in segs if s["calls"]]


def cost(u, w):
    return (u["input_tokens"] * w["in"] + u["cache_creation_input_tokens"] * w["cw"] + u["cache_read_input_tokens"] * w["cr"] + u["output_tokens"] * w["out"]) / 1e6


def session_timeline(folder, prefix):
    """One session read closely: where its time went, and every word the owner said."""
    paths = glob.glob(os.path.join(folder, prefix + "*.jsonl"))
    if not paths:
        print("no transcript starts with", prefix); return
    pending = {}; buckets = collections.Counter(); counts = collections.Counter(); longest = []
    for line in open(paths[0], encoding="utf-8", errors="replace"):
        try: r = json.loads(line)
        except Exception: continue
        t = r.get("type"); ts = r.get("timestamp", "")
        if t == "assistant":
            for b in r["message"].get("content", []) if isinstance(r["message"].get("content"), list) else []:
                if b.get("type") == "tool_use":
                    inp = b.get("input") or {}
                    desc = str(inp.get("description") or inp.get("file_path") or str(inp.get("command", ""))[:60])
                    pending[b["id"]] = (b["name"], desc, parse_ts(ts) if ts else None, inp)
                    if b["name"] == "AskUserQuestion":
                        for q in inp.get("questions", []): print(f"[{ts[11:16]}] ASK: {q.get('question', '')[:400]!r}")
                    if b["name"] == "Agent":
                        print(f"[{ts[11:16]}] AGENT: {inp.get('subagent_type')} {inp.get('description', '')!r}")
        elif t == "user":
            c = r["message"].get("content")
            if isinstance(c, str):
                if not r.get("isMeta") and not c.startswith("<local-command") and "<command-name>/clear" not in c:
                    print(f"[{ts[11:16]}] USER: {c[:400]!r}")
            elif isinstance(c, list):
                for b in c:
                    if b.get("type") == "text" and not r.get("isMeta") and "<task-notification>" not in b["text"][:60]:
                        print(f"[{ts[11:16]}] USER: {b['text'][:400]!r}")
                    if b.get("type") == "tool_result" and b.get("tool_use_id") in pending and ts:
                        name, desc, st, inp = pending.pop(b["tool_use_id"])
                        if st is None: continue
                        d = (parse_ts(ts) - st).total_seconds()
                        key = name
                        if name in ("Bash", "PowerShell"):
                            cmd = str(inp.get("command", "")).lower()
                            key = "shell:tests" if ("test" in cmd or "automation" in cmd) else "shell:build" if "build" in cmd else "shell:git" if cmd.strip().startswith("git") else "shell:other"
                        if name == "Agent": key = "Agent:" + str(inp.get("subagent_type"))
                        buckets[key] += d; counts[key] += 1; longest.append((d, key, desc, ts[11:16]))
        elif t == "system" and r.get("subtype") == "compact_boundary":
            print(f"[{ts[11:16]}] COMPACT")
    print("\ntime per tool (foreground calls only; background agents and jobs return at once):")
    for k, v in buckets.most_common():
        print(f"  {k:30s} n={counts[k]:4d} total={v / 3600:6.2f}h avg={v / counts[k]:7.1f}s")
    print("longest 15:")
    for d, k, desc, ts in sorted(longest, reverse=True)[:15]:
        print(f"  {d / 60:7.1f}m {k:26s} {ts} {desc[:80]!r}")


def run_records(audit, prefix, since, until):
    """Section H: what the runs recorded about themselves (run.json / plan.json event logs)."""
    rows = []
    for d in sorted(glob.glob(os.path.join(audit, prefix + "*")) + glob.glob(os.path.join(audit, "plan-issue-*"))):
        for name in ("run.json", "plan.json"):
            f = os.path.join(d, name)
            if not os.path.exists(f): continue
            try: ev = json.load(open(f, encoding="utf-8")).get("events", [])
            except Exception: continue
            if not ev: continue
            day = ev[0].get("t", "")[:10]
            if day < since.isoformat() or day > until.isoformat(): continue
            by = collections.defaultdict(list)
            for e in ev:
                e = dict(e)
                e.setdefault("id", e.get("task") or e.get("topic"))      # spellings an early run chose for itself
                if "verdict" in e:
                    v = str(e["verdict"]).upper(); e["verdict"] = "PASS" if v.startswith("PASS") else "FAIL" if v.startswith("FAIL") else v
                by[e.get("event")].append(e)
            attempts = collections.Counter(e.get("id") for e in by["task-start"] + by["task-end"] if e.get("id"))
            ends = collections.Counter(e.get("id") for e in by["task-end"])
            verd = collections.Counter(e.get("verdict") for e in by["critic"] if e.get("verdict"))
            causes = collections.Counter(e.get("cause") for e in by["rework"])
            caught = collections.Counter(e.get("caught-by") for e in by["finding"])
            runs = collections.defaultdict(float)
            for e in by["run"]: runs[e.get("kind")] += float(e.get("seconds") or 0)
            suite = [e for e in by["run"] if e.get("kind") == "suite"]
            span = (parse_ts(ev[-1]["t"]) - parse_ts(ev[0]["t"])).total_seconds() / 3600
            rows.append(dict(folder=os.path.basename(d), kind=name[:-5], day=day, hours=span, tasks=len(attempts), retried=sum(1 for v in ends.values() if v > 1),
                             critic=dict(verd), rework=dict(causes), findings=dict(caught), asks=len(by["ask"]), runs={k: round(v / 60, 1) for k, v in runs.items()},
                             suite_total=(suite[-1].get("total") if suite else None), rewrites=len(by["rewrite"]), shapes=len(by["shape"])))
    print("\n## H. What the runs recorded about themselves (run.json / plan.json; absent for runs before the records existed)")
    if not rows:
        print("  none in the window"); return
    for r in rows:
        print(f"  {r['folder']:16s} {r['kind']:4s} {r['day']} span {r['hours']:5.1f}h tasks {r['tasks']} retried {r['retried']} critic {r['critic']} rework-causes {r['rework']} findings-caught-by {r['findings']} asks {r['asks']} runs(min) {r['runs']} suite-total {r['suite_total']} rewrites {r['rewrites']} shapes {r['shapes']}")
    tot = collections.Counter()
    for r in rows:
        for k, v in r["rework"].items(): tot["rework:" + str(k)] += v
        for k, v in r["findings"].items(): tot["finding-caught-by:" + str(k)] += v
    if tot: print("  totals: " + ", ".join(f"{k} {v}" for k, v in tot.most_common()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcripts", required=True, help="the project's Claude Code transcript folder")
    ap.add_argument("--since", help="first day (YYYY-MM-DD); default = today minus --weeks")
    ap.add_argument("--until", help="last day (YYYY-MM-DD), inclusive; default today")
    ap.add_argument("--weeks", type=int, default=4)
    ap.add_argument("--audit", help="run-folder tree: <audit>/<prefix><n>/briefs/*.md and state.md")
    ap.add_argument("--audit-prefix", default="issue-")
    ap.add_argument("--prs", help="JSON array from gh pr list --json number,state,createdAt,mergedAt,additions,deletions,title,closingIssuesReferences")
    ap.add_argument("--kinds", help="JSON file: {kind: regex over PR title}; first match wins, else 'other'")
    ap.add_argument("--weights", default="in=1,cw=1.25,cr=0.1,out=5", help="cost weights per token class")
    ap.add_argument("--implement-cmd", default="/implement-issue", help="the command whose sessions implement one issue")
    ap.add_argument("--plan-cmds", default="/plan-issues")
    ap.add_argument("--top-fill", type=int, default=3, help="context-fill breakdown for the N largest runs")
    ap.add_argument("--json", help="write every per-session record here")
    ap.add_argument("--session", help="instead of the tables: print one session's timeline (time per tool, every user message, ask and agent spawn) by transcript-name prefix")
    a = ap.parse_args()
    if a.session:
        return session_timeline(a.transcripts, a.session)

    w = {k: float(v) for k, v in (kv.split("=") for kv in a.weights.split(","))}
    until = datetime.date.fromisoformat(a.until) if a.until else datetime.date.today()
    since = datetime.date.fromisoformat(a.since) if a.since else until - datetime.timedelta(weeks=a.weeks)
    kinds = json.load(open(a.kinds, encoding="utf-8")) if a.kinds else {}
    prs = json.load(open(a.prs, encoding="utf-8-sig")) if a.prs else []
    if a.prs and not prs:
        print("session-stats: %s holds no pull requests - change sizes will be empty;"
              " check the fetch before reading the tables" % a.prs, file=sys.stderr)
    for p in prs: p["closes"] = [c["number"] for c in p.get("closingIssuesReferences") or []]
    # issues joined by a PR that closes them are one unit of work
    parent = {}

    def unit_of(i):
        while parent.get(i, i) != i: i = parent[i]
        return i
    for p in prs:
        for i in p["closes"][1:]: parent[unit_of(i)] = unit_of(p["closes"][0])
    members = collections.defaultdict(set); merged = collections.defaultdict(list)
    for p in prs:
        for i in p["closes"]: members[unit_of(i)].add(i)
        if p["closes"] and p["state"] == "MERGED": merged[unit_of(p["closes"][0])].append(p)

    def kind_of(title):
        for k, rx in kinds.items():
            if re.search(rx, title, re.I): return k
        return "other"

    def week_of(d):
        return "week %d" % (((datetime.date.fromisoformat(d) - since).days // 7) + 1)

    def segment_record(s, sid, subs):
        sub = collections.Counter(); subcalls = 0; sub_verdicts = collections.Counter(); sub_status = collections.Counter(); sub_hours = 0.0
        for ss in subs:
            for k in ss["usage"]: sub[k] += ss["usage"][k]
            subcalls += ss["calls"]; sub_verdicts.update(ss["verdicts"]); sub_status.update(ss["statuses"])
            sub_hours += (parse_ts(ss["last"]) - parse_ts(ss["first"])).total_seconds() / 3600
        day = s["first"][:10]
        hours = (parse_ts(s["last"]) - parse_ts(s["first"])).total_seconds() / 3600
        issue = issue_of(s["cmd"], s["arg"], a.implement_cmd)
        rec = dict(date=day, week=week_of(day), sid=sid[:8], cmd=s["cmd"] or "", arg=s["arg"] or "", issue=issue, hours=round(hours, 2),
                   wait_ask_h=round(union_hours(s["ask_spans"]), 2), wait_text_h=round(s["wait_text"] / 3600, 2), calls=s["calls"],
                   tools_per_call=round(s["tools_total"] / max(1, s["calls"]), 2), maxctx_k=s["maxctx"] // 1000, compactions=s["compactions"],
                   manual_compacts=s["manual_compacts"], main_meq=round(cost(s["usage"], w), 2), sub_meq=round(cost(sub, w), 2), subcalls=subcalls,
                   sub_hours=round(sub_hours, 2), asks=s["asks"], agents=dict(s["agents"]), n_agents=sum(s["agents"].values()),
                   critic_pass=sub_verdicts["PASS"], critic_fail=sub_verdicts["FAIL"], agent_blocked=sub_status["BLOCKED"],
                   images=s["images"], version=s["version"], model=s["model"],
                   out_k=s["usage"]["output_tokens"] // 1000, cache_read_M=round(s["usage"]["cache_read_input_tokens"] / 1e6, 1),
                   fill=dict(s["fill"]), fill_items=sorted(s["fill_items"], reverse=True)[:12], ctx_series=s["ctx_series"])
        return rec

    sessions = []; owner_said = []
    for p in sorted(glob.glob(os.path.join(a.transcripts, "*.jsonl"))):
        mtime = datetime.date.fromtimestamp(os.stat(p).st_mtime)
        if mtime < since: continue
        segs = read_transcript(p, a.implement_cmd)
        sid = os.path.basename(p)[:-6]
        # ahead of the cuts below: a short question, or a session begun before the window, is still the owner's word
        owner_said += [(when, sid[:8], s["cmd"] or "", text) for s in segs for when, text in s["owner"] if since.isoformat() <= when[:10] <= until.isoformat()]
        if sum(s["calls"] for s in segs) < 5: continue
        day = segs[0]["first"][:10]
        if day < since.isoformat() or day > until.isoformat(): continue
        subs = [ss for sp in glob.glob(os.path.join(a.transcripts, sid, "subagents", "*.jsonl")) for ss in read_transcript(sp, a.implement_cmd, sub=True)]
        for n, s in enumerate(segs):
            # a sub-agent is charged whole to the segment it started in
            end = segs[n + 1]["first"] if n + 1 < len(segs) else None
            sessions.append(segment_record(s, sid, [ss for ss in subs if (n == 0 or ss["first"] >= s["first"]) and (end is None or ss["first"] < end)]))
    if a.json:
        json.dump(sessions, open(a.json, "w"), indent=1, default=str)

    print(f"# Performance review: {since} .. {until}  ({len(sessions)} sessions, transcripts {a.transcripts})")
    print("\n## A. Every session, a row per prompt command typed in it and per run begun without one")
    print("date       sid      command                 hours waitAsk waitTxt calls tools/call ctxMax compact main  sub   asks agents version  arg")
    for s in sorted(sessions, key=lambda s: s["date"]):
        print(f"{s['date']} {s['sid']} {s['cmd'][:22]:22s} {s['hours']:5.1f} {s['wait_ask_h']:6.1f} {s['wait_text_h']:6.1f} {s['calls']:5d} {s['tools_per_call']:9.2f} {s['maxctx_k']:5d}k {s['compactions']:2d}/{s['manual_compacts']:<2d} {s['main_meq']:5.1f} {s['sub_meq']:5.1f} {s['asks']:3d} {s['n_agents']:5d} {str(s['version']):8s} {s['arg'][:30]}")

    impl = [s for s in sessions if s["cmd"] == a.implement_cmd and s["issue"]]
    by_unit = collections.defaultdict(list)
    for s in impl:
        by_unit[unit_of(s["issue"])].append(s); members[unit_of(s["issue"])].add(s["issue"])
    print("\n## B. Implementation runs per issue (Meq = cost-equivalent millions of tokens at the given weights)")
    print("issues     first-run  sessions hours  Meq   lines  Meq/100l  asks critic P/F blocked kind  title")
    issue_rows = []
    for u, ss in sorted(by_unit.items(), key=lambda kv: kv[1][0]["date"]):
        i = "+".join(str(x) for x in sorted(members[u])); ps = merged.get(u, [])
        lines = sum(p["additions"] + p["deletions"] for p in ps) or None; title = ps[0]["title"] if ps else ""
        meq = sum(s["main_meq"] + s["sub_meq"] for s in ss); hours = sum(s["hours"] for s in ss)
        row = dict(issue=i, date=ss[0]["date"], week=ss[0]["week"], sessions=len(ss), hours=hours, meq=meq, lines=lines, kind=kind_of(title) if title else "unmerged",
                   asks=sum(s["asks"] for s in ss), cp=sum(s["critic_pass"] for s in ss), cf=sum(s["critic_fail"] for s in ss),
                   blocked=sum(s["agent_blocked"] for s in ss), maxctx=max(s["maxctx_k"] for s in ss), calls=sum(s["calls"] for s in ss), tpc=med([s["tools_per_call"] for s in ss]))
        issue_rows.append(row)
        per = f"{100 * meq / lines:8.2f}" if lines else "       -"
        print(f"{i:10s} {row['date']}  {len(ss):8d} {hours:5.1f} {meq:5.1f} {str(lines):>6s} {per} {row['asks']:5d} {row['cp']:6d}/{row['cf']:<4d} {row['blocked']:7d} {row['kind'][:6]:6s} {title[:50]}")

    print("\n## C. By week (implementation runs; medians unless stated)")
    print("week    runs issues ctxMax calls tools/call  Meq  Meq/100l asks/run critic-fail%  rerun-issues compactions versions")
    weeks = sorted(set(s["week"] for s in sessions), key=lambda x: int(x.split()[1]))
    for wk in weeks:
        ss = [s for s in impl if s["week"] == wk]
        rows = [r for r in issue_rows if r["week"] == wk]
        if not ss: continue
        per = [100 * r["meq"] / r["lines"] for r in rows if r["lines"]]
        cf = sum(r["cf"] for r in rows); cp = sum(r["cp"] for r in rows)
        print(f"{wk:7s} {len(ss):4d} {len(rows):6d} {med([s['maxctx_k'] for s in ss]):5.0f}k {med([s['calls'] for s in ss]):5.0f} {med([s['tools_per_call'] for s in ss]):9.2f} {med([r['meq'] for r in rows]):5.1f} {med(per):8.2f} {sum(s['asks'] for s in ss) / len(ss):8.2f} {100 * cf / max(1, cf + cp):11.0f}% {sum(1 for r in rows if r['sessions'] > 1):12d} {sum(s['compactions'] for s in ss):11d} {sorted(set(str(s['version']) for s in ss))}")
    if kinds:
        print("\n## D. By kind of work and week (median Meq per 100 changed lines; runs)")
        for k in list(kinds) + ["other"]:
            parts = []
            for wk in weeks:
                rows = [r for r in issue_rows if r["week"] == wk and r["kind"] == k and r["lines"]]
                if rows: parts.append(f"{wk}: {med([100 * r['meq'] / r['lines'] for r in rows]):.2f} ({len(rows)})")
            if parts: print(f"  {k:14s} " + " | ".join(parts))

    plan_cmds = a.plan_cmds.split(",")
    plans = [s for s in sessions if s["cmd"] in plan_cmds]
    print("\n## E. Planning sessions by week")
    print("week    sessions  Meq/session  asks/session  critic-rounds/session  hours(median)")
    for wk in weeks:
        ss = [s for s in plans if s["week"] == wk]
        if not ss: continue
        rounds = sum(sum(v for k, v in s["agents"].items() if k and "critic" in k) for s in ss)
        print(f"{wk:7s} {len(ss):8d} {sum(s['main_meq'] + s['sub_meq'] for s in ss) / len(ss):11.1f} {sum(s['asks'] for s in ss) / len(ss):13.1f} {rounds / len(ss):21.1f} {med([s['hours'] for s in ss]):13.1f}")

    if a.audit:
        print("\n## F. Churn from the run folders (briefs per issue folder, by folder date)")
        print("week    issues implBriefs reworkBriefs criticBriefs rework/impl tasks(median)")
        C = collections.defaultdict(lambda: [0, 0, 0, 0, []])
        for d in glob.glob(os.path.join(a.audit, a.audit_prefix + "*")):
            bdir = os.path.join(d, "briefs")
            if not os.path.isdir(bdir): continue
            mt = datetime.date.fromtimestamp(os.path.getmtime(d))
            if mt < since or mt > until: continue
            b = os.listdir(bdir)
            rw = sum(1 for x in b if re.search(r"rework|followup|fix|-R\d+-", x))
            im = sum(1 for x in b if re.search(r"implementer|artist|designer|integrator|tester", x) and not re.search(r"rework|followup|fix", x))
            cr = sum(1 for x in b if "critic" in x)
            tasks = 0
            sp = os.path.join(d, "state.md")
            if os.path.exists(sp):
                tasks = len(re.findall(r"^\| T\d+", open(sp, encoding="utf-8", errors="replace").read(), flags=re.M))
            c = C[week_of(mt.isoformat())]; c[0] += 1; c[1] += im; c[2] += rw; c[3] += cr; c[4].append(tasks)
        for wk in weeks:
            c = C.get(wk)
            if c: print(f"{wk:7s} {c[0]:6d} {c[1]:10d} {c[2]:12d} {c[3]:12d} {c[2] / max(1, c[1]):11.2f} {med(c[4]):13.1f}")

    if a.audit:
        run_records(a.audit, a.audit_prefix, since, until)

    print("\n## I. Every message the owner typed in the window, oldest first, whatever session or command it arrived in; a bare command is not one")
    for when, sid, cmd, text in sorted(owner_said):
        print(f"  {when[:16]} {sid} {cmd[:20]:20s} {text!r}")

    print(f"\n## G. What fills the context — the {a.top_fill} largest runs (chars, by source; output is retained, results and attachments are added)")
    for s in sorted(impl, key=lambda s: -s["maxctx_k"])[:a.top_fill]:
        f = s["fill"]; tot = sum(f.values()) or 1
        print(f"  {s['sid']} issue {s['issue']} ctxMax {s['maxctx_k']}k calls {s['calls']} output {s['out_k']}k tokens; images {s['images']}; cache-read {s['cache_read_M']}M")
        groups = collections.Counter()
        for k, v in f.items():
            g = k.split(":")[0] if not k.startswith("attachment") else "attachment"
            groups[g if g != "result" else "result:" + k.split(":")[1]] += v
        print("     " + ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in groups.most_common(9)))
        print("     largest results: " + "; ".join(f"{n // 1000}k {name} {desc[:40]!r}" for n, name, desc in s["fill_items"][:5]))
        steps = s["ctx_series"][:: max(1, len(s["ctx_series"]) // 6)]
        print("     context over the run: " + " -> ".join(f"{t} {c // 1000}k" for t, c in steps))


if __name__ == "__main__":
    main()
