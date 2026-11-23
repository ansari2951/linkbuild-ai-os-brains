
import sys
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.brain import CentralBrain

st.set_page_config(
    page_title="LINKBUILD AI OS",
    page_icon="🔗",
    layout="wide"
)

st.title("LINKBUILD AI OS")
st.caption("Central SEO & Link Building Automation Dashboard")

brain = CentralBrain()
summary = brain.get_system_summary()

st.subheader("System Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Agents", summary["total_agents"])
col2.metric("Available Agents", summary["available_agents"])
col3.metric("Missing Agents", summary["missing_agents"])

st.divider()

st.subheader("Agent Monitor")

for name, details in summary["agents"].items():
    status = "Available" if details["available"] else "Missing"

    with st.expander(f"{name.replace('_', ' ').title()} | {status}"):
        st.write(f"File: `{details['file']}`")
        st.write(f"Status: {status}")

st.divider()

st.subheader("Outreach Overview")

email_dir = (
    BASE_DIR / "data" / "private" / "email_extraction"
)

draft_file = email_dir / "outreach_drafts.csv"
personalized_file = email_dir / "personalized_outreach.csv"
approval_file = email_dir / "approval_decisions.csv"

def count_csv_records(path):
    if not path.exists():
        return 0

    try:
        import csv

        with open(
            path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:
            return sum(1 for _ in csv.DictReader(file))

    except (OSError, csv.Error):
        return 0


a, b, c = st.columns(3)

a.metric("Outreach Drafts", count_csv_records(draft_file))
b.metric("Personalized Drafts", count_csv_records(personalized_file))
c.metric("Approval Records", count_csv_records(approval_file))

st.divider()

st.subheader("Publisher & Client Data")

publisher_db = (
    BASE_DIR / "data" / "private" / "publisher_crm"
    / "publishers.db"
)

prospect_file = (
    BASE_DIR / "data" / "private" / "client_prospecting"
    / "client_prospects.csv"
)

publisher_count = 0

if publisher_db.exists():
    try:
        import sqlite3

        with sqlite3.connect(publisher_db) as conn:
            publisher_count = conn.execute(
                "SELECT COUNT(*) FROM publishers"
            ).fetchone()[0]

    except sqlite3.Error:
        publisher_count = 0

d, e = st.columns(2)

d.metric("Saved Publishers", publisher_count)
e.metric("Client Prospects", count_csv_records(prospect_file))

st.divider()

st.subheader("System Information")

st.write("Project:", "LINKBUILD AI OS Brains")
st.write("Architecture:", "Localhost")
st.write("Central Controller:", "CentralBrain")
st.write("Dashboard Status:", "Initial Version")

st.info(
    "This dashboard currently displays project status and stored records. "
    "Agent execution and workflow controls will be integrated in a later phase."
)

st.caption("LINKBUILD AI OS | Development Dashboard")
