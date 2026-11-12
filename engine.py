"""Core: Rule, forward-chaining inference, decision support, explanation facility."""
from dataclasses import dataclass

@dataclass
class Rule:
    id: str; cat: str; conds: dict; concl: str; cf: float; prio: int
    sev: int; atype: str; cost: str; action: str   # sev: 4=Critical..1=Low

    def text(self):
        c = " AND ".join(f"{label(k)} = {v}" for k, v in self.conds.items())
        return f"IF {c} THEN {label(self.concl)}"

SEV = {4: "Critical", 3: "High", 2: "Medium", 1: "Low", 0: "-"}
# least invasive first (used as tiebreaker)
INVASIVE = ["Further Test", "Clean", "Update", "Scan", "Repair", "Reinstall", "Upgrade", "Replace"]

def label(k):
    return k.split(":")[-1].replace("_", " ").capitalize()

def run(rules, facts, normal_state=None, strict=False):
    """Forward chaining with open-world handling.
    - Confirmed facts in `facts` have certainty 1.0.
    - Explicit `None` ('Don't know') blocks rules requiring that fact.
    - Unasked baseline conditions in `normal_state` (if strict=False) contribute reduced certainty (0.75).
    """
    wm = {k: (v, 1.0) for k, v in facts.items() if v is not None}
    explicit_unknowns = {k for k, v in facts.items() if v is None}
    done, trace = set(), []

    while True:
        agenda = []
        for r in rules:
            if r.id in done:
                continue
            possible = True
            cond_cfs = []
            assumed = []
            for k, v in r.conds.items():
                if k in wm:
                    if wm[k][0] == v:
                        cond_cfs.append(wm[k][1])
                    else:
                        possible = False
                        break
                elif (
                    not strict
                    and normal_state
                    and k not in explicit_unknowns
                    and k in normal_state
                    and normal_state[k] == v
                ):
                    cond_cfs.append(0.75)
                    assumed.append(k)
                else:
                    possible = False
                    break
            if possible and len(assumed) < len(r.conds):
                agenda.append((r, cond_cfs, assumed))

        if not agenda:
            break

        # conflict resolution: priority > specificity > effective confidence
        r, cond_cfs, assumed = min(
            agenda, key=lambda item: (-item[0].prio, -len(item[0].conds), -(item[0].cf * min(item[1])))
        )
        cf = r.cf * min(cond_cfs)
        old = wm.get(r.concl)
        new = cf if old is None else old[1] + cf * (1 - old[1])   # CF combination
        wm[r.concl] = (True, new)
        done.add(r.id)
        trace.append({
            "step": len(trace) + 1,
            "rule": r,
            "cf": cf,
            "matched": {k: wm[k][0] if k in wm else f"{normal_state[k]} (assumed)" for k in r.conds},
            "assumed": assumed,
        })
    return wm, trace

def decide(wm, trace):
    """Decision support: rank faults by severity x confidence."""
    out = []
    for k, (_, cf) in wm.items():
        if not k.startswith("fault:"):
            continue
        best_trace = max(
            (t for t in trace if t["rule"].concl == k),
            key=lambda t: (t["rule"].prio, t["cf"], len(t["rule"].conds), t["rule"].cf)
        )
        best = best_trace["rule"]
        out.append({
            "id": k,
            "name": label(k),
            "cf": cf,
            "sev": best.sev,
            "score": best.sev * cf,
            "atype": best.atype,
            "cost": best.cost,
            "action": best.action,
            "urgent": best.sev == 4,
        })
    out.sort(key=lambda f: (-f["score"], INVASIVE.index(f["atype"])))
    return out

def why(fault, trace):
    out = []
    for t in trace:
        if t["rule"].concl == fault:
            note = f" *(assumed: {', '.join(label(k) for k in t['assumed'])})*" if t.get("assumed") else ""
            out.append(f"**{t['rule'].id}** fired (CF {t['cf']:.2f}): {t['rule'].text()}{note}")
    return out

def how(fault, trace, d=0):
    out = []
    for t in trace:
        r = t["rule"]
        if r.concl != fault:
            continue
        out.append("    " * d + f"{label(fault)} ← {r.id} (CF {t['cf']:.2f})")
        for k, v in r.conds.items():
            if k.startswith(("fault:", "d:")):
                out += how(k, trace, d + 1)
            else:
                tag = " [assumed baseline]" if k in t.get("assumed", []) else ""
                out.append("    " * (d + 1) + f"• symptom: {label(k)} = {v}{tag}")
    return out

def why_not(fault, rules, wm):
    cands = [r for r in rules if r.concl == fault]
    if not cands:
        return "No rule in the knowledge base concludes this fault."
    def missing(r):
        return [(k, v, wm.get(k, ("unknown",))[0]) for k, v in r.conds.items()
                if k not in wm or wm[k][0] != v]
    r = min(cands, key=lambda r: len(missing(r)))
    m = "; ".join(f"{label(k)} should be {v} but is {a}" for k, v, a in missing(r))
    return f"Closest rule {r.id} did not fire because: {m}."

def report(faults, trace):
    L = ["COMPUTER FAULT DIAGNOSIS REPORT", "=" * 32]
    for i, f in enumerate(faults, 1):
        L += [f"{i}. {f['name']}  [{SEV[f['sev']]}, confidence {f['cf']:.0%}]",
              f"   Action ({f['atype']}, cost {f['cost']}): {f['action']}"]
    L += ["", "RULES FIRED:"]
    for t in trace:
        note = f" [assumed: {', '.join(t['assumed'])}]" if t.get("assumed") else ""
        L.append(f"  {t['step']}. {t['rule'].id}: {t['rule'].text()}{note}")
    return "\n".join(L)

def near_misses(rules, wm, n=3):
    """Closest fault rules that did not fire, judged by symptoms the user actually reported."""
    out = []
    for r in rules:
        if not r.concl.startswith("fault:") or r.concl in wm:
            continue
        pos = {k: v for k, v in r.conds.items() if (v is True or v in ("high", "failing", "hdd"))
               and k not in ("fans_spin", "post_ok", "bios_sees_drive", "fan_spinning", "other_devices_ok")}
        hit = [k for k, v in pos.items() if k in wm and wm[k][0] == v]
        miss = [(k, v, wm.get(k, ("not answered",))[0]) for k, v in r.conds.items()
                if k not in wm or wm[k][0] != v]
        if hit and miss:
            out.append((len(hit) / len(pos), r, miss))
    out.sort(key=lambda x: (-x[0], len(x[2])))
    return out[:n]