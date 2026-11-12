# Computer Fault Diagnosis Expert System

A symbolic, rule-based PC Fault Diagnosis Expert System built with Python and Streamlit[cite: 6]. Users can describe a computer issue in plain English, answer goal-driven follow-up questions, and receive a ranked diagnosis with recommended remediation steps and full explainability[cite: 2, 3, 4, 6].

> **Live Demo:** _[Add your Streamlit Community Cloud URL here after deploying]_

## Core AI & Architecture Features
* **Forward-Chaining Inference (`engine.py`):** Evaluates 138 `IF-THEN` production rules with conflict resolution (`priority > specificity > effective confidence`) and MYCIN-style certainty factor combination[cite: 4, 6].
* **Open-World Evaluation (`engine.py`, `knowledge.py`):** Distinguishes confirmed symptoms (`True`/`False`), explicit `"Don't know"` answers (`None`), and unasked baseline assumptions (`NORMAL_STATE`) with automatic certainty discounting[cite: 2, 4, 5].
* **Explainable AI (XAI):** Provides deterministic **WHY** (rules that fired), **HOW** (recursive derivation trees showing intermediate facts), **WHY NOT** (closest unfired rules and missing conditions), and **Near Misses**[cite: 2, 4].
* **Goal-Driven Dialogue Manager (`dialogue.py`):** Extracts initial facts via regex with clause-level negation detection and dynamically scores the most informative next question[cite: 3].
* **Decision Support (`engine.py`):** Ranks confirmed faults by `Severity × Confidence` and breaks ties using a least-invasive-first remediation ladder[cite: 4].

## Project Structure
| File | Purpose |
| :--- | :--- |
| `app.py` | 5-page Streamlit web interface (*Consultation, Diagnosis, Explanation, Knowledge Base, Report*)[cite: 2, 6] |
| `engine.py` | Forward-chaining inference engine, certainty factor math, decision ranking, and explanation generator[cite: 4, 6] |
| `knowledge.py` | Knowledge base containing 138 rules, 95 symptom fields, baseline states, and 12 sample scenarios[cite: 5, 6] |
| `dialogue.py` | Regex symptom parser (with negation handling) and heuristic question selector[cite: 3, 6] |
| `test_system.py` | Automated test suite covering all 12 sample scenarios, extended rules, negation, and headless UI flow[cite: 6, 8] |
| `.streamlit/config.toml` | Streamlit theme configuration[cite: 1, 6] |

## Local Setup & Testing
```bash
pip install -r requirements.txt
python test_system.py
streamlit run app.py
```[cite: 6]

## Deploying to Streamlit Community Cloud
1. Push this repository (including `.streamlit/config.toml`[cite: 1, 6]) to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repository, branch, and set **Main file path** to `app.py`[cite: 2].
4. Click **Deploy**.