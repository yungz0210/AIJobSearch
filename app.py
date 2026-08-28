"""
AI Job Search & Career Acceleration Studio
Multi-Page Navigation Controller powered by Streamlit, Gemini 3.7 Flash, and Pydantic v2.

Modules:
1. 📄 Application Studio (Job Finder & 1-Click ATS 1-Page Resume & Cover Letter)
2. 📈 Market Radar & Skill Pulse (Live multi-board demand scanning & Plotly analytics)
3. 🎯 Employability & Upskilling (Pareto 80/20 gap diagnostic & budget-adaptive paths)
4. 🎙️ Tough Gap Interview Simulator (Interview drills addressing weak spots via STAR)
"""
import sys
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from src.views.studio_view import render_studio_view
from src.views.market_radar_view import render_market_radar_view
from src.views.employability_view import render_employability_view
from src.views.interview_view import render_interview_view

st.set_page_config(
    page_title="AI Job Search & Career Acceleration Studio",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Custom CSS for Premium Design & Micro-animations
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .score-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .score-val {
        font-size: 2.6rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .highlight-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        color: #334155;
    }
    .job-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .job-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.12);
        transform: translateY(-2px);
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.4rem;
    }
    .badge-linkedin { background-color: #0077b5; color: white; }
    .badge-indeed { background-color: #2164f3; color: white; }
    .badge-google { background-color: #ea4335; color: white; }
    .badge-loc { background-color: #f1f5f9; color: #475569; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initializes shared session state variables across all pages."""
    defaults = {
        "base_resume_text": "",
        "target_role_query": "Software Engineer",
        "target_location": "Kuala Lumpur, Malaysia",
        "search_results": [],
        "market_demand_report": None,
        "employability_roadmap": None,
        "selected_model": "gemini-3.6-flash",
        "custom_key": "",
        "max_retries": 1
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_sidebar():
    """Renders shared sidebar configurations and status."""
    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")
        model = st.selectbox(
            "Gemini Model",
            ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.7-flash"],
            index=0,
            key="sb_model"
        )
        st.session_state["selected_model"] = model

        key = st.text_input(
            "Custom API Key (optional)",
            type="password",
            value=st.session_state.get("custom_key", ""),
            help="Leave blank to use preloaded rotation keys.",
            key="sb_key"
        )
        st.session_state["custom_key"] = key

        retries = st.slider(
            "ATS Validation Refinement Loops",
            min_value=0,
            max_value=3,
            value=st.session_state.get("max_retries", 1),
            key="sb_retries"
        )
        st.session_state["max_retries"] = retries

        st.markdown("---")
        st.markdown("### 📊 Session Context")
        resume_len = len(st.session_state.get("base_resume_text", ""))
        st.caption(f"📄 **Resume:** {'Loaded (' + str(resume_len) + ' chars)' if resume_len > 0 else 'Not loaded'}")
        has_market = st.session_state.get("market_demand_report") is not None
        st.caption(f"📈 **Market Radar:** {'Active Report' if has_market else 'No scan yet'}")
        has_road = st.session_state.get("employability_roadmap") is not None
        st.caption(f"🎯 **Roadmap:** {'Generated' if has_road else 'Not started'}")

        st.markdown("---")
        st.markdown("### 🇲🇾 Target Hubs")
        st.markdown("""
        - **Malaysia Core:** Kuala Lumpur, Selangor, Cyberjaya, Penang, Johor Bahru
        - **Global:** Singapore, Remote, Worldwide
        - **Subsidies:** HRD Corp, MDEC, GLIC
        """)


def main():
    init_session_state()
    render_sidebar()

    # Define Navigation Structure
    page_studio = st.Page(render_studio_view, title="Application Studio", icon="📄", default=True)
    page_market = st.Page(render_market_radar_view, title="Market Radar & Skill Pulse", icon="📈")
    page_employ = st.Page(render_employability_view, title="Employability & Upskilling", icon="🎯")
    page_interview = st.Page(render_interview_view, title="Tough Gap Interview Simulator", icon="🎙️")

    nav = st.navigation({
        "Career Studio Suite": [page_studio, page_market, page_employ, page_interview]
    })
    nav.run()


if __name__ == "__main__":
    main()
