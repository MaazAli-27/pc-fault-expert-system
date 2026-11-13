import html
import streamlit as st
from engine import run, decide, why, how, why_not, report, label, SEV, near_misses
from knowledge import RULES, FIELDS, SAMPLES, NORMAL_STATE
from dialogue import parse, next_question, FIELD, MAX_Q

st.set_page_config(
    page_title="PC Fault Diagnosis Expert System",
    page_icon=":material/computer:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""<style>
@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap");
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css");

:root {
    --bg-canvas: #F8FAFC;
    --surface-light: rgba(255, 255, 255, 0.94);
    --surface-dark: #0B1120;
    --surface-dark-elevated: #111827;
    --border-light: #E2E8F0;
    --border-dark: #1E293B;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --text-muted: #64748B;
    --accent-blue: #2563EB;
    --accent-cyan: #38BDF8;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.bi { margin-right: 7px; vertical-align: -1px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.75);
    backdrop-filter: blur(12px);
}

.stApp {
    background: radial-gradient(circle at 85% 0%, #E0F2FE 0%, #F8FAFC 42%, #F1F5F9 100%);
    color: var(--text-primary);
}

.block-container {
    padding-top: 3.2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

/* Primary & Secondary Buttons */
[data-testid="stBaseButton-primary"], button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: 1px solid #1D4ED8 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28) !important;
    transition: all 0.18s ease !important;
}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.38) !important;
}
[data-testid="stBaseButton-primary"]:disabled, button[kind="primary"]:disabled {
    background: #94A3B8 !important;
    border-color: #94A3B8 !important;
    box-shadow: none !important;
}
[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #0F172A !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover {
    border-color: #2563EB !important;
    color: #2563EB !important;
    background: #F8FAFC !important;
}

/* Dark Obsidian Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1120 0%, #0F172A 100%);
    border-right: 1px solid #1E293B;
}
[data-testid="stSidebar"] * { color: #E2E8F0; }
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.55);
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 10px 12px;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.35rem !important;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
[data-testid="stSidebar"] button[kind="secondary"] {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
    color: #F8FAFC !important;
    width: 100%;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
    border-color: #38BDF8 !important;
    background: #26354D !important;
}
[data-testid="stSidebar"] hr { border-color: #1E293B; }

/* Tags & Progress Bar */
span[data-baseweb="tag"] {
    background: #1E293B !important;
    color: #F8FAFC !important;
    border-radius: 6px !important;
}
[data-testid="stProgress"] [role="progressbar"] > div > div {
    background: linear-gradient(90deg, #2563EB, #0EA5E9) !important;
}

/* Dark Hero Header Banner */
.hero-banner {
    background: linear-gradient(135deg, #0B1120 0%, #162033 60%, #1E293B 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 18px;
    padding: 1.5rem 1.85rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 18px 32px -12px rgba(11, 17, 32, 0.22);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.hero-left { display: flex; align-items: center; gap: 16px; }
.hero-ico {
    width: 50px; height: 50px; border-radius: 14px;
    background: linear-gradient(135deg, #2563EB, #0EA5E9);
    color: #FFFFFF; display: flex; align-items: center; justify-content: center;
    font-size: 1.45rem;
    box-shadow: 0 8px 18px rgba(14, 165, 233, 0.35);
    flex-shrink: 0;
}
.hero-banner h1 {
    font-size: 1.55rem; font-weight: 800; margin: 0; padding: 0;
    color: #FFFFFF; letter-spacing: -0.02em;
}
.hero-banner p {
    margin: 4px 0 0 0; color: #94A3B8; font-size: 0.92rem;
}
.hero-pill {
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38BDF8;
    padding: 6px 14px;
    border-radius: 999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    white-space: nowrap;
}

/* Stepper Bar */
.steps {
    display: flex; gap: 10px; margin: 0 0 1.4rem 0;
    background: #FFFFFF; padding: 8px; border-radius: 14px;
    border: 1px solid var(--border-light);
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
}
.step {
    flex: 1; text-align: center; padding: 10px 12px; border-radius: 10px;
    font-weight: 600; background: transparent; color: #64748B; font-size: 0.9rem;
    transition: all 0.2s ease;
}
.step.on {
    background: #0F172A; color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.2);
}
.step.ok {
    background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0;
}

/* Light Glassmorphic Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface-light) !important;
    backdrop-filter: blur(10px);
    border: 1px solid var(--border-light) !important;
    border-radius: 16px !important;
    padding: 0.4rem 0.6rem !important;
    box-shadow: 0 8px 24px -8px rgba(15, 23, 42, 0.06) !important;
}

/* Fault Diagnosis Cards */
.card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.35rem 1.55rem;
    margin: 12px 0;
    border: 1px solid #E2E8F0;
    border-left: 6px solid var(--c);
    box-shadow: 0 6px 20px -6px rgba(15, 23, 42, 0.07);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 26px -8px rgba(15, 23, 42, 0.11);
}
.card h3 {
    margin: 0 0 10px 0; font-size: 1.15rem; font-weight: 700; color: #0F172A;
}
.card p { margin: 12px 0 0 0; color: #334155; line-height: 1.55; }
.badge {
    display: inline-flex; align-items: center; padding: 4px 12px;
    border-radius: 999px; font-size: 0.75rem; font-weight: 700;
    color: #FFFFFF; background: var(--c); margin-right: 6px; letter-spacing: 0.02em;
}
.badge-neutral {
    display: inline-flex; align-items: center; padding: 4px 12px;
    border-radius: 999px; font-size: 0.75rem; font-weight: 600;
    color: #1E293B; background: #F1F5F9; border: 1px solid #CBD5E1; margin-right: 6px;
}
.bar { height: 8px; border-radius: 999px; background: #E2E8F0; margin: 12px 0 5px; overflow: hidden; }
.bar > div { height: 8px; border-radius: 999px; background: var(--c); }
.why-box {
    margin-top: 12px; padding: 10px 14px; border-radius: 10px;
    background: #F8FAFC; border: 1px solid #E2E8F0;
    font-size: 0.87rem; color: #475569; line-height: 1.5;
}

/* KPI Strip (Dark Accent + Crisp Light Cards) */
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 8px 0 18px; }
@media (max-width: 768px) { .kpis { grid-template-columns: repeat(2, 1fr); } }
.kpi {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px;
    padding: 15px 18px; box-shadow: 0 4px 12px -4px rgba(15, 23, 42, 0.05);
}
.kpi.dark {
    background: #0F172A; border-color: #1E293B;
}
.kpi small {
    color: #64748B; font-weight: 700; text-transform: uppercase;
    font-size: 0.7rem; letter-spacing: 0.06em; display: block; margin-bottom: 4px;
}
.kpi.dark small { color: #94A3B8; }
.kpi div { font-size: 1.5rem; font-weight: 800; color: #0F172A; }
.kpi.dark div { color: #38BDF8; }

/* Interview Question Typography */
.q { font-size: 1.32rem; font-weight: 700; color: #0F172A; margin: 8px 0 12px; line-height: 1.35; }
.area {
    display: inline-block; background: #EFF6FF; color: #1D4ED8;
    border: 1px solid #BFDBFE; padding: 4px 11px; border-radius: 999px;
    font-weight: 700; font-size: 0.74rem; letter-spacing: 0.06em;
}
.reason-pill {
    margin-top: 10px; padding: 9px 13px; border-radius: 10px;
    background: #F8FAFC; border-left: 3px solid #2563EB;
    color: #475569; font-size: 0.85rem;
}

/* Dark Terminal Console (HOW Tree & Report) */
.dark-console {
    background: #0B1120;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 1.15rem 1.35rem;
    color: #E2E8F0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.83rem;
    line-height: 1.65;
    white-space: pre-wrap;
    overflow-x: auto;
    box-shadow: 0 12px 24px -8px rgba(11, 17, 32, 0.25);
}
.dark-console-bar {
    display: flex; align-items: center; gap: 6px;
    padding-bottom: 10px; margin-bottom: 10px;
    border-bottom: 1px solid #1E293B; color: #94A3B8; font-size: 0.75rem;
}
.mac-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

/* Rule Firing Timeline */
.tl {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 12px 14px; margin-bottom: 8px;
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
}
.dot {
    min-width: 30px; height: 30px; border-radius: 10px;
    background: #0F172A; color: #38BDF8;
    font-family: 'JetBrains Mono', monospace;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700;
}
.sec {
    font-weight: 800; font-size: 1.05rem; margin: 20px 0 8px;
    color: #0F172A; letter-spacing: -0.01em;
}
</style>""", unsafe_allow_html=True)

ss = st.session_state
for k, v in {"stage": "describe", "known": {}, "asked": [], "focus": [], "hits": []}.items():
    ss.setdefault(k, v)

bi = lambda n: f'<i class="bi bi-{n}"></i>'
CAT_ICON = {
    "Power & Boot": "power", "RAM": "memory", "CPU & Thermal": "cpu", "Storage": "device-hdd",
    "Display": "display", "Network": "wifi", "Operating System": "windows",
    "Security": "shield-lock", "Software & Peripherals": "keyboard",
}
SEV_ICON = {4: "exclamation-octagon-fill", 3: "exclamation-triangle-fill", 2: "exclamation-circle-fill", 1: "check-circle-fill"}
ACT_ICON = {
    "Replace": "arrow-left-right", "Repair": "wrench-adjustable", "Update": "cloud-arrow-down",
    "Clean": "brush", "Scan": "bug", "Reinstall": "arrow-clockwise", "Upgrade": "graph-up-arrow", "Further Test": "search",
}
COL = {4: "#DC2626", 3: "#EA580C", 2: "#D97706", 1: "#059669"}
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


def title(icon, text, sub, pill="FORWARD-CHAINING ENGINE"):
    st.markdown(
        f'<div class="hero-banner">'
        f'<div class="hero-left"><div class="hero-ico">{bi(icon)}</div>'
        f'<div><h1>{text}</h1><p>{sub}</p></div></div>'
        f'<div class="hero-pill">● {pill}</div></div>',
        unsafe_allow_html=True,
    )


def gate():
    if not done:
        st.info("Complete the consultation first to unlock diagnostic telemetry.", icon=":material/info:")
        if st.button("Go to Consultation", type="primary"):
            st.switch_page(pages[0])
    return done


def kpis(items, dark_first=True):
    st.markdown(
        '<div class="kpis">'
        + "".join(
            f'<div class="kpi {"dark" if (dark_first and idx == 0) else ""}"><small>{a}</small><div>{b}</div></div>'
            for idx, (a, b) in enumerate(items)
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def dark_terminal(header_label, body_text):
    escaped = html.escape(body_text)
    st.markdown(
        f'<div class="dark-console">'
        f'<div class="dark-console-bar">'
        f'<span class="mac-dot" style="background:#EF4444"></span>'
        f'<span class="mac-dot" style="background:#F59E0B"></span>'
        f'<span class="mac-dot" style="background:#10B981"></span>'
        f'<span style="margin-left:6px">{html.escape(header_label)}</span></div>'
        f'{escaped}</div>',
        unsafe_allow_html=True,
    )


def card(f, primary=False):
    c = COL[f["sev"]]
    st.markdown(
        f'<div class="card" style="--c:{c}">'
        f'<h3>{bi("star-fill") if primary else bi(SEV_ICON[f["sev"]])}{f["name"]}</h3>'
        f'<span class="badge">{SEV[f["sev"]]}</span>'
        f'<span class="badge-neutral">{bi(ACT_ICON.get(f["atype"], "tools"))}{f["atype"]}</span>'
        f'<span class="badge-neutral">{bi("tag")}Est. Cost: {f["cost"]}</span>'
        f'<div class="bar"><div style="width:{min(f["cf"], 1) * 100:.0f}%"></div></div>'
        f'<small style="color:#64748B;font-weight:600">Diagnostic Confidence: {f["cf"]:.0%}</small>'
        f'<p>{bi("tools")}<b>Recommended Action:</b> {f["action"]}</p>'
        f'<div class="why-box">{bi("info-circle")}<b>Decision Rationale:</b> {f["why_action"]}</div></div>',
        unsafe_allow_html=True,
    )


def p_consult():
    stage_pill = {"describe": "STEP 1 · INTAKE", "interview": "STEP 2 · TRIAGE", "done": "STEP 3 · COMPLETE"}[ss.stage]
    title(
        "cpu-fill",
        "PC Fault Diagnosis Expert System",
        "Describe your symptoms in plain English, answer targeted triage questions, and review deterministic XAI results.",
        pill=stage_pill,
    )
    cur = {"describe": 0, "interview": 1, "done": 2}[ss.stage]
    st.markdown(
        '<div class="steps">'
        + "".join(
            f'<div class="step {"ok" if i < cur else "on" if i == cur else ""}">'
            f'{bi("check-circle-fill") if i < cur else bi(ic)}{t}</div>'
            for i, (t, ic) in enumerate(
                [("1. Describe Symptoms", "pencil-square"), ("2. Expert Triage", "question-circle"), ("3. Diagnosis Ready", "heart-pulse")]
            )
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    if ss.stage == "describe":
        with st.container(border=True):
            st.text_area(
                "What problem are you facing?",
                key="issue_text",
                height=115,
                placeholder="e.g. My PC shuts down randomly under load and the CPU gets very hot...",
            )
            st.multiselect(
                "Suspected subsystem area (optional)",
                list(dict.fromkeys(f[0] for f in FIELDS)),
                key="focus_sel",
                placeholder="Select one or more hardware/software domains",
            )
            st.button("Start consultation", on_click=start, type="primary", icon=":material/play_arrow:")

        with st.expander("Explore 12 preset diagnostic scenarios"):
            c = st.columns(2)
            for i, n in enumerate(SAMPLES):
                c[i % 2].button(n, on_click=load_sample, args=(n,), key="s" + n, use_container_width=True)

    elif ss.stage == "interview":
        if ss.hits:
            st.info("Extracted symptoms: " + ", ".join(ss.hits), icon=":material/check_circle:")
        elif not ss.focus:
            st.warning("No specific keywords detected in text — starting with broad system screening.", icon=":material/help:")

        nq = next_question(ss.known, ss.asked, ss.focus)
        if nq is None:
            ss.stage = "done"
            st.rerun()

        k, reason = nq
        g, lab, opts = FIELD[k]
        st.progress(len(ss.asked) / MAX_Q, text=f"Diagnostic Question {len(ss.asked) + 1} of max {MAX_Q}")

        with st.container(border=True):
            st.markdown(f'<div class="area">{bi(CAT_ICON.get(g, "gear"))}{g.upper()}</div><div class="q">{lab}?</div>', unsafe_allow_html=True)
            if opts:
                st.selectbox("Choose", opts + ["Don't know"], index=None, key=f"ans_{k}", label_visibility="collapsed")
            else:
                st.radio("Answer", ["Yes", "No", "Don't know"], index=None, key=f"ans_{k}", horizontal=True, label_visibility="collapsed")

            st.markdown(f'<div class="reason-pill">{bi("lightbulb")}<b>Inference rationale:</b> {reason}</div>', unsafe_allow_html=True)
            st.write("")
            c1, c2, _ = st.columns([1, 1.4, 2])
            c1.button("Next", on_click=answer, args=(k,), disabled=ss.get(f"ans_{k}") is None, type="primary", icon=":material/arrow_forward:")
            c2.button("Finish & diagnose", on_click=lambda: ss.update(stage="done"), icon=":material/flag:")

        if ss.asked:
            with st.expander(f"Recorded responses ({len(ss.asked)})"):
                for q in ss.asked:
                    a = ss.known.get(q)
                    a = "Don't know" if a is None else ("Yes" if a is True else "No" if a is False else a)
                    st.write(f"• {FIELD[q][1]} → **{a}**")

    else:
        st.success("Consultation complete. Inference engine has evaluated all matching production rules.", icon=":material/check_circle:")
        c1, c2, _ = st.columns([1.3, 1.5, 2])
        if c1.button("View diagnosis", type="primary", icon=":material/stethoscope:"):
            st.switch_page(pages[1])
        c2.button("New consultation", on_click=reset, icon=":material/refresh:")
        with st.expander("Working memory facts collected"):
            st.dataframe(
                [{"Fact": label(k), "Value": "Don't know" if v is None else str(v)} for k, v in ss.known.items()],
                hide_index=True,
                use_container_width=True,
            )


def p_diag():
    title("heart-pulse", "Diagnostic Assessment", "Ranked root-cause faults ordered by risk score (Severity × Certainty Factor).", pill="DECISION SUPPORT")
    if not gate():
        return
    if not faults:
        st.warning("No fault reached confirmation threshold with the current evidence.", icon=":material/help:")
        for sc_, r, miss in near_misses(RULES, wm):
            st.markdown(f"- **{label(r.concl)}** ({sc_:.0%} match) — missing: " + "; ".join(f"{label(k)} = {v}" for k, v, _ in miss))
        st.info("Provide a more specific symptom description or answer Yes/No instead of 'Don't know'.")
        return

    kpis(
        [
            ("Confirmed Faults", len(faults)),
            ("Peak Severity", SEV[max(f["sev"] for f in faults)]),
            ("Top Confidence", f"{max(f['cf'] for f in faults):.0%}"),
            ("Primary Action", faults[0]["atype"]),
        ]
    )
    if any(f["urgent"] for f in faults):
        st.error(
            "CRITICAL HARDWARE / DATA HAZARD: "
            + ", ".join(f["name"] for f in faults if f["urgent"])
            + ". Back up critical data immediately before attempting repairs.",
            icon=":material/warning:",
        )

    st.markdown('<div class="sec">Primary Root-Cause Recommendation</div>', unsafe_allow_html=True)
    card(faults[0], True)

    if len(faults) > 1:
        st.markdown('<div class="sec">Secondary & Contributing Faults</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, f in enumerate(faults[1:]):
            with cols[i % 2]:
                card(f)


def p_explain():
    title("lightbulb", "Explainable AI (XAI) Trace", "Inspect WHY rules fired, HOW intermediate facts chained, and WHY NOT alternative faults.", pill="XAI TELEMETRY")
    if not gate():
        return
    if faults:
        pick = st.selectbox("Select diagnosed fault to inspect", [f["id"] for f in faults], format_func=label)
        c1, c2 = st.columns([1.05, 1.15], gap="large")
        with c1:
            st.markdown(f'<div class="sec">{bi("question-circle")}WHY was this diagnosed?</div>', unsafe_allow_html=True)
            with st.container(border=True):
                for line in why(pick, trace):
                    st.markdown("- " + line)
            st.markdown(f'<div class="sec">{bi("wrench-adjustable")}WHY this intervention?</div>', unsafe_allow_html=True)
            st.info(next(f["why_action"] for f in faults if f["id"] == pick), icon=":material/build:")
        with c2:
            st.markdown(f'<div class="sec">{bi("diagram-3")}HOW was it derived? (Inference Tree)</div>', unsafe_allow_html=True)
            dark_terminal("FORWARD-CHAINING DERIVATION TREE", "\n".join(how(pick, trace)))

    st.markdown(f'<div class="sec">{bi("slash-circle")}WHY NOT…? (Counterfactual Check)</div>', unsafe_allow_html=True)
    with st.container(border=True):
        ask = st.selectbox("Check why another fault did not fire", sorted({r.concl for r in RULES if r.concl.startswith("fault:")}), format_func=label)
        st.write("This fault *was* confirmed (see the Diagnosis page)." if ask in wm else why_not(ask, RULES, wm))

    st.markdown(f'<div class="sec">{bi("list-ol")}Rule-Firing Execution Timeline ({len(trace)} steps)</div>', unsafe_allow_html=True)
    st.markdown(
        "".join(
            f'<div class="tl"><div class="dot">{t["step"]}</div><div><b>{t["rule"].id}</b> · {t["rule"].text()}<br>'
            f'<small style="color:#64748B;font-family:\'JetBrains Mono\',monospace">CF {t["cf"]:.2f}'
            f'{" · Assumed baseline: " + ", ".join(label(k) for k in t["assumed"]) if t.get("assumed") else ""}</small></div></div>'
            for t in trace
        ),
        unsafe_allow_html=True,
    )


def p_kb():
    title("book", "Production Rule Knowledge Base", "Inspect and filter all IF-THEN production rules, certainty factors, and priority weights.", pill=f"{len(RULES)} RULES LOADED")
    kpis([("Total Rules", len(RULES)), ("Input Fields", len(FIELDS)), ("Fault Classes", N_PROB), ("Domains", len({r.cat for r in RULES}))])
    c1, c2 = st.columns([2, 1])
    cat = c1.multiselect("Filter by domain category", sorted({r.cat for r in RULES}))
    q = c2.text_input("Search rule conditions or conclusions", icon=":material/search:")
    rows = [
        {"ID": r.id, "Category": r.cat, "Rule": r.text(), "CF": r.cf, "Priority": r.prio}
        for r in RULES
        if (not cat or r.cat in cat) and q.lower() in r.text().lower()
    ]
    st.caption(f"Displaying {len(rows)} of {len(RULES)} production rules")
    st.dataframe(rows, hide_index=True, height=480, use_container_width=True)


def p_report():
    title("file-earmark-text", "Diagnostic Report Export", "Download a timestamp-ready plain-text audit of findings and fired rules.", pill="EXPORT READY")
    if not gate():
        return
    txt = report(faults, trace)
    dark_terminal("diagnosis_report.txt · AUDIT PREVIEW", txt)
    st.write("")
    st.download_button("Download report (.txt)", txt, "diagnosis_report.txt", type="primary", icon=":material/download:")


pages = [
    st.Page(p_consult, title="Consultation", icon=":material/forum:", default=True),
    st.Page(p_diag, title="Diagnosis", icon=":material/stethoscope:"),
    st.Page(p_explain, title="Explanation", icon=":material/lightbulb:"),
    st.Page(p_kb, title="Knowledge Base", icon=":material/menu_book:"),
    st.Page(p_report, title="Report", icon=":material/description:"),
]
nav = st.navigation(pages)

with st.sidebar:
    st.markdown("### ⚡ Fault Engine")
    st.caption("Symbolic Hardware & OS Diagnostics")
    st.divider()
    a, b = st.columns(2)
    a.metric("Rules", len(RULES))
    b.metric("Inputs", len(FIELDS))
    st.metric("Fault Classes", N_PROB)
    st.divider()
    st.caption("Forward-chaining · MYCIN Certainty Factors · WHY / HOW / WHY NOT XAI")
    st.button("New consultation", on_click=reset, icon=":material/refresh:")

nav.run()