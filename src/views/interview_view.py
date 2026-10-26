"""
Interview Gap Simulator View:
- Drills candidate on tough technical and behavioral questions targeting their exact skill gaps
- Reveals recruiter hidden intent and provides STAR-method response frameworks
- Interactive AI mock answer evaluation and feedback
"""
import streamlit as st
from src.agent import JobSearchAgent, KeyManager
from src.schema import EmployabilityRoadmap


def render_interview_view():
    """Renders the Tough Gap Interview Simulator view."""
    st.markdown('<div class="main-header">🎙️ AI Tough Gap Interview Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Practice answering challenging questions on your <b>exact missing skills</b>. Learn what recruiters are really testing and master the STAR response framework.</div>', unsafe_allow_html=True)

    roadmap: EmployabilityRoadmap = st.session_state.get("employability_roadmap")
    model_name = st.session_state.get("selected_model", "gemini-3.8-flash")
    custom_key = st.session_state.get("custom_key", "")

    if not roadmap or not roadmap.interview_gap_questions:
        st.info("💡 **No active gap diagnostic found in session.**")
        st.write("To simulate questions tailored specifically to your background and gaps, run a diagnostic in **🎯 Employability & Upskilling** first.")
        st.markdown("Or, generate sample gap drill questions right now:")

        sample_col1, sample_col2 = st.columns([2, 1])
        with sample_col1:
            custom_role = st.text_input("Target Role:", value=st.session_state.get("target_role_query", "Senior AI & Full Stack Engineer"))
            custom_gap = st.text_input("Skill Gap to Drill:", value="Kubernetes & Distributed Microservices at Scale")
        with sample_col2:
            st.write("")
            st.write("")
            gen_drill_btn = st.button("⚡ Generate Gap Drill Questions", type="primary", use_container_width=True)

        if gen_drill_btn:
            km = KeyManager()
            if custom_key.strip():
                km.add_key(custom_key.strip())

            if not km.keys:
                st.error(
                    "🔑 **Google Gemini API Key Required**\n\n"
                    "Please enter your Gemini API key in the sidebar under **⚙️ Engine Settings** to generate interview questions.\n\n"
                    "👉 [Click here to get a free key from Google AI Studio](https://aistudio.google.com/app/apikey) (Takes 30 seconds, 100% free)."
                )
                return

            agent = JobSearchAgent(key_manager=km, model=model_name)
            current_resume = st.session_state.get("base_resume_text", "Experienced developer with Python, FastAPI, and SQL background.")

            with st.spinner("Synthesizing tough recruiter questions..."):
                try:
                    mock_roadmap = agent.generate_employability_roadmap(
                        base_resume=current_resume,
                        target_role=custom_role,
                        budget_preference="All Tiers"
                    )
                    st.session_state["employability_roadmap"] = mock_roadmap
                    roadmap = mock_roadmap
                    st.success("✅ Questions Generated!")
                except Exception as e:
                    st.error(f"Error: {e}")
                    return

    if roadmap and roadmap.interview_gap_questions:
        st.markdown(f"### 🎯 Drills for Target Role: **{roadmap.target_role}**")
        st.caption(f"Showing {len(roadmap.interview_gap_questions)} high-stakes interview questions designed to probe weak spots.")

        for q_idx, q in enumerate(roadmap.interview_gap_questions, 1):
            with st.container():
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:1.2rem; margin-bottom:1rem; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                        <span style="background:#fee2e2; color:#991b1b; padding:0.2rem 0.6rem; border-radius:9999px; font-size:0.75rem; font-weight:700;">
                            Gap Probed: {q.skill_gap}
                        </span>
                        <span style="font-size:0.8rem; color:#94a3b8; font-weight:600;">Question #{q_idx}</span>
                    </div>
                    <h3 style="margin:0.4rem 0 0.6rem 0; color:#0f172a;">"{q.question}"</h3>
                    <div style="background:#f8fafc; border-left:3px solid #3b82f6; padding:0.8rem; border-radius:6px; margin-bottom:0.6rem;">
                        <b style="color:#1e40af;">🔍 What the Recruiter is Really Testing:</b><br>
                        <span style="font-size:0.9rem; color:#334155;">{q.recruiter_intent}</span>
                    </div>
                    <div style="background:#f0fdf4; border-left:3px solid #10b981; padding:0.8rem; border-radius:6px; margin-bottom:0.6rem;">
                        <b style="color:#065f46;">💡 Recommended STAR Response Framework:</b><br>
                        <span style="font-size:0.9rem; color:#064e3b;">{q.recommended_star_response}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"✍️ Practice Answering Question #{q_idx} & Get AI Feedback"):
                    user_answer = st.text_area(
                        "Your practice response (aim for Situation, Task, Action, Result):",
                        key=f"user_ans_{q_idx}",
                        height=120,
                        placeholder="In my previous role at Company X, we faced a situation where... My task was... I took action by... As a result..."
                    )
                    eval_btn = st.button("Evaluate My Answer", key=f"eval_btn_{q_idx}")

                    if eval_btn:
                        if not user_answer.strip():
                            st.warning("Please type your response first.")
                        else:
                            km = KeyManager()
                            if custom_key.strip():
                                km.add_key(custom_key.strip())
                            agent = JobSearchAgent(key_manager=km, model=model_name)

                            with st.spinner("Recruiter evaluating your answer..."):
                                prompt = f"""You are a Tough Tech Hiring Manager. Evaluate this candidate's interview answer.
Question: {q.question}
Skill Gap Probed: {q.skill_gap}
Recruiter Intent: {q.recruiter_intent}

Candidate Draft Response:
\"\"\"{user_answer}\"\"\"

Provide:
1. Overall Rating: (Needs Work / Good / Exceptional)
2. Strengths: What was done well
3. Flaws / Red Flags: What sounded unconvincing, defensive, or lacking in specifics
4. Polished Re-write: A 1-paragraph refined version showcasing how to answer with confidence
"""
                                try:
                                    def _run(client):
                                        res = client.models.generate_content(
                                            model=agent.model,
                                            contents=prompt
                                        )
                                        return res.text
                                    feedback = km.execute_with_retry(_run)
                                    st.markdown("#### 🤖 AI Recruiter Feedback:")
                                    st.markdown(feedback)
                                except Exception as e:
                                    st.error(f"Feedback evaluation failed: {e}")
