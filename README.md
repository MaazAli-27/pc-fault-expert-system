# Computer Fault Diagnosis Expert System

A symbolic, rule-based PC Fault Diagnosis Expert System built with Python and Streamlit. Users can describe computer problems in plain English, answer goal-driven follow-up questions, and receive a ranked diagnosis with recommended remediation steps and full explainability.

> **Live Demo:** [https://pc-fault-expert-system.streamlit.app/](https://pc-fault-expert-system.streamlit.app/)

## Core Expert System Capabilities

* **Inferencing (`engine.py`, `dialogue.py`):**
  * **Forward-Chaining Engine:** Evaluates 138 `IF-THEN` production rules with conflict resolution (`priority > specificity > effective confidence`) and multi-step intermediate fact derivation (`d:thermal_shutdown`, `d:thermal_throttling`, `d:cooling_failure`, `d:data_at_risk`).
  * **MYCIN-Style Certainty Factors & Open-World Logic:** Distinguishes confirmed symptoms (`True`/`False`), explicit `"Don't know"` responses (`None`), and unasked baseline assumptions (`NORMAL_STATE`) with automatic certainty discounting.
  * **Goal-Driven Dialogue Manager:** Parses natural-language problem descriptions with clause-level negation detection and dynamically selects the highest-information follow-up question.
* **Diagnosis (`app.py`, `knowledge.py`):**
  * Covers 95 diagnostic inputs across 10 hardware, OS, network, security, and peripheral domains, identifying specific root-cause faults alongside severity badges (`Critical`, `High`, `Medium`, `Low`), confidence scores, and near-miss candidates.
* **Decision Support (`engine.py`):**
  * Computes a risk-weighted priority score ($\text{Severity} \times \text{Confidence}$) for every confirmed fault and pairs each diagnosis with actionable repair steps, intervention categories (`Further Test`, `Clean`, `Update`, `Scan`, `Repair`, `Reinstall`, `Upgrade`, `Replace`), and estimated cost tiers (`Free`, `Low`, `Medium`, `High`).
  * Generates a downloadable plain-text diagnostic report containing ranked recommendations and the complete rule execution trace.
* **Decision Making & Explainability (`engine.py`, `app.py`):**
  * **Least-Invasive Tie-Breaking:** Automatically resolves equal-risk faults by favoring the least invasive intervention first before escalating to costly hardware replacements.
  * **Deterministic XAI:** Provides **WHY** (rules that fired), **HOW** (recursive derivation trees showing intermediate facts and baseline assumptions), and **WHY NOT** (closest unfired rules and missing conditions).

## Project Structure

| File | Description |
| :--- | :--- |
| `app.py` | 5-page Streamlit web interface (*Consultation, Diagnosis, Explanation, Knowledge Base, Report*) |
| `engine.py` | Forward-chaining inference engine, certainty factor math, decision ranking, and explanation generator |
| `knowledge.py` | Knowledge base containing 138 production rules, 95 symptom fields, baseline states, and 12 sample scenarios |
| `dialogue.py` | Regex symptom parser with clause-level negation handling and heuristic question selector |
| `test_system.py` | Automated test suite covering all 12 sample scenarios, extended rules, negation parsing, open-world logic, and headless UI consultation |
| `requirements.txt` | Python dependencies (`streamlit>=1.40`) |
| `.streamlit/config.toml` | Custom Streamlit theme configuration |

## Local Setup & Testing

```bash
git clone [https://github.com/MaazAli-27/pc-fault-expert-system.git](https://github.com/MaazAli-27/pc-fault-expert-system.git)
cd pc-fault-expert-system
pip install -r requirements.txt
python test_system.py
streamlit run app.py