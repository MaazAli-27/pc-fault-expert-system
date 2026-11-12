import streamlit as st
from engine import run, decide, why, how, why_not, report, label, SEV, near_misses
from knowledge import RULES, FIELDS, SAMPLES, NORMAL_STATE
from dialogue import parse, next_question, FIELD, MAX_Q

st.set_page_config(page_title="PC Fault Diagnosis Expert System", page_icon=":material/computer:", layout="wide")
st.markdown("""<style>
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css");
.bi{margin-right:7px;vertical-align:-2px}
#MainMenu,footer{visibility:hidden}
header[data-testid=stHeader]{background:transparent}
.stApp{background:#f4f6fb;color:#0f172a}.block-container{padding-top:4rem;max-width:1150px}
[data-testid=stBaseButton-primary],button[kind=primary]{background:#2563eb!important;border-color:#2563eb!important;color:#fff!important}
[data-testid=stBaseButton-primary]:hover,button[kind=primary]:hover{background:#1d4ed8!important;border-color:#1d4ed8!important}
[data-testid=stBaseButton-primary]:disabled,button[kind=primary]:disabled{background:#93b4f5!important;border-color:#93b4f5!important}
[data-testid=stBaseButton-secondary],button[kind=secondary]{background:#fff!important;border:1px solid #cbd5e1!important;color:#0f172a!important}
[data-testid=stSidebar] [data-testid=stBaseButton-secondary],[data-testid=stSidebar] button[kind=secondary]{background:#1e293b!important;border:1px solid #475569!important;color:#e2e8f0!important}
[data-testid=stSidebar] button *{color:#e2e8f0!important}
span[data-baseweb=tag]{background:#2563eb!important;color:#fff!important}
[data-testid=stProgress] [role=progressbar]>div>div{background:#2563eb!important}
[data-testid=stSidebar]{background:#0f172a}[data-testid=stSidebar] *{color:#e2e8f0}
[data-testid=stSidebar] [data-testid=stMetricValue]{color:#fff}
[data-testid=stSidebar] hr{border-color:#334155}
.title{display:flex;align-items:center;gap:14px;margin-bottom:4px}
.title .ico{width:46px;height:46px;border-radius:12px;background:linear-gradient(135deg,#1d4ed8,#0ea5e9);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.4rem}
.title h1{font-size:1.6rem;margin:0;padding:0;color:#0f172a}.sub{color:#64748b;margin:0 0 18px 60px;margin-top:-4px}
.steps{display:flex;gap:8px;margin:4px 0 20px}
.step{flex:1;text-align:center;padding:10px;border-radius:10px;font-weight:600;background:#e8ecf4;color:#64748b;font-size:.92rem}
.step.on{background:#2563eb;color:#fff;box-shadow:0 4px 12px rgba(37,99,235,.35)}.step.ok{background:#dcfce7;color:#166534}
.card{background:#fff;border-radius:14px;padding:16px 20px;margin:10px 0;border:1px solid #e2e8f0;border-left:6px solid var(--c);box-shadow:0 1px 3px rgba(15,23,42,.06)}
.card h3{margin:0 0 8px;font-size:1.12rem;color:#0f172a}.card p{margin:10px 0 0;color:#334155}
.badge{display:inline-block;padding:3px 11px;border-radius:999px;font-size:.76rem;font-weight:600;color:#fff;background:var(--c);margin-right:6px}
.bar{height:8px;border-radius:6px;background:#e2e8f0;margin:10px 0 4px}.bar>div{height:8px;border-radius:6px;background:var(--c)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:6px 0 14px}
.kpi{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:14px 18px;box-shadow:0 1px 3px rgba(15,23,42,.06)}
.kpi small{color:#64748b;font-weight:600;text-transform:uppercase;font-size:.7rem;letter-spacing:.04em}.kpi div{font-size:1.5rem;font-weight:700;color:#0f172a}
.q{font-size:1.3rem;font-weight:700;color:#0f172a;margin:6px 0 10px}.area{color:#2563eb;font-weight:700;font-size:.8rem;letter-spacing:.06em}
.tl{display:flex;gap:12px;align-items:flex-start;padding:8px 0;border-bottom:1px solid #eef1f6}
.dot{min-width:28px;height:28px;border-radius:50%;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700}
.sec{font-weight:700;font-size:1.05rem;margin:18px 0 6px;color:#0f172a}
</style>""", unsafe_allow_html=True)

ss = st.session_state
for k, v in {"stage": "describe", "known": {}, "asked": [], "focus": [], "hits": []}.items():
    ss.setdefault(k, v)
bi = lambda n: f'<i class="bi bi-{n}"></i>'
CAT_ICON = {"Power & Boot": "power", "RAM": "memory", "CPU & Thermal": "cpu", "Storage": "device-hdd", "Display": "display",
            "Network": "wifi", "Operating System": "windows", "Security": "shield-lock", "Software & Peripherals": "keyboard"}
SEV_ICON = {4: "exclamation-octagon-fill", 3: "exclamation-triangle-fill", 2: "exclamation-circle-fill", 1: "check-circle-fill"}
ACT_ICON = {"Replace": "arrow-left-right", "Repair": "wrench-adjustable", "Update": "cloud-arrow-down", "Clean": "brush",
            "Scan": "bug", "Reinstall": "arrow-clockwise", "Upgrade": "graph-up-arrow", "Further Test": "search"}
COL = {4: "#dc2626", 3: "#ea580c", 2: "#d97706", 1: "#16a34a"}
N_PROB = len({r.concl for r in RULES if r.concl.startswith("fault:")})

def start():
    found, hits = parse(ss.get("issue_text", ""))
    ss.known, ss.hits, ss.asked, ss.focus, ss.stage = found, hits, [], ss.get("focus_sel", []), "interview"
def load_sample(n):
    ss.known, ss.hits, ss.asked, ss.focus, ss.stage = dict(SAMPLES[n]), ["Sample: " + n], [], [], "interview"
def answer(k):
    v = ss[f"ans_{k}"]
    ss.known[k] = None if v == "Don't know" else {"Yes": True, "No": False}.get(v, v)
    ss.asked.append(k)
def reset():
    ss.stage, ss.known, ss.asked, ss.hits = "describe", {}, [], []

done = ss.stage == "done"
if done:
    wm, trace = run(RULES, ss.known, normal_state=NORMAL_STATE)
    faults = decide(wm, trace)

def title(icon, text, sub):
    st.markdown(f'<div class="title"><div class="ico">{bi(icon)}</div><h1>{text}</h1></div><p class="sub">{sub}</p>', unsafe_allow_html=True)
def gate():
    if not done:
        st.info("Complete the consultation first.", icon=":material/info:")
        if st.button("Go to Consultation", type="primary"): st.switch_page(pages[0])
    return done
def kpis(items):
    st.markdown('<div class="kpis">' + "".join(f'<div class="kpi"><small>{a}</small><div>{b}</div></div>' for a, b in items) + '</div>', unsafe_allow_html=True)
def card(f, primary=False):
    c = COL[f["sev"]]
    st.markdown(f'<div class="card" style="--c:{c}"><h3>{bi("star-fill") if primary else bi(SEV_ICON[f["sev"]])}{f["name"]}</h3>'
                f'<span class="badge">{SEV[f["sev"]]}</span><span class="badge" style="--c:#475569">{bi(ACT_ICON.get(f["atype"], "tools"))}{f["atype"]}</span>'
                f'<span class="badge" style="--c:#475569">Cost: {f["cost"]}</span><div class="bar"><div style="width:{min(f["cf"], 1)*100:.0f}%"></div></div>'
                f'<small style="color:#64748b">Confidence {f["cf"]:.0%}</small><p>{bi("tools")}{f["action"]}</p></div>', unsafe_allow_html=True)

def p_consult():
    title("chat-square-text", "Consultation", "Describe the problem, answer a few expert questions, then review the diagnosis.")
    cur = {"describe": 0, "interview": 1, "done": 2}[ss.stage]
    st.markdown('<div class="steps">' + "".join(
        f'<div class="step {"ok" if i < cur else "on" if i == cur else ""}">{bi("check-lg") if i < cur else bi(ic)}{t}</div>'
        for i, (t, ic) in enumerate([("Describe", "pencil-square"), ("Answer questions", "question-circle"), ("Diagnosis", "heart-pulse")])) + '</div>', unsafe_allow_html=True)
    if ss.stage == "describe":
        with st.container(border=True):
            st.text_area("What problem are you facing?", key="issue_text", height=110, placeholder="e.g. My PC shuts down randomly and gets very hot")
            st.multiselect("Where does it seem to happen? (optional)", list(dict.fromkeys(f[0] for f in FIELDS)), key="focus_sel", placeholder="Pick one or two areas")
            st.button("Start consultation", on_click=start, type="primary", icon=":material/play_arrow:")
        with st.expander("Try a demo scenario"):
            c = st.columns(2)
            for i, n in enumerate(SAMPLES): c[i % 2].button(n, on_click=load_sample, args=(n,), key="s" + n)
    elif ss.stage == "interview":
        if ss.hits: st.info("Understood: " + ", ".join(ss.hits), icon=":material/check_circle:")
        elif not ss.focus: st.warning("No symptoms recognised in your text, so I'll start with general questions.", icon=":material/help:")
        nq = next_question(ss.known, ss.asked, ss.focus)
        if nq is None:
            ss.stage = "done"; st.rerun()
        k, reason = nq; g, lab, opts = FIELD[k]
        st.progress(len(ss.asked) / MAX_Q, text=f"Question {len(ss.asked) + 1} of at most {MAX_Q}")
        with st.container(border=True):
            st.markdown(f'<div class="area">{bi(CAT_ICON.get(g, "gear"))}{g.upper()}</div><div class="q">{lab}?</div>', unsafe_allow_html=True)
            if opts: st.selectbox("Choose", opts + ["Don't know"], index=None, key=f"ans_{k}", label_visibility="collapsed")
            else: st.radio("Answer", ["Yes", "No", "Don't know"], index=None, key=f"ans_{k}", horizontal=True, label_visibility="collapsed")
            st.markdown(f'<small style="color:#64748b">{bi("lightbulb")}Why I am asking: {reason}</small>', unsafe_allow_html=True)
            c1, c2, _ = st.columns([1, 1.4, 2])
            c1.button("Next", on_click=answer, args=(k,), disabled=ss.get(f"ans_{k}") is None, type="primary", icon=":material/arrow_forward:")
            c2.button("Finish & diagnose", on_click=lambda: ss.update(stage="done"), icon=":material/flag:")
        if ss.asked:
            with st.expander(f"Your answers so far ({len(ss.asked)})"):
                for q in ss.asked:
                    a = ss.known.get(q)
                    a = "Don't know" if a is None else ("Yes" if a is True else "No" if a is False else a)
                    st.write(f"• {FIELD[q][1]} → **{a}**")
    else:
        st.success("Consultation complete.", icon=":material/check_circle:")
        c1, c2, _ = st.columns([1.3, 1.5, 2])
        if c1.button("View diagnosis", type="primary", icon=":material/stethoscope:"): st.switch_page(pages[1])
        c2.button("New consultation", on_click=reset, icon=":material/refresh:")
        with st.expander("Facts collected"):
            st.dataframe([{"Fact": label(k), "Value": "Don't know" if v is None else str(v)} for k, v in ss.known.items()], hide_index=True)

def p_diag():
    title("heart-pulse", "Diagnosis", "Ranked faults with severity, confidence and recommended actions.")
    if not gate(): return
    if not faults:
        st.warning("No fault could be confirmed with the information given.", icon=":material/help:")
        for sc_, r, miss in near_misses(RULES, wm):
            st.markdown(f"- **{label(r.concl)}** ({sc_:.0%} match) – still needed: " + "; ".join(f"{label(k)} = {v}" for k, v, _ in miss))
        st.info("Try a more specific description, pick the problem areas, or answer Yes/No instead of 'Don't know'.")
        return
    kpis([("Faults found", len(faults)), ("Top severity", SEV[max(f["sev"] for f in faults)]),
          ("Best confidence", f"{max(f['cf'] for f in faults):.0%}"), ("Primary action", faults[0]["atype"])])
    if any(f["urgent"] for f in faults):
        st.error("Critical issue: " + ", ".join(f["name"] for f in faults if f["urgent"]) + ". Back up important data before anything else.", icon=":material/warning:")
    st.markdown('<div class="sec">Primary recommendation</div>', unsafe_allow_html=True); card(faults[0], True)
    if len(faults) > 1:
        st.markdown('<div class="sec">Other possible faults</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, f in enumerate(faults[1:]):
            with cols[i % 2]: card(f)

def p_explain():
    title("lightbulb", "Explanation", "Why each diagnosis was made, how it was derived, and why other faults were not.")
    if not gate(): return
    if faults:
        pick = st.selectbox("Diagnosis to explain", [f["id"] for f in faults], format_func=label)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="sec">{bi("question-circle")}WHY was this diagnosed?</div>', unsafe_allow_html=True)
            for line in why(pick, trace): st.markdown("- " + line)
        with c2:
            st.markdown(f'<div class="sec">{bi("diagram-3")}HOW was it derived?</div>', unsafe_allow_html=True)
            st.code("\n".join(how(pick, trace)), language=None)
    st.markdown(f'<div class="sec">{bi("slash-circle")}WHY NOT…?</div>', unsafe_allow_html=True)
    ask = st.selectbox("Check another fault", sorted({r.concl for r in RULES if r.concl.startswith("fault:")}), format_func=label)
    st.write("It *was* diagnosed (see the Diagnosis page)." if ask in wm else why_not(ask, RULES, wm))
    st.markdown(f'<div class="sec">{bi("list-ol")}Rule-firing timeline ({len(trace)} rules)</div>', unsafe_allow_html=True)
    st.markdown("".join(
        f'<div class="tl"><div class="dot">{t["step"]}</div><div><b>{t["rule"].id}</b> · {t["rule"].text()}<br>'
        f'<small style="color:#64748b">Confidence {t["cf"]:.2f}'
        f'{" · Assumed baseline: " + ", ".join(label(k) for k in t["assumed"]) if t.get("assumed") else ""}</small></div></div>'
        for t in trace), unsafe_allow_html=True)

def p_kb():
    title("book", "Knowledge Base", "Browse and search every IF-THEN rule used by the inference engine.")
    kpis([("Rules", len(RULES)), ("Questions", len(FIELDS)), ("Problems covered", N_PROB), ("Categories", len({r.cat for r in RULES}))])
    c1, c2 = st.columns([2, 1])
    cat = c1.multiselect("Filter by category", sorted({r.cat for r in RULES})); q = c2.text_input("Search rules", icon=":material/search:")
    rows = [{"ID": r.id, "Category": r.cat, "Rule": r.text(), "CF": r.cf, "Priority": r.prio}
            for r in RULES if (not cat or r.cat in cat) and q.lower() in r.text().lower()]
    st.caption(f"Showing {len(rows)} of {len(RULES)} rules"); st.dataframe(rows, hide_index=True, height=480)

def p_report():
    title("file-earmark-text", "Report", "Download the diagnosis and the rules that produced it.")
    if not gate(): return
    txt = report(faults, trace)
    with st.container(border=True): st.code(txt, language=None)
    st.download_button("Download report (.txt)", txt, "diagnosis_report.txt", type="primary", icon=":material/download:")

pages = [st.Page(p_consult, title="Consultation", icon=":material/forum:", default=True),
         st.Page(p_diag, title="Diagnosis", icon=":material/stethoscope:"),
         st.Page(p_explain, title="Explanation", icon=":material/lightbulb:"),
         st.Page(p_kb, title="Knowledge Base", icon=":material/menu_book:"),
         st.Page(p_report, title="Report", icon=":material/description:")]
nav = st.navigation(pages)
with st.sidebar:
    a, b = st.columns(2); a.metric("Rules", len(RULES)); b.metric("Questions", len(FIELDS))
    st.metric("Problems covered", N_PROB)
    st.divider(); st.caption("Forward-chaining inference · Certainty factors · WHY / HOW / WHY NOT explanations")
    st.button("New consultation", on_click=reset, icon=":material/refresh:")
nav.run()