"""
Application Studio View:
- Live Job Finder across Malaysia & Global (LinkedIn, Indeed, Google Jobs)
- Direct Job Description / URL Input (JobStreet, Greenhouse, Lever, etc.)
- Multi-Agent ATS 1-Page Resume & Cover Letter Generation
"""
import os
from pathlib import Path
import streamlit as st

from src.parser import InputParser
from src.agent import JobSearchAgent, KeyManager
from src.renderer import Renderer
from src.job_finder import JobFinder


def run_tailoring_pipeline(resume_text: str, job_text_or_url: str, model_name: str, custom_key: str, max_retries: int):
    """Executes the multi-agent tailoring pipeline and renders results."""
    target_job_content = ""
    raw = job_text_or_url.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        with st.spinner("Scraping job details from URL..."):
            try:
                target_job_content = InputParser.parse_url(raw)
            except Exception as e:
                st.warning(f"Direct URL scraping encountered an issue ({e}). If job text was provided, using fallback.")
    if not target_job_content and raw:
        target_job_content = raw

    if not target_job_content:
        st.error("Could not obtain target job content. Please provide a valid URL or job description text.")
        return

    # Execute Multi-Agent Engine
    km = KeyManager()
    if custom_key.strip():
        km.add_key(custom_key.strip())

    if not km.keys:
        st.error(
            "🔑 **Google Gemini API Key Required**\n\n"
            "Please provide your API key in the sidebar under **⚙️ Engine Settings** to run the multi-agent pipeline.\n\n"
            "👉 [Click here to get a free key from Google AI Studio](https://aistudio.google.com/app/apikey) "
            "(Takes 30 seconds, 100% free with no credit card required)."
        )
        return

    agent = JobSearchAgent(key_manager=km, model=model_name)
    renderer = Renderer()

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_ui(msg, step):
        progress_bar.progress(step / 5.0)
        status_text.info(f"⏳ **Step {step}/5:** {msg}")

    try:
        job_analysis, match_eval, tailored_resume, cover_letter, review = agent.run_pipeline(
            job_raw_text=target_job_content,
            base_resume_text=resume_text,
            max_refinement_retries=max_retries,
            progress_callback=update_ui
        )
        progress_bar.progress(1.0)
        status_text.success("✅ Multi-Agent Pipeline Completed!")
    except Exception as e:
        status_text.error(f"❌ Execution failed: {e}")
        return

    # Save artifacts
    output_dir = Path("./outputs")
    artifacts = renderer.export_all(
        output_dir=output_dir,
        job_analysis=job_analysis,
        match_evaluation=match_eval,
        tailored_resume=tailored_resume,
        cover_letter=cover_letter,
        review_feedback=review,
        generate_pdf=True
    )

    st.markdown("---")

    # Results Dashboard
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.markdown(f"""
        <div class="score-card">
            <div style="font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">Match Score</div>
            <div class="score-val">{match_eval.overall_score}%</div>
            <div style="font-size:0.85rem; color:#94a3b8;">Role Alignment</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="score-card">
            <div style="font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">ATS Score</div>
            <div class="score-val" style="color: {'#4ade80' if review.ats_score >= 85 else '#facc15'}">{review.ats_score}%</div>
            <div style="font-size:0.85rem; color:#94a3b8;">{'Verified Pass' if review.pass_review else 'Good'}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="highlight-box">
            <b>🎯 Target Role:</b> {job_analysis.title} @ {job_analysis.company} ({job_analysis.experience_level})<br>
            <b>💡 Alignment Strategy:</b> {match_eval.alignment_strategy}
        </div>
        """, unsafe_allow_html=True)

    # Tabs for Artifacts
    tab_resume, tab_cover, tab_analysis, tab_downloads = st.tabs([
        "📄 Tailored 1-Page Resume",
        "✉️ Corporate Cover Letter",
        "📊 Strategic Analysis & ATS Audit",
        "💾 Download Center"
    ])

    with tab_resume:
        col_res1, col_res2 = st.columns([1, 1])
        with col_res1:
            st.markdown("#### Rendered HTML Preview")
            resume_html = renderer.render_resume_html(tailored_resume)
            st.components.v1.html(resume_html, height=750, scrolling=True)
        with col_res2:
            st.markdown("#### Markdown Source")
            resume_md = renderer.render_resume_markdown(tailored_resume)
            st.markdown(resume_md)

    with tab_cover:
        col_cov1, col_cov2 = st.columns([1, 1])
        with col_cov1:
            st.markdown("#### Rendered Cover Letter")
            cover_html = renderer.render_cover_letter_html(cover_letter)
            st.components.v1.html(cover_html, height=750, scrolling=True)
        with col_cov2:
            st.markdown("#### Markdown Source")
            cover_md = renderer.render_cover_letter_markdown(cover_letter)
            st.markdown(cover_md)

    with tab_analysis:
        st.markdown("### 📋 Matching Strengths")
        for q in match_eval.matching_qualifications:
            st.markdown(f"- ✅ {q}")

        if match_eval.missing_gaps:
            st.markdown("### 🔍 Addressed Gaps")
            for g in match_eval.missing_gaps:
                st.markdown(f"- ⚠️ {g}")

        st.markdown("### 🤖 Recruiter ATS Critique")
        st.info(review.critique)

    with tab_downloads:
        st.subheader("📥 Download Ready-to-Send Application Files")
        dcol1, dcol2 = st.columns(2)

        with dcol1:
            st.markdown("#### 📄 Resume Files")
            if "resume_pdf" in artifacts and artifacts["resume_pdf"].exists():
                with open(artifacts["resume_pdf"], "rb") as f:
                    st.download_button("📥 Download Resume (PDF)", f.read(), file_name="Tailored_Resume.pdf", mime="application/pdf", use_container_width=True)
            
            with open(artifacts["resume_html"], "rb") as f:
                st.download_button("📥 Download Resume (HTML)", f.read(), file_name="Tailored_Resume.html", mime="text/html", use_container_width=True)
            
            with open(artifacts["resume_md"], "rb") as f:
                st.download_button("📥 Download Resume (Markdown)", f.read(), file_name="Tailored_Resume.md", mime="text/markdown", use_container_width=True)

        with dcol2:
            st.markdown("#### ✉️ Cover Letter Files")
            if "cover_letter_pdf" in artifacts and artifacts["cover_letter_pdf"].exists():
                with open(artifacts["cover_letter_pdf"], "rb") as f:
                    st.download_button("📥 Download Cover Letter (PDF)", f.read(), file_name="Cover_Letter.pdf", mime="application/pdf", use_container_width=True)

            with open(artifacts["cover_letter_html"], "rb") as f:
                st.download_button("📥 Download Cover Letter (HTML)", f.read(), file_name="Cover_Letter.html", mime="text/html", use_container_width=True)

            with open(artifacts["cover_letter_md"], "rb") as f:
                st.download_button("📥 Download Cover Letter (Markdown)", f.read(), file_name="Cover_Letter.md", mime="text/markdown", use_container_width=True)


def render_studio_view():
    """Renders the Application Studio view."""
    st.markdown('<div class="main-header">💼 AI Job Search & Tailored Application Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Discover live job openings across <b>Malaysia & Global</b> (LinkedIn, Indeed, Google Jobs) and auto-generate 1-page ATS Resumes & Cover Letters.</div>', unsafe_allow_html=True)

    # Ensure session state variables
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = []
    if "base_resume_text" not in st.session_state:
        st.session_state["base_resume_text"] = ""
    if "target_role_query" not in st.session_state:
        st.session_state["target_role_query"] = "Software Engineer"
    if "target_location" not in st.session_state:
        st.session_state["target_location"] = "Kuala Lumpur, Malaysia"

    model_name = st.session_state.get("selected_model", "gemini-3.8-flash")
    custom_key = st.session_state.get("custom_key", "")
    max_retries = st.session_state.get("max_retries", 1)

    # Section 1: Resume Intake
    st.subheader("📄 1. Your Base Resume / CV Profile")

    resume_source = st.radio(
        "Resume Source:",
        ["⬆️ Upload CV / Resume", "✨ Try Demo Profile (Alex Rivera)", "✍️ Paste Resume Text", "📁 Project Directory Files"],
        horizontal=True,
        index=0,
        key="studio_resume_source"
    )

    resume_content = st.session_state.get("base_resume_text", "")

    if resume_source == "✨ Try Demo Profile (Alex Rivera)":
        demo_file = Path("test_resume.md")
        if demo_file.exists():
            demo_text = demo_file.read_text(encoding="utf-8")
            st.session_state["base_resume_text"] = demo_text
            resume_content = demo_text
            st.success("✅ **Demo Profile Loaded:** Alex Rivera — Senior AI Systems Engineer (5+ yrs exp)")
            with st.expander("👀 View Loaded Demo Profile Preview", expanded=False):
                st.markdown(demo_text)
        else:
            st.info("Demo profile file not found.")

    elif resume_source == "⬆️ Upload New File" or resume_source == "⬆️ Upload CV / Resume":
        uploaded_file = st.file_uploader(
            "Upload Base Resume (.docx, .pdf, .md, .txt)",
            type=["docx", "pdf", "md", "txt"],
            help="Drop your current CV or resume."
        )
        if uploaded_file is not None:
            suffix = Path(uploaded_file.name).suffix
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            try:
                resume_content = InputParser.parse_file(tmp_path)
                st.session_state["base_resume_text"] = resume_content
                st.success(f"✅ Uploaded and parsed **{uploaded_file.name}** ({len(resume_content)} chars).")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    elif resume_source == "✍️ Paste Resume Text":
        pasted_resume = st.text_area(
            "Paste your resume text here:",
            value=resume_content if len(resume_content) < 5000 else "",
            height=150,
            placeholder="Paste your base experience, education, and skills..."
        )
        if pasted_resume.strip():
            resume_content = pasted_resume.strip()
            st.session_state["base_resume_text"] = resume_content
            st.success(f"✅ Loaded pasted resume text ({len(resume_content)} chars).")

    else:  # "📁 Project Directory Files"
        detected_files = []
        ignored_names = {"readme.md", "requirements.txt", "test_job.txt", ".env", ".env.example", "packages.txt"}
        for f in sorted(Path(".").iterdir()):
            if f.is_file() and f.suffix.lower() in [".docx", ".pdf", ".md", ".txt"]:
                if f.name.lower() not in ignored_names:
                    detected_files.append(f.name)

        if detected_files:
            default_idx = 0
            for idx, fname in enumerate(detected_files):
                if "resume" in fname.lower():
                    default_idx = idx
                    break

            selected_local_file = st.selectbox(
                "Detected CV / Resume Files:",
                options=detected_files,
                index=default_idx,
                help="Automatically reads your resume directly from the project directory."
            )
            if selected_local_file:
                try:
                    resume_content = InputParser.parse_file(selected_local_file)
                    st.session_state["base_resume_text"] = resume_content
                    st.success(f"✅ Loaded **{selected_local_file}** directly from folder ({len(resume_content)} characters parsed).")
                    with st.expander("👀 View Parsed Resume Preview"):
                        st.text(resume_content[:800] + ("..." if len(resume_content) > 800 else ""))
                except Exception as e:
                    st.error(f"Error reading {selected_local_file}: {e}")
        else:
            st.info("No resume files found in the project directory. Please use Upload or Paste options above.")

    st.markdown("---")

    # Workflow Tabs
    mode_tab1, mode_tab2 = st.tabs([
        "🔍 Auto Job Finder (Malaysia & Global)",
        "📋 Direct Input (Paste Job URL / Text / JobStreet)"
    ])

    # TAB 1: AUTO JOB FINDER
    with mode_tab1:
        st.markdown("#### 🇲🇾 Search Live Job Openings")
        st.caption("Search across LinkedIn, Indeed Malaysia, and Google Jobs without needing any accounts.")
        st.info("💡 **Tip for mobile & cloud visitors:** If job portals are temporarily slow or rate-limited, switch to the **'Direct Input'** tab to paste any JobStreet, LinkedIn, or company job description directly for instant 1-click tailoring!")

        s_col1, s_col2, s_col3 = st.columns([2, 2, 1])

        with s_col1:
            search_query = st.text_input("Job Title / Keywords", value=st.session_state.get("target_role_query", "Software Engineer"), placeholder="e.g. Full Stack Developer, AI Engineer, Project Manager")
        with s_col2:
            default_loc = st.session_state.get("target_location", "Kuala Lumpur, Malaysia")
            loc_options = JobFinder.MALAYSIA_LOCATIONS + ["Singapore", "Remote", "Global"]
            loc_idx = loc_options.index(default_loc) if default_loc in loc_options else 1
            location_choice = st.selectbox(
                "Location Hub",
                options=loc_options,
                index=loc_idx
            )
        with s_col3:
            results_count = st.selectbox("Max Results", [5, 10, 15, 20], index=1)

        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            selected_sites = st.multiselect(
                "Job Portals to Search",
                ["linkedin", "indeed", "google"],
                default=["linkedin", "indeed"]
            )
        with f_col2:
            search_btn = st.button("🔎 Search Openings", type="primary", use_container_width=True)

        if search_btn:
            if not search_query.strip():
                st.warning("Please enter a job title or keyword.")
            else:
                st.session_state["target_role_query"] = search_query.strip()
                st.session_state["target_location"] = location_choice
                with st.spinner(f"Searching live job postings for '{search_query}' in {location_choice}..."):
                    results = JobFinder.search(
                        search_term=search_query.strip(),
                        location=location_choice,
                        sites=selected_sites,
                        results_wanted=results_count
                    )
                    st.session_state["search_results"] = results

        # Display Search Results
        results = st.session_state.get("search_results", [])
        if results:
            st.markdown(f"### Found **{len(results)}** Matching Openings in {location_choice}")
            
            for idx, job in enumerate(results):
                with st.container():
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <span class="badge badge-{job.site.lower()}">{job.site}</span>
                                <span class="badge badge-loc">📍 {job.location}</span>
                                <h4 style="margin: 0.3rem 0 0.1rem 0; color:#0f172a;">{job.title}</h4>
                                <div style="font-weight:600; color:#3b82f6;">🏢 {job.company}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns([3, 1])
                    with btn_col1:
                        if job.job_url:
                            st.markdown(f"[🔗 View Original Posting on {job.site}]({job.job_url})")
                        if job.description:
                            with st.expander("👀 View Description Preview"):
                                st.write(job.description[:1000] + ("..." if len(job.description) > 1000 else ""))
                    with btn_col2:
                        if st.button(f"⚡ 1-Click Tailor", key=f"tailor_{job.id}", use_container_width=True):
                            current_resume = st.session_state.get("base_resume_text", "")
                            if not current_resume:
                                st.error("⚠️ Please upload or paste your base resume in Section 1 above first!")
                            else:
                                job_input = job.description if len(job.description) > 200 else job.job_url
                                run_tailoring_pipeline(
                                    resume_text=current_resume,
                                    job_text_or_url=job_input,
                                    model_name=model_name,
                                    custom_key=custom_key,
                                    max_retries=max_retries
                                )

    # TAB 2: DIRECT INPUT
    with mode_tab2:
        st.markdown("#### 📋 Paste Job URL or Description")
        st.caption("Paste a link from **JobStreet Malaysia**, **LinkedIn**, **Indeed**, **Greenhouse**, **Lever**, or paste the raw description text.")

        sample_col_btn1, sample_col_btn2 = st.columns([3, 1])
        with sample_col_btn2:
            if st.button("✨ Load Sample Job", use_container_width=True, help="Load sample Senior AI Systems Engineer job posting"):
                sample_job_path = Path("test_job.txt")
                if sample_job_path.exists():
                    st.session_state["sample_job_text"] = sample_job_path.read_text(encoding="utf-8")
                    st.success("Loaded sample job description!")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            direct_job_url = st.text_input(
                "Job Posting URL (JobStreet, LinkedIn, etc.)",
                placeholder="https://my.jobstreet.com/jobs/..."
            )
        with d_col2:
            default_job_text = st.session_state.get("sample_job_text", "")
            direct_job_text = st.text_area(
                "Or paste full job description text:",
                value=default_job_text,
                height=150,
                placeholder="Paste the job responsibilities, requirements, qualifications..."
            )

        direct_gen_btn = st.button("🚀 Analyze & Generate Tailored Application", type="primary", use_container_width=True)

        if direct_gen_btn:
            current_resume = st.session_state.get("base_resume_text", "")
            if not current_resume:
                st.error("⚠️ Please upload or paste your base resume in Section 1 above first!")
            else:
                input_job = direct_job_url.strip() if direct_job_url.strip() else direct_job_text.strip()
                if not input_job:
                    st.error("Please provide either a Job URL or paste the job description text.")
                else:
                    run_tailoring_pipeline(
                        resume_text=current_resume,
                        job_text_or_url=input_job,
                        model_name=model_name,
                        custom_key=custom_key,
                        max_retries=max_retries
                    )
