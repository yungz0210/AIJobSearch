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

# Global Custom CSS for Premium Design, Micro-animations & Mobile Responsiveness
st.markdown("""
<style>
    /* Desktop & Core Styles */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .score-card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        color: #ffffff;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .score-val {
        font-size: 2.6rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.1;
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
        padding: 1.1rem;
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
        padding: 0.25rem 0.65rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .badge-linkedin { background-color: #0077b5; color: white; }
    .badge-indeed { background-color: #2164f3; color: white; }
    .badge-google { background-color: #ea4335; color: white; }
    .badge-loc { background-color: #f1f5f9; color: #475569; }

    .bmac-btn {
        display: block;
        background: linear-gradient(135deg, #FFDD00 0%, #FBBF24 100%);
        color: #000000 !important;
        font-weight: 700;
        text-align: center;
        padding: 0.65rem 1rem;
        border-radius: 8px;
        text-decoration: none !important;
        box-shadow: 0 2px 6px rgba(251, 191, 36, 0.3);
        transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .bmac-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
    }

    /* 📱 Mobile Specific Media Queries */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-bottom: 3rem !important;
        }
        .main-header {
            font-size: 1.5rem !important;
            margin-bottom: 0.4rem !important;
        }
        .sub-header {
            font-size: 0.9rem !important;
            margin-bottom: 1rem !important;
        }
        .score-card {
            padding: 0.8rem !important;
            margin-bottom: 0.6rem !important;
        }
        .score-val {
            font-size: 2rem !important;
        }
        .job-card {
            padding: 0.8rem !important;
        }
        /* Make buttons touch-friendly on mobile */
        button[kind="primary"], button[kind="secondary"] {
            min-height: 44px !important;
            font-size: 0.95rem !important;
        }
        /* Make tabs scrollable horizontally on mobile */
        div[data-baseweb="tab-list"] {
            overflow-x: auto !important;
            white-space: nowrap !important;
            padding-bottom: 4px !important;
        }
    }
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
        "selected_model": "gemini-3.8-flash",
        "custom_key": "",
        "max_retries": 1
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render_sidebar():
    """Renders shared sidebar configurations, BYOK helper, and status."""
    with st.sidebar:
        st.markdown("### ⚙️ Engine Settings")
        model = st.selectbox(
            "Gemini Model",
            ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-3.7-flash", "gemini-3.5-flash"],
            index=0,
            key="sb_model"
        )
        st.session_state["selected_model"] = model

        st.markdown("🔑 **Gemini API Key (BYOK)**")
        key = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.get("custom_key", ""),
            placeholder="AIzaSy...",
            help="Free via Google AI Studio. Stored privately only in your browser session.",
            key="sb_key",
            label_visibility="collapsed"
        )
        st.session_state["custom_key"] = key
        st.markdown(
            '<div style="margin-top:-0.4rem; margin-bottom:0.8rem; font-size:0.8rem;">'
            '👉 <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#38bdf8; text-decoration:underline;">'
            'Get a Free Gemini Key (Takes 30s)</a></div>',
            unsafe_allow_html=True
        )

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
        st.markdown("### ☕ Support This Tool")
        st.markdown("""
        <a class="bmac-btn" href="https://buymeacoffee.com/3amassembly" target="_blank">
            ☕ Buy Me a Coffee
        </a>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🇲🇾 Target Hubs")
        st.markdown("""
        - **Malaysia Core:** Kuala Lumpur, Selangor, Cyberjaya, Penang, Johor Bahru
        - **Global:** Singapore, Remote, Worldwide
        - **Subsidies:** HRD Corp, MDEC, GLIC
        """)

        st.markdown("---")
        st.caption(
            "⚖️ **Disclaimer:** AI-generated documents are recommendations. "
            "Please review and verify before submitting. Not affiliated with Google, LinkedIn, or Indeed."
        )


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
