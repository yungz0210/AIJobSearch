"""
Multi-Agent Orchestration Engine powered by Gemini 3.7 Flash and Google GenAI SDK.
Includes thread-safe rotatable API key pool and iterative ATS review loop.
"""
import os
import json
import time
import logging
from typing import List, Optional, Tuple, Callable
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.schema import (
    JobAnalysis,
    MatchEvaluation,
    TailoredResumePayload,
    CoverLetterPayload,
    ReviewFeedback,
    MarketDemandReport,
    EmployabilityRoadmap
)

load_dotenv()
logger = logging.getLogger("AIJobSearch.Agent")


# ---------------------------------------------------------------------------
# Rotatable API Key Manager
# ---------------------------------------------------------------------------

class KeyManager:
    """Manages a pool of Google Gemini API keys with automatic rotation on rate limits."""

    def __init__(self, api_keys: Optional[List[str]] = None):
        self.keys: List[str] = []
        if api_keys:
            self.keys.extend([k.strip() for k in api_keys if k and k.strip()])
        
        # Also read from environment or Streamlit secrets
        env_keys = os.getenv("GEMINI_API_KEYS", "") or os.getenv("GEMINI_API_KEY", "")
        
        # Check Streamlit Cloud secrets if available
        if not env_keys:
            try:
                import streamlit as st
                if hasattr(st, "secrets"):
                    env_keys = st.secrets.get("GEMINI_API_KEYS", "") or st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                pass

        if env_keys:
            for k in str(env_keys).split(","):
                k_clean = k.strip()
                if k_clean and k_clean not in self.keys:
                    self.keys.append(k_clean)

        self.current_index = 0

    def add_key(self, key: str):
        """Add a new API key to the active rotation pool."""
        clean = key.strip()
        if clean and clean not in self.keys:
            self.keys.append(clean)

    def get_client(self) -> genai.Client:
        """Get a GenAI client initialized with the current active key."""
        if not self.keys:
            # Fall back to default environment resolution
            return genai.Client()
        current_key = self.keys[self.current_index % len(self.keys)]
        return genai.Client(api_key=current_key)

    def rotate(self) -> str:
        """Rotate to the next API key in the pool."""
        if not self.keys:
            return "default"
        self.current_index = (self.current_index + 1) % len(self.keys)
        new_key = self.keys[self.current_index]
        logger.warning(f"🔄 Rotated to Gemini API Key #{self.current_index + 1} (...{new_key[-6:] if len(new_key) > 6 else '***'})")
        return new_key

    def execute_with_retry(self, fn: Callable[[genai.Client], any], max_retries: int = 8) -> any:
        """
        Execute a GenAI API call with automatic key rotation and exponential backoff
        upon 429/ResourceExhausted, 503/Unavailable, or transient server errors.
        """
        attempts = 0
        while attempts < max_retries:
            client = self.get_client()
            try:
                return fn(client)
            except Exception as e:
                err_str = str(e).lower()
                is_retryable = any(term in err_str for term in [
                    "429", "503", "500", "502", "504", "resource_exhausted", "quota",
                    "rate limit", "overloaded", "exhausted", "unavailable", "high demand", "bandwidth"
                ])
                if is_retryable:
                    backoff = min(2.0 * (1.5 ** attempts), 12.0)
                    if len(self.keys) > 1:
                        self.rotate()
                    logger.warning(f"Transient API notice ({e}). Waiting {backoff:.1f}s before retry #{attempts + 1}...")
                    time.sleep(backoff)
                    attempts += 1
                else:
                    logger.error(f"GenAI Call Error: {e}")
                    if attempts < 2:
                        time.sleep(2.0)
                        attempts += 1
                        continue
                    raise e

        raise RuntimeError(f"Exceeded maximum API retries ({max_retries}).")


# ---------------------------------------------------------------------------
# Multi-Agent Workflow Engine
# ---------------------------------------------------------------------------

class JobSearchAgent:
    """
    Orchestrates the 3-pass multi-agent workflow:
      PASS 1: Scraper & Job Evaluator
      PASS 2: Resume & Cover Letter Drafter
      PASS 3: ATS Validator & Reviewer Refinement Loop
    """

    def __init__(self, key_manager: Optional[KeyManager] = None, model: Optional[str] = None):
        self.km = key_manager or KeyManager()
        self.model = model or os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"
        # Fallback models in case of temporary 503 high demand or 429 quota exhaustion
        self.fallback_models = ["gemini-3.6-flash", "gemini-3.5-flash"]

    def _call_structured_gemini(self, prompt: str, schema_cls: type, system_instruction: Optional[str] = None) -> any:
        """Helper to invoke Gemini with rigid Pydantic JSON schema."""
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]

        for model_candidate in models_to_try:
            try:
                def _invoke(client: genai.Client):
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=schema_cls,
                        temperature=0.2,
                        system_instruction=system_instruction
                    )
                    response = client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                        config=config
                    )
                    raw_text = response.text
                    return schema_cls.model_validate_json(raw_text)

                return self.km.execute_with_retry(_invoke, max_retries=2)
            except Exception as e:
                err_str = str(e).lower()
                is_last_model = (model_candidate == models_to_try[-1])
                if not is_last_model and any(term in err_str for term in [
                    "503", "unavailable", "high demand", "429", "quota", "resource_exhausted", "exceeded maximum api retries", "rate limit"
                ]):
                    next_model = models_to_try[models_to_try.index(model_candidate)+1]
                    logger.warning(f"Model {model_candidate} issue ({e}). Auto-switching to fallback model {next_model}...")
                    continue
                raise e


    # -----------------------------------------------------------------------
    # PASS 1: Job Analysis & Match Evaluation
    # -----------------------------------------------------------------------

    def analyze_job(self, job_text: str) -> JobAnalysis:
        """Extract structured requirements, skills, and duties from job posting."""
        system_instruction = (
            "You are an expert Technical Talent Sourcer. Analyze the provided job posting "
            "and extract hard skills, soft skills, key responsibilities, target experience level, "
            "and company details with utmost precision."
        )
        prompt = f"""Extract structured information from this job posting:

--- JOB POSTING ---
{job_text}
-------------------
"""
        return self._call_structured_gemini(prompt, JobAnalysis, system_instruction)

    def evaluate_match(self, job_analysis: JobAnalysis, base_resume: str) -> MatchEvaluation:
        """Evaluate candidate profile against target job requirements."""
        system_instruction = (
            "You are a rigorous Technical Hiring Committee Member. Evaluate the candidate's base "
            "profile against the target job requirements. Score honestly (0-100), identify exact "
            "matching strengths, point out gaps, and devise an ethical alignment strategy to bridge gaps."
        )
        prompt = f"""Compare the Candidate Base Profile against the Target Job Analysis.

--- TARGET JOB ANALYSIS ---
Title: {job_analysis.title}
Company: {job_analysis.company}
Experience Level: {job_analysis.experience_level}
Hard Skills: {', '.join(job_analysis.hard_skills)}
Soft Skills: {', '.join(job_analysis.soft_skills)}
Key Responsibilities: {', '.join(job_analysis.key_responsibilities)}

--- CANDIDATE BASE PROFILE ---
{base_resume}
------------------------------

Generate a comprehensive match evaluation and alignment strategy.
"""
        return self._call_structured_gemini(prompt, MatchEvaluation, system_instruction)

    # -----------------------------------------------------------------------
    # PASS 2: Drafter Agent (Resume & Cover Letter)
    # -----------------------------------------------------------------------

    def draft_tailored_resume(
        self,
        job_analysis: JobAnalysis,
        match_evaluation: MatchEvaluation,
        base_resume: str,
        feedback: Optional[ReviewFeedback] = None
    ) -> TailoredResumePayload:
        """
        Draft a high-impact, ATS-optimized 1-page resume payload.
        Strict rule: Do NOT hallucinate jobs, dates, or titles. Reframe authentic accomplishments using the XYZ formula.
        """
        system_instruction = (
            "You are an Elite Executive Resume Strategist specializing in ATS-optimized, high-conversion tech resumes. "
            "RULES:\n"
            "1. STRICT TRUTH: Do NOT invent employment history, fake degrees, companies, or dates. Use only the candidate's authentic background.\n"
            "2. IMPACT FORMULA: Rewrite bullet points using the Google XYZ formula ('Accomplished [X] as measured by [Y], by doing [Z]').\n"
            "3. KEYWORD ALIGNMENT: Incorporate relevant hard skills and keywords from the target job where the candidate has genuine experience.\n"
            "4. 1-PAGE CONCISENESS: Keep descriptions tight, high-density, and impactful."
        )

        feedback_section = ""
        if feedback:
            feedback_section = f"""
--- PREVIOUS ATS CRITIQUE & REQUIRED IMPROVEMENTS ---
ATS Score: {feedback.ats_score}/100
Critique: {feedback.critique}
Actionable Suggestions:
{json.dumps(feedback.suggestions, indent=2)}
Please thoroughly address all critique and suggestions in this refined version!
---------------------------------------------------
"""

        prompt = f"""Draft a tailored, 1-page structured resume payload for the target role.

--- TARGET JOB ---
Title: {job_analysis.title}
Company: {job_analysis.company}
Target Hard Skills: {', '.join(job_analysis.hard_skills)}
Target Soft Skills: {', '.join(job_analysis.soft_skills)}

--- MATCH STRATEGY ---
Alignment Strategy: {match_evaluation.alignment_strategy}
Matching Qualifications: {', '.join(match_evaluation.matching_qualifications)}

--- CANDIDATE BASE PROFILE ---
{base_resume}
{feedback_section}

Generate the complete TailoredResumePayload.
"""
        return self._call_structured_gemini(prompt, TailoredResumePayload, system_instruction)

    def draft_cover_letter(
        self,
        job_analysis: JobAnalysis,
        match_evaluation: MatchEvaluation,
        tailored_resume: TailoredResumePayload,
        feedback: Optional[ReviewFeedback] = None
    ) -> CoverLetterPayload:
        """Draft an authentic, compelling corporate cover letter matching the target role."""
        system_instruction = (
            "You are a top-tier Executive Communications Coach. Draft a compelling, modern, "
            "authentic cover letter. Avoid cliché corporate fluff ('I am writing to express my enthusiasm...'). "
            "Open with a strong value-hook, highlight 2-3 specific quantifiable achievements directly relevant "
            "to the role's challenges, and close with a confident, proactive call to action."
        )

        feedback_section = ""
        if feedback:
            feedback_section = f"""
--- PREVIOUS ATS CRITIQUE ---
Critique: {feedback.critique}
Suggestions: {', '.join(feedback.suggestions)}
Address these points in the revised cover letter.
----------------------------
"""

        prompt = f"""Draft a tailored CoverLetterPayload for:

Candidate: {tailored_resume.contact_info.full_name}
Target Role: {job_analysis.title}
Company: {job_analysis.company}
Key Skills to Highlight: {', '.join(job_analysis.hard_skills[:6])}
Alignment Strategy: {match_evaluation.alignment_strategy}
Summary Pitch: {tailored_resume.summary}
{feedback_section}

Generate the complete CoverLetterPayload.
"""
        return self._call_structured_gemini(prompt, CoverLetterPayload, system_instruction)

    # -----------------------------------------------------------------------
    # PASS 3: Reviewer & ATS Validator Agent
    # -----------------------------------------------------------------------

    def review_application(
        self,
        job_analysis: JobAnalysis,
        tailored_resume: TailoredResumePayload,
        cover_letter: CoverLetterPayload
    ) -> ReviewFeedback:
        """Simulate an ATS algorithm & Senior Executive Recruiter to grade the application."""
        system_instruction = (
            "You are an Elite Executive Recruiter and ATS Validation Algorithm. "
            "Strictly evaluate the drafted resume and cover letter against the target job requirements.\n"
            "- Grade the ATS readiness & keyword match score (0 to 100).\n"
            "- Set pass_review = True ONLY if score >= 85 AND achievements feature strong metric outcomes.\n"
            "- Provide critical, constructive feedback on weak action verbs, keyword gaps, or tone."
        )

        prompt = f"""Review the tailored application materials:

--- TARGET JOB ---
Title: {job_analysis.title} at {job_analysis.company}
Required Hard Skills: {', '.join(job_analysis.hard_skills)}
Key Responsibilities: {', '.join(job_analysis.key_responsibilities)}

--- DRAFTED RESUME SUMMARY & HIGHLIGHTS ---
Candidate: {tailored_resume.contact_info.full_name}
Summary: {tailored_resume.summary}
Technical Skills: {json.dumps([s.model_dump() for s in tailored_resume.technical_skills])}
Experience Highlights:
{json.dumps([{'role': exp.role, 'company': exp.company, 'achievements': exp.achievements} for exp in tailored_resume.work_experience], indent=2)}

--- DRAFTED COVER LETTER ---
Opening: {cover_letter.opening_paragraph}
Body: {json.dumps(cover_letter.body_paragraphs)}
Closing: {cover_letter.call_to_action}

Perform a rigorous evaluation and output the ReviewFeedback.
"""
        return self._call_structured_gemini(prompt, ReviewFeedback, system_instruction)

    # -----------------------------------------------------------------------
    # Orchestrated Pipeline with Iterative Refinement
    # -----------------------------------------------------------------------

    def run_pipeline(
        self,
        job_raw_text: str,
        base_resume_text: str,
        max_refinement_retries: int = 2,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> Tuple[JobAnalysis, MatchEvaluation, TailoredResumePayload, CoverLetterPayload, ReviewFeedback]:
        """
        Execute the full multi-pass pipeline with feedback refinement loop.
        """
        def update_progress(msg: str, step: int):
            logger.info(f"[{step}/5] {msg}")
            if progress_callback:
                progress_callback(msg, step)

        # PASS 1: Analyze & Match
        update_progress("Analyzing Target Job Description...", 1)
        job_analysis = self.analyze_job(job_raw_text)

        update_progress("Evaluating Candidate Match & Strategic Alignment...", 2)
        match_evaluation = self.evaluate_match(job_analysis, base_resume_text)

        # PASS 2: Initial Draft
        update_progress("Drafting ATS-Optimized 1-Page Resume & Cover Letter...", 3)
        tailored_resume = self.draft_tailored_resume(job_analysis, match_evaluation, base_resume_text)
        cover_letter = self.draft_cover_letter(job_analysis, match_evaluation, tailored_resume)

        # PASS 3: Reviewer & ATS Validator
        update_progress("Running ATS Recruiter & Keyword Validation...", 4)
        review = self.review_application(job_analysis, tailored_resume, cover_letter)

        # Iterative Refinement Loop
        iteration = 0
        while (not review.pass_review or review.ats_score < 85) and iteration < max_refinement_retries:
            iteration += 1
            update_progress(f"Refining application based on ATS feedback (Iteration {iteration}/{max_refinement_retries}, Score: {review.ats_score}%)...", 4)
            tailored_resume = self.draft_tailored_resume(job_analysis, match_evaluation, base_resume_text, feedback=review)
            cover_letter = self.draft_cover_letter(job_analysis, match_evaluation, tailored_resume, feedback=review)
            review = self.review_application(job_analysis, tailored_resume, cover_letter)

        update_progress("Finalizing Application Artifacts...", 5)
        return job_analysis, match_evaluation, tailored_resume, cover_letter, review

    # -----------------------------------------------------------------------
    # PASS 4: Market Demand Intelligence & Macro Trend Analyzer
    # -----------------------------------------------------------------------

    def analyze_market_demand(
        self,
        query: str,
        location: str,
        sample_size: int,
        market_corpus: str
    ) -> MarketDemandReport:
        """
        Synthesizes a representative sample of active job listings into a
        structured market intelligence report on in-demand skills, salary, and trends.
        """
        system_instruction = (
            "You are a Chief Labor Market Economist & Senior Technical Talent Strategist specializing in the "
            "technology ecosystem (Southeast Asia, Malaysia, and Global Tech). You analyze live job postings "
            "to extract accurate skill demand frequencies, must-have prerequisites vs. emerging differentiators, "
            "market compensation insights, and actionable hiring trends."
        )

        corpus_section = market_corpus.strip() if market_corpus and market_corpus.strip() else (
            f"Note: Direct live postings were limited; utilize verified 2026 market benchmarks for '{query}' in '{location}'."
        )

        prompt = f"""Synthesize labor market demand for:
Target Role: {query}
Geographic Hub: {location}
Sample Postings Analyzed: {sample_size}

--- SCANNED MARKET POSTINGS DATA ---
{corpus_section}
-----------------------------------

Extract and produce a comprehensive MarketDemandReport:
1. Identify the top 8-15 technical hard skills with accurate relative frequency scores (0-100), importance tags, and real use cases.
2. Highlight key soft skills and emerging/breakout tools.
3. Detail experience expectations across Junior, Mid, and Senior tiers.
4. Provide realistic compensation insights (incorporating local currency e.g. MYR / USD / SGD where appropriate).
5. List active hiring companies or major industry sectors.
"""
        return self._call_structured_gemini(prompt, MarketDemandReport, system_instruction)

    # -----------------------------------------------------------------------
    # PASS 5: Employability Diagnostic & Budget-Adaptive Upskilling Engine
    # -----------------------------------------------------------------------

    def generate_employability_roadmap(
        self,
        base_resume: str,
        target_role: str,
        market_report: Optional[MarketDemandReport] = None,
        budget_preference: Optional[str] = None,
        hours_per_week: int = 10
    ) -> EmployabilityRoadmap:
        """
        Diagnoses a candidate's background against market requirements using the Pareto 80/20 rule.
        Generates budget-tiered learning paths (including Malaysian hubs/subsidies),
        portfolio proof-of-work project specs, sprint milestones, and mock interview drills.
        """
        system_instruction = (
            "You are an Elite Career Transition Architect & Technical Engineering Mentor. "
            "You evaluate a candidate's genuine background against real market standards using the Pareto 80/20 principle:\n"
            "1. NO FLUFF: Be brutally honest with the candidate's current readiness score (0-100).\n"
            "2. 80/20 GAP PRIORITIZATION: Classify gaps into:\n"
            "   - 'Tier 1: Deal-Breaker' (auto-rejection risks: must address first)\n"
            "   - 'Tier 2: High-Leverage Booster' (differentiators that yield +20-30% interview callbacks)\n"
            "   - 'Tier 3: Learn-on-the-Job' (acceptable to pick up once hired)\n"
            "3. BUDGET-ADAPTIVE LEARNING: Provide curated resources across 4 distinct tiers:\n"
            "   - Free / RM0 (YouTube, official docs, FreeCodeCamp, open-source)\n"
            "   - Budget (< RM150 / $30) (Udemy sales, Coursera audit/financial aid)\n"
            "   - Professional Certifications (AWS, GCP, CKA, Terraform)\n"
            "   - Physical / Bootcamp / Subsidized Hubs (especially Malaysia: HRD Corp claimable, 42KL, Next Academy, MDEC)\n"
            "4. PROOF-OF-WORK: Suggest 1-2 portfolio project blueprints with system architecture, starter README, and pre-written resume bullet points.\n"
            "5. TOUGH GAP INTERVIEW PREP: Provide questions recruiters ask about their specific weak spots with STAR-method responses."
        )

        market_context_str = ""
        if market_report:
            skills_preview = ', '.join([f'{s.skill_name} ({s.importance})' for s in market_report.top_hard_skills[:10]])
            market_context_str = f"""
--- RECENT MARKET DEMAND INTELLIGENCE ---
Target Query: {market_report.query} in {market_report.location}
Key Market Hard Skills: {skills_preview}
Emerging Trends: {', '.join(market_report.emerging_trends)}
Salary Trends: {market_report.salary_insights}
----------------------------------------
"""

        budget_str = f"Preferred Budget Focus: {budget_preference}\n" if budget_preference else "Provide all 4 budget tiers for each gap.\n"

        prompt = f"""Perform a comprehensive Employability Diagnostic and generate an action-oriented EmployabilityRoadmap:

Target Role / Track: {target_role}
Candidate Available Study Time: {hours_per_week} hours/week
{budget_str}
{market_context_str}

--- CANDIDATE BASE RESUME PROFILE ---
{base_resume}
-------------------------------------

Generate the complete EmployabilityRoadmap.
"""
        return self._call_structured_gemini(prompt, EmployabilityRoadmap, system_instruction)

