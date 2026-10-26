"""
Market Radar & Skill Pulse Scanner View:
- Live multi-board market sampling across Malaysia & Global
- AI synthesis of in-demand skills, relative frequency, and emergence
- Interactive Plotly visualizations and salary intelligence
- Direct handoff to Employability Diagnostic
"""
import os
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

from src.job_finder import JobFinder
from src.agent import JobSearchAgent, KeyManager
from src.schema import MarketDemandReport


def render_market_radar_view():
    """Renders the Market Radar & Skill Pulse Scanner."""
    st.markdown('<div class="main-header">📈 Live Job Market Radar & Skill Pulse</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Scan live postings across <b>Malaysia & Global hubs</b> to uncover real-time skill demand heatmaps, salary bands, and emerging tech trends.</div>', unsafe_allow_html=True)

    # Session State Initialization
    if "market_demand_report" not in st.session_state:
        st.session_state["market_demand_report"] = None
    if "target_role_query" not in st.session_state:
        st.session_state["target_role_query"] = "Software Engineer"
    if "target_location" not in st.session_state:
        st.session_state["target_location"] = "Kuala Lumpur, Malaysia"

    model_name = st.session_state.get("selected_model", "gemini-3.8-flash")
    custom_key = st.session_state.get("custom_key", "")

    # Market Scan Controls
    with st.container():
        st.markdown("### 🔍 Market Scan Parameters")
        c1, c2, c3 = st.columns([2, 2, 1])

        preset_roles = [
            "Software Engineer",
            "Full Stack Developer",
            "AI / Machine Learning Engineer",
            "Cloud & DevOps Engineer",
            "Data Scientist / Data Analyst",
            "Mobile Developer (Flutter / React Native)",
            "Cybersecurity Specialist",
            "Custom Role..."
        ]

        with c1:
            role_selection = st.selectbox(
                "Target Role / Field",
                options=preset_roles,
                index=0
            )
            if role_selection == "Custom Role...":
                target_query = st.text_input("Enter custom job title:", value="Solutions Architect")
            else:
                target_query = role_selection

        with c2:
            loc_options = JobFinder.MALAYSIA_LOCATIONS + ["Singapore", "Remote", "Global"]
            default_loc = st.session_state.get("target_location", "Kuala Lumpur, Malaysia")
            loc_idx = loc_options.index(default_loc) if default_loc in loc_options else 1
            target_loc = st.selectbox("Market Geographic Hub", options=loc_options, index=loc_idx)

        with c3:
            sample_size = st.slider("Sample Size", min_value=10, max_value=30, value=15, step=5, help="Number of live postings to scrape and synthesize")

        portals_col, scan_btn_col = st.columns([3, 1])
        with portals_col:
            selected_portals = st.multiselect(
                "Aggregated Platforms",
                ["linkedin", "indeed", "google"],
                default=["linkedin", "indeed"]
            )
        with scan_btn_col:
            st.write("")
            scan_btn = st.button("📡 Scan Live Market", type="primary", use_container_width=True)

    # Trigger Market Analysis
    if scan_btn:
        if not target_query.strip():
            st.warning("Please specify a target role.")
        else:
            st.session_state["target_role_query"] = target_query.strip()
            st.session_state["target_location"] = target_loc

            km = KeyManager()
            if custom_key.strip():
                km.add_key(custom_key.strip())

            if not km.keys:
                st.error(
                    "🔑 **Google Gemini API Key Required**\n\n"
                    "Please enter your Gemini API key in the sidebar under **⚙️ Engine Settings** to run the live market synthesis.\n\n"
                    "👉 [Click here to get a free key from Google AI Studio](https://aistudio.google.com/app/apikey) (Takes 30 seconds, 100% free)."
                )
                return

            agent = JobSearchAgent(key_manager=km, model=model_name)

            progress_bar = st.progress(0)
            status_box = st.empty()

            try:
                # Step 1: Scrape Sample Corpus
                status_box.info(f"⏳ **Step 1/2:** Sampling {sample_size} live job postings for '{target_query}' in {target_loc}...")
                progress_bar.progress(0.4)
                listings, corpus = JobFinder.sample_market_corpus(
                    query=target_query,
                    location=target_loc,
                    sample_size=sample_size,
                    sites=selected_portals
                )

                # Step 2: Gemini Synthesis
                status_box.info("🧠 **Step 2/2:** Gemini is synthesizing macro skill demand, salary bands, and emerging trends...")
                progress_bar.progress(0.8)

                report = agent.analyze_market_demand(
                    query=target_query,
                    location=target_loc,
                    sample_size=len(listings) if listings else sample_size,
                    market_corpus=corpus
                )

                progress_bar.progress(1.0)
                status_box.success(f"✅ Synthesized {len(listings) if listings else sample_size} postings into Market Demand Report!")
                st.session_state["market_demand_report"] = report

                # Persist snapshot locally
                reports_dir = Path("./outputs/market_reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                clean_name = f"{target_query}_{target_loc}".replace(" ", "_").replace("/", "_").replace(",", "")
                report_file = reports_dir / f"{clean_name}.json"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report.model_dump_json(indent=2))

            except Exception as e:
                status_box.error(f"❌ Market scan encountered an issue: {e}")
                return

    # Render Report Dashboard
    report: MarketDemandReport = st.session_state.get("market_demand_report")
    if report:
        st.markdown("---")

        # Top Macro Cards
        mc1, mc2, mc3 = st.columns([1, 1, 2])
        with mc1:
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">Postings Analyzed</div>
                <div class="score-val">{report.sample_size}</div>
                <div style="font-size:0.85rem; color:#94a3b8;">{report.location}</div>
            </div>
            """, unsafe_allow_html=True)

        with mc2:
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">Market Focus</div>
                <div class="score-val" style="font-size:1.8rem; padding-top:0.4rem;">{len(report.top_hard_skills)} Skills</div>
                <div style="font-size:0.85rem; color:#38bdf8;">Tracked & Ranked</div>
            </div>
            """, unsafe_allow_html=True)

        with mc3:
            st.markdown(f"""
            <div class="highlight-box">
                <b>💰 Salary & Compensation Insights:</b><br>
                {report.salary_insights}<br><br>
                <b>🏢 Active Hiring Hotspots:</b> {', '.join(report.top_hiring_companies[:6]) if report.top_hiring_companies else 'Various Tech & Enterprise Employers'}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📋 Executive Market Overview")
        st.info(report.market_summary)

        # Plotly Interactive Demand Heatmap
        if report.top_hard_skills:
            st.markdown("### 📊 Skill Demand Intensity Chart (0 – 100%)")
            st.caption("Relative market demand frequency extracted from active employer postings.")

            df_skills = pd.DataFrame([
                {
                    "Skill": s.skill_name,
                    "Demand Index": s.frequency_score,
                    "Importance": s.importance,
                    "Category": s.category,
                    "Real Use Cases": "<br>• ".join(s.sample_use_cases) if s.sample_use_cases else "Standard role requirements"
                }
                for s in report.top_hard_skills
            ])

            # Sort ascending so highest appears at top of horizontal chart
            df_skills = df_skills.sort_values("Demand Index", ascending=True)

            color_map = {
                "Core / Must-Have": "#ef4444",
                "High-Demand": "#3b82f6",
                "Emerging / Differentiator": "#10b981"
            }

            fig = px.bar(
                df_skills,
                x="Demand Index",
                y="Skill",
                color="Importance",
                orientation="h",
                color_discrete_map=color_map,
                hover_data={"Real Use Cases": True, "Category": True, "Demand Index": True},
                height=max(400, len(df_skills) * 32)
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(range=[0, 100], title="Market Demand Intensity Index (%)"),
                yaxis=dict(title=""),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Categorized Skills Breakdown
        st.markdown("### 🛠️ In-Demand Technical & Professional Breakdown")
        col_must, col_high, col_emerge = st.columns(3)

        with col_must:
            st.markdown("#### 🔴 Core Must-Haves")
            must_skills = [s for s in report.top_hard_skills if "must" in s.importance.lower() or "core" in s.importance.lower()]
            if not must_skills:
                must_skills = report.top_hard_skills[:4]
            for s in must_skills:
                with st.expander(f"**{s.skill_name}** ({s.frequency_score}%)"):
                    st.caption(f"Category: {s.category}")
                    if s.sample_use_cases:
                        for u in s.sample_use_cases:
                            st.write(f"- {u}")

        with col_high:
            st.markdown("#### 🔵 High-Demand Competencies")
            high_skills = [s for s in report.top_hard_skills if "high" in s.importance.lower()]
            if not high_skills:
                high_skills = report.top_hard_skills[4:8]
            for s in high_skills:
                with st.expander(f"**{s.skill_name}** ({s.frequency_score}%)"):
                    st.caption(f"Category: {s.category}")
                    if s.sample_use_cases:
                        for u in s.sample_use_cases:
                            st.write(f"- {u}")

        with col_emerge:
            st.markdown("#### 🟢 Emerging Differentiators")
            emerge_skills = [s for s in report.top_hard_skills if "emerg" in s.importance.lower() or "diff" in s.importance.lower()]
            if not emerge_skills:
                emerge_skills = report.top_hard_skills[8:]
            for s in emerge_skills:
                with st.expander(f"**{s.skill_name}** ({s.frequency_score}%)"):
                    st.caption(f"Category: {s.category}")
                    if s.sample_use_cases:
                        for u in s.sample_use_cases:
                            st.write(f"- {u}")

        # Soft Skills & Emerging Trends
        st.markdown("---")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("#### 🧠 Essential Soft Skills & Culture Fit")
            for ss in report.top_soft_skills:
                st.markdown(f"- 🤝 **{ss}**")

        with sc2:
            st.markdown("#### 🚀 Breakout Tech & Architecture Paradigms")
            for et in report.emerging_trends:
                st.markdown(f"- ⚡ **{et}**")

        # Experience Bands
        if report.experience_expectations:
            st.markdown("#### 🎓 Seniority & Experience Expectations")
            num_cols = max(1, min(len(report.experience_expectations), 4))
            exp_cols = st.columns(num_cols)
            for i, tier in enumerate(report.experience_expectations):
                with exp_cols[i % num_cols]:
                    st.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:0.8rem; margin-bottom:0.5rem;">
                        <b style="color:#0f172a;">{tier.band}</b><br>
                        <span style="font-size:0.85rem; color:#475569;">{tier.expectation}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # Call to Action & Navigation
        st.markdown("---")
        cta_col1, cta_col2 = st.columns([2, 1])
        with cta_col1:
            st.markdown("### 🎯 Ready to see where you stand?")
            st.write("Cross-examine your base CV against this real market radar to get your **Pareto 80/20 Gap Diagnosis** and budget-friendly learning roadmap.")
        with cta_col2:
            st.write("")
            st.info("👉 Switch to the **🎯 Employability & Upskilling** page from the sidebar to generate your personalized action plan!")

        # Export Report
        with st.expander("💾 Export Market Report Data (JSON)"):
            st.download_button(
                "📥 Download Market Demand JSON",
                report.model_dump_json(indent=2),
                file_name=f"market_report_{report.query.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
