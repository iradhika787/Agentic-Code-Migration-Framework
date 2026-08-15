from __future__ import annotations

from pathlib import Path

import streamlit as st

from orchestrator import Orchestrator


st.set_page_config(
    page_title="Python Migration Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(74, 222, 128, 0.12), transparent 32%),
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.12), transparent 28%),
            linear-gradient(180deg, #0b1020 0%, #0a0f1a 45%, #050814 100%);
        color: #e5e7eb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .hero {
        border: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(15, 23, 42, 0.72);
        backdrop-filter: blur(14px);
        border-radius: 24px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.25rem;
    }

    .hero h1 {
        font-size: 2.1rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.03em;
    }

    .hero p {
        color: #cbd5e1;
        margin-bottom: 0;
        line-height: 1.5;
    }

    .metric-card {
        border: 1px solid rgba(148, 163, 184, 0.18);
        background: rgba(15, 23, 42, 0.66);
        border-radius: 18px;
        padding: 1rem 1.1rem;
    }

    .section-card {
        border: 1px solid rgba(148, 163, 184, 0.15);
        background: rgba(15, 23, 42, 0.58);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1rem 1rem 0.85rem;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.01em;
        margin-bottom: 0.75rem;
        color: #f8fafc;
    }

    .small-label {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }

    .stTextArea textarea, .stTextInput input {
        background: rgba(2, 6, 23, 0.72) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 14px !important;
    }

    .stFileUploader {
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: rgba(2, 6, 23, 0.35);
        padding: 0.35rem;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #cbd5e1;
        background: transparent;
        padding: 0.55rem 0.8rem;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(37, 99, 235, 0.35) !important;
        color: #ffffff !important;
    }

    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.16);
        padding: 0.7rem 0.8rem;
        border-radius: 16px;
    }

    pre {
        border-radius: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource

def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def read_uploaded_file(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    return data.decode("utf-8")


def format_issues(issues: list[dict]) -> str:
    if not issues:
        return "No issues detected."
    lines = []
    for issue in issues:
        line = issue.get("line", "?")
        issue_type = issue.get("type", "issue")
        detail = issue.get("detail", "")
        lines.append(f"Line {line}: {issue_type} - {detail}")
    return "\n".join(lines)


def format_verification(report: dict | None) -> str:
    if not report:
        return "No verification report available."
    rows = []
    for key in ["syntax_valid", "compiles", "runs", "output_matches", "actual_output"]:
        if key in report:
            rows.append(f"{key}: {report.get(key)}")
    if report.get("errors"):
        rows.append("errors:")
        rows.extend(f"- {error}" for error in report["errors"])
    return "\n".join(rows)


def placeholder_code(text: str) -> str:
    return text if text.strip() else "# Upload a Python file to preview code here."


st.markdown(
    """
    <div class="hero">
        <h1>Python Migration Studio</h1>
        <p>Upload a Python 2 script, run the existing analysis → migration → verification workflow, and inspect the result.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Controls")
    uploaded_file = st.file_uploader("Upload Python file", type=["py"])
    expected_output = st.text_input("Expected output (optional)")
    run_button = st.button("Run Migration", type="primary", use_container_width=True)
    st.caption("The backend workflow is reused as-is through `Orchestrator`.")

if "source_code" not in st.session_state:
    st.session_state.source_code = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "file_name" not in st.session_state:
    st.session_state.file_name = "No file uploaded"

if uploaded_file is not None:
    st.session_state.source_code = read_uploaded_file(uploaded_file)
    st.session_state.file_name = uploaded_file.name

if run_button:
    if not st.session_state.source_code.strip():
        st.warning("Upload a Python file before running the migration.")
    else:
        orchestrator = get_orchestrator()
        progress = st.progress(0, text="Starting workflow...")
        with st.spinner("Running analysis, migration, and verification..."):
            progress.progress(20, text="Analyzing source code...")
            result = orchestrator.run(
                st.session_state.source_code,
                expected_output=expected_output or None,
            )
            progress.progress(100, text="Workflow complete")
        st.session_state.result = result

result = st.session_state.result
source_code = st.session_state.source_code
migrated_code = result["migrated_code"] if result else ""
issues = result["issues_found"] if result else []
verification_report = result["verification_report"] if result else None
execution_log = result["execution_log"] if result else []
diff_text = result["diff"] if result else ""
confidence_scores = result.get("confidence_scores", {}) if result else {}
confidence_decision = result.get("confidence_decision") if result else None

metrics = st.columns(4)
metrics[0].metric("File", st.session_state.file_name)
metrics[1].metric("Issues", len(issues))
metrics[2].metric("Attempts", result["attempts"] if result else "-")
metrics[3].metric("Status", "Success" if result and result["success"] else "Idle/Failed")

if result:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Execution Summary</div>', unsafe_allow_html=True)
    summary_cols = st.columns(3)
    summary_cols[0].write(f"**Decision:** {confidence_decision or 'n/a'}")
    summary_cols[1].write(f"**Confidence:** {confidence_scores}")
    summary_cols[2].write(f"**Verification:** {'passed' if verification_report and verification_report.get('runs') else 'pending'}")
    st.markdown('</div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Input → Output</div>', unsafe_allow_html=True)
    code_tabs = st.tabs(["Input", "Output", "Diff"])
    with code_tabs[0]:
        st.code(placeholder_code(source_code), language="python")
    with code_tabs[1]:
        st.code(placeholder_code(migrated_code), language="python")
    with code_tabs[2]:
        st.code(diff_text or "# Diff will appear after running migration.", language="diff")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Analysis</div>', unsafe_allow_html=True)
    st.text_area("Detected issues", value=format_issues(issues), height=220, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Verification</div>', unsafe_allow_html=True)
    if verification_report:
        st.text_area(
            "Verification report",
            value=format_verification(verification_report),
            height=240,
            label_visibility="collapsed",
        )
    else:
        st.info("Run the workflow to see syntax, compile, runtime, and output checks.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Logs Panel</div>', unsafe_allow_html=True)
    log_text = "\n".join(execution_log) if execution_log else "Workflow logs will appear here after execution."
    st.text_area("Execution log", value=log_text, height=320, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if result:
    if result["success"]:
        st.success("Migration completed successfully.")
    else:
        st.error("Migration completed with verification failures.")
