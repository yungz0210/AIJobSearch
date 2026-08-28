"""
Employability & Upskilling Navigator View:
- Diagnostic comparing candidate base resume against market benchmarks
- Pareto 80/20 Gap Prioritization (Tier 1 Deal-Breakers vs Tier 2 Boosters)
- Budget-adaptive learning pathways (RM0 Free to Physical Centers & HRD Corp Subsidies)
- 30/60/90-Day Career Sprints and Proof-of-Work Project Blueprints
"""
import os
import json
from pathlib import Path
import streamlit as st

from src.parser import InputParser
from src.agent import JobSearchAgent, KeyManager
from src.schema import EmployabilityRoadmap, MarketDemandReport


def render_employability_view():
    """Renders the Employability Diagnostic & Budget-Adaptive Upskilling View."""
    st.markdown('<div class="main-header">🎯 Employability & Upskilling Navigator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Bridge your skill gaps with a <b>Pareto 80/20 career roadmap</b>, budget-adaptive learning paths (RM0 to Physical Centers), and portfolio proof-of-work specs.</div>', unsafe_allow_html=True)

    # Session State
    if "employability_roadmap" not in st.session_state:
        st.session_state["employability_roadmap"] = None
    if "base_resume_text" not in st.session_state:
        st.session_state["base_resume_text"] = ""
    if "target_role_query" not in st.session_state:
        st.session_state["target_role_query"] = "Software Engineer"

    model_name = st.session_state.get("selected_model", "gemini-3.6-flash")
    custom_key = st.session_state.get("custom_key", "")
    active_market_report: MarketDemandReport = st.session_state.get("market_demand_report")

    # Section 1: Inputs & Diagnostic Settings
    with st.container():
        st.markdown("### 📋 Diagnostic Profile & Preferences")
        c1, c2 = st.columns([1, 1])

        with c1:
            default_role = st.session_state.get("target_role_query", "Software Engineer")
            target_role = st.text_input(
                "Target Role / Career Direction:",
                value=default_role,
                placeholder="e.g. AI Engineer, Full Stack Developer, DevOps Engineer"
            )

            study_hours = st.slider(
                "Available Study Time (Hours / Week):",
                min_value=3,
                max_value=35,
                value=10,
                step=1,
                help="Calibrates the 30/60/90-day sprint intensity to your real schedule."
            )

        with c2:
            budget_choice = st.selectbox(
                "Preferred Budget Focus:",
                [
                    "All Tiers (Show RM0 Free, Budget, Certs, & Bootcamps)",
                    "Free / RM0 Focus (YouTube, Open-Source, Docs, CS50)",
                    "Budget-Friendly (< RM150 / $30 - Udemy, Coursera Aid)",
                    "Professional Certifications (AWS, GCP, CKA, Terraform)",
                    "Physical Centers & Subsidized Hubs (HRD Corp, 42KL, Next Academy)"
                ],
                index=0
            )

            if active_market_report:
                st.success(f"🔗 Linked with live Market Radar data: **{active_market_report.query}** in **{active_market_report.location}**")
            else:
                st.caption("💡 Tip: Running a scan on the **📈 Market Radar** page first enriches this diagnostic with live hiring data.")

    # Section 2: Resume Intake
    st.markdown("---")
    st.subheader("📄 Your Current CV / Resume")

    current_resume = st.session_state.get("base_resume_text", "")

    if current_resume:
        st.info(f"✅ Active resume loaded in session ({len(current_resume)} characters).")
        with st.expander("👀 View or Replace Loaded Resume"):
            pasted_new = st.text_area("Resume Content:", value=current_resume[:3000], height=120)
            if st.button("Update Resume Content"):
                st.session_state["base_resume_text"] = pasted_new
                current_resume = pasted_new
                st.success("Resume updated!")
    else:
        st.warning("No resume currently loaded in session. Please upload or paste one below:")
        upload_col, paste_col = st.columns(2)
        with upload_col:
            up_file = st.file_uploader("Upload CV (.docx, .pdf, .md, .txt)", type=["docx", "pdf", "md", "txt"])
            if up_file is not None:
                import tempfile
                suffix = Path(up_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(up_file.getvalue())
                    tmp_path = tmp.name
                try:
                    current_resume = InputParser.parse_file(tmp_path)
                    st.session_state["base_resume_text"] = current_resume
                    st.success(f"Loaded {up_file.name} successfully!")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
        with paste_col:
            pasted_text = st.text_area("Or Paste Resume Text:", height=100)
            if st.button("Load Pasted Resume"):
                if pasted_text.strip():
                    current_resume = pasted_text.strip()
                    st.session_state["base_resume_text"] = current_resume
                    st.success("Resume loaded from text!")

    # Diagnostic Trigger Button
    diag_btn = st.button("🚀 Run Employability Diagnostic & Generate Roadmap", type="primary", use_container_width=True)

    if diag_btn:
        if not current_resume:
            st.error("Please load or paste your CV/Resume first.")
        elif not target_role.strip():
            st.error("Please specify your target role.")
        else:
            st.session_state["target_role_query"] = target_role.strip()
            km = KeyManager()
            if custom_key.strip():
                km.add_key(custom_key.strip())
            agent = JobSearchAgent(key_manager=km, model=model_name)

            with st.spinner("Analyzing candidate profile against market expectations and curating multi-tier learning paths..."):
                try:
                    roadmap = agent.generate_employability_roadmap(
                        base_resume=current_resume,
                        target_role=target_role.strip(),
                        market_report=active_market_report,
                        budget_preference=budget_choice,
                        hours_per_week=study_hours
                    )
                    st.session_state["employability_roadmap"] = roadmap
                    st.success("✅ Employability Roadmap Generated!")
                except Exception as e:
                    st.error(f"Diagnostic generation failed: {e}")
                    return

    # Render Roadmap Dashboard
    roadmap: EmployabilityRoadmap = st.session_state.get("employability_roadmap")
    if roadmap:
        st.markdown("---")

        # Top Diagnostic Cards
        rc1, rc2, rc3 = st.columns([1, 1, 2])
        with rc1:
            score_color = "#4ade80" if roadmap.current_readiness_score >= 80 else ("#facc15" if roadmap.current_readiness_score >= 60 else "#f87171")
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">Readiness Score</div>
                <div class="score-val" style="color: {score_color}">{roadmap.current_readiness_score}%</div>
                <div style="font-size:0.85rem; color:#94a3b8;">Target: {roadmap.target_role}</div>
            </div>
            """, unsafe_allow_html=True)

        with rc2:
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">Estimated Timeline</div>
                <div class="score-val" style="font-size:1.6rem; padding-top:0.6rem; color:#38bdf8;">{roadmap.time_to_ready_estimate}</div>
                <div style="font-size:0.85rem; color:#94a3b8;">To Reach 85%+ Match</div>
            </div>
            """, unsafe_allow_html=True)

        with rc3:
            st.markdown(f"""
            <div class="highlight-box">
                <b>💡 Executive Career Diagnosis:</b><br>
                {roadmap.executive_summary}
            </div>
            """, unsafe_allow_html=True)

        # Tabbed Roadmap Modules
        tab_gaps, tab_sprint, tab_projects = st.tabs([
            "🔍 Pareto 80/20 Gaps & Learning Pathways",
            "📅 30 / 60 / 90-Day Sprint Roadmap",
            "🛠️ Proof-of-Work Project Blueprints"
        ])

        # TAB 1: GAPS & LEARNING PATHWAYS
        with tab_gaps:
            st.markdown("### 🎯 Prioritized Skill Gaps & Curated Recommendations")
            st.caption("Addressing **Tier 1 Deal-Breakers** first maximizes interview call-backs with minimum wasted effort.")

            tier_colors = {
                "Tier 1: Deal-Breaker": "#ef4444",
                "Tier 2: High-Leverage Booster": "#3b82f6",
                "Tier 3: Learn-on-the-Job": "#10b981"
            }

            for idx, gap in enumerate(roadmap.skill_gaps):
                badge_bg = tier_colors.get(gap.tier, "#64748b")
                with st.container():
                    st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                            <h3 style="margin:0; color:#0f172a;">#{idx+1}. {gap.skill}</h3>
                            <span style="background-color:{badge_bg}; color:#ffffff; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.8rem; font-weight:700;">
                                {gap.tier}
                            </span>
                        </div>
                        <p style="color:#475569; font-size:0.95rem; margin-bottom:0.8rem;"><b>Why it matters:</b> {gap.why_it_matters}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if gap.learning_pathway:
                        st.markdown("##### 📚 Recommended Learning Paths by Budget & Format:")
                        res_cols = st.columns(min(len(gap.learning_pathway), 4))
                        for r_idx, res in enumerate(gap.learning_pathway):
                            with res_cols[r_idx % len(res_cols)]:
                                subsidy_badge = "🇲🇾 **HRD Corp / MDEC Subsidized**<br>" if res.malaysia_subsidy_eligible else ""
                                st.markdown(f"""
                                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:0.8rem; height:100%; display:flex; flex-direction:column; justify-content:space-between;">
                                    <div>
                                        <span style="font-size:0.75rem; font-weight:700; color:#3b82f6; text-transform:uppercase;">{res.resource_type}</span><br>
                                        <b style="color:#0f172a; font-size:0.9rem;">{res.title}</b><br>
                                        <span style="font-size:0.8rem; color:#64748b;">🏢 {res.provider}</span><br>
                                        <span style="font-size:0.8rem; color:#059669; font-weight:600;">💰 {res.cost_tier}</span><br>
                                        <span style="font-size:0.8rem; color:#475569;">⏱️ {res.estimated_duration}</span><br>
                                        {subsidy_badge}
                                    </div>
                                    <div style="margin-top:0.6rem;">
                                        <a href="{res.search_url}" target="_blank" style="display:inline-block; font-size:0.8rem; font-weight:600; color:#2563eb; text-decoration:none;">🔗 Explore / Enroll →</a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    st.write("")

        # TAB 2: 30 / 60 / 90 DAY SPRINT
        with tab_sprint:
            st.markdown("### 📅 Execution Sprints (Tailored to Your Available Hours)")
            sc1, sc2, sc3 = st.columns(3)

            with sc1:
                st.markdown("""
                <div style="background:#fef2f2; border-left:4px solid #ef4444; padding:0.8rem; border-radius:6px; margin-bottom:0.8rem;">
                    <b style="color:#991b1b; font-size:1.05rem;">Days 1 – 30: Deal-Breakers</b><br>
                    <span style="font-size:0.85rem; color:#7f1d1d;">Eliminate auto-rejection risks</span>
                </div>
                """, unsafe_allow_html=True)
                for item in roadmap.sprint_30_days:
                    st.markdown(f"- 🔴 {item}")

            with sc2:
                st.markdown("""
                <div style="background:#eff6ff; border-left:4px solid #3b82f6; padding:0.8rem; border-radius:6px; margin-bottom:0.8rem;">
                    <b style="color:#1e40af; font-size:1.05rem;">Days 31 – 60: High-Leverage Boosters</b><br>
                    <span style="font-size:0.85rem; color:#1e3a8a;">Build proof-of-work project</span>
                </div>
                """, unsafe_allow_html=True)
                for item in roadmap.sprint_60_days:
                    st.markdown(f"- 🔵 {item}")

            with sc3:
                st.markdown("""
                <div style="background:#f0fdf4; border-left:4px solid #10b981; padding:0.8rem; border-radius:6px; margin-bottom:0.8rem;">
                    <b style="color:#065f46; font-size:1.05rem;">Days 61 – 90: Interview Ready & Apply</b><br>
                    <span style="font-size:0.85rem; color:#064e3b;">High-volume targeted applications</span>
                </div>
                """, unsafe_allow_html=True)
                for item in roadmap.sprint_90_days:
                    st.markdown(f"- 🟢 {item}")

        # TAB 3: PROOF-OF-WORK PROJECTS
        with tab_projects:
            st.markdown("### 🛠️ Portfolio Proof-of-Work Project Blueprints")
            st.caption("Recruiters hire evidence over claims. Building one of these projects gives you undeniable proof of skill.")

            for p_idx, proj in enumerate(roadmap.portfolio_projects, 1):
                with st.container():
                    st.markdown(f"""
                    <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:10px; padding:1.2rem; margin-bottom:1rem;">
                        <span style="background:#e0e7ff; color:#3730a3; padding:0.2rem 0.6rem; border-radius:9999px; font-size:0.75rem; font-weight:700;">
                            Project #{p_idx} • {proj.target_industry}
                        </span>
                        <h3 style="margin:0.4rem 0 0.2rem 0; color:#0f172a;">{proj.title}</h3>
                        <p style="color:#334155; margin-bottom:0.6rem;"><b>Problem Solved:</b> {proj.problem_statement}</p>
                        <div style="margin-bottom:0.6rem;">
                            <b>Tech Stack:</b> {' • '.join([f'<code>{t}</code>' for t in proj.tech_stack])}
                        </div>
                        <div style="background:#f1f5f9; padding:0.8rem; border-radius:6px; margin-bottom:0.6rem;">
                            <b style="color:#0f172a;">Architecture Overview:</b><br>
                            <span style="font-size:0.9rem; color:#475569;">{proj.architecture_overview}</span>
                        </div>
                        <div style="background:#ecfdf5; border-left:3px solid #10b981; padding:0.8rem; border-radius:6px; margin-bottom:0.6rem;">
                            <b style="color:#065f46;">Pre-Written Resume Bullet Point (XYZ Formula):</b><br>
                            <span style="font-size:0.9rem; color:#064e3b; font-style:italic;">"{proj.resume_bullet_point}"</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander(f"📋 View Starter GitHub README.md Template for {proj.title}"):
                        st.code(proj.github_readme_starter, language="markdown")

        # Call to Action for Interview Prep
        st.markdown("---")
        cta_c1, cta_c2 = st.columns([2, 1])
        with cta_c1:
            st.markdown("### 🎙️ Ready to practice answering questions on your gaps?")
            st.write("Recruiters will spot your missing skills. Go to the **🎙️ Interview Gap Simulator** to practice STAR-method answers.")
        with cta_c2:
            st.write("")
            st.info("👉 Switch to the **🎙️ Interview Gap Simulator** page in the sidebar!")

        # Export Roadmap
        with st.expander("💾 Export Complete Employability Roadmap (JSON / Markdown)"):
            st.download_button(
                "📥 Download Roadmap JSON",
                roadmap.model_dump_json(indent=2),
                file_name=f"employability_roadmap_{roadmap.target_role.replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
