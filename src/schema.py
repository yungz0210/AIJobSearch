"""
Rigid Data Schemas for Gemini 3.7 Flash structured JSON outputs using Pydantic v2.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. Job Analysis & Matching Schemas
# ---------------------------------------------------------------------------

class JobAnalysis(BaseModel):
    title: str = Field(..., description="Target job title extracted from the job posting")
    company: str = Field(..., description="Hiring company name")
    hard_skills: List[str] = Field(default_factory=list, description="List of required/preferred hard skills and technical tools")
    soft_skills: List[str] = Field(default_factory=list, description="List of soft skills and leadership traits sought")
    key_responsibilities: List[str] = Field(default_factory=list, description="Core responsibilities and duties of the role")
    experience_level: str = Field(..., description="Target seniority/experience level (e.g. Entry, Mid, Senior, Lead, Staff, Director)")


class MatchEvaluation(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Match score between 0 and 100 based on candidate qualification overlap")
    matching_qualifications: List[str] = Field(default_factory=list, description="Key candidate strengths and experiences that directly match the job")
    missing_gaps: List[str] = Field(default_factory=list, description="Skills, qualifications, or requirements missing or underrepresented in the base profile")
    alignment_strategy: str = Field(..., description="Strategic positioning on how to highlight relevant achievements to bridge gaps without fabricating facts")


# ---------------------------------------------------------------------------
# 2. Resume Schemas
# ---------------------------------------------------------------------------

class ContactInfo(BaseModel):
    full_name: str = Field(..., description="Candidate's full name")
    email: str = Field(..., description="Candidate's email address")
    phone: Optional[str] = Field(default="", description="Candidate's phone number")
    location: Optional[str] = Field(default="", description="Candidate's location (City, State/Country)")
    linkedin: Optional[str] = Field(default="", description="LinkedIn profile URL or handle")
    github: Optional[str] = Field(default="", description="GitHub profile URL or handle")
    website: Optional[str] = Field(default="", description="Personal website or portfolio URL")


class WorkExperienceItem(BaseModel):
    company: str = Field(..., description="Company or organization name")
    role: str = Field(..., description="Job title / role held")
    dates: str = Field(..., description="Employment duration (e.g., 'Jan 2022 – Present')")
    location: Optional[str] = Field(default="", description="Job location or Remote status")
    achievements: List[str] = Field(
        ...,
        description="High-impact bullet points using action verbs + metrics + business outcomes (XYZ formula)"
    )


class EducationItem(BaseModel):
    institution: str = Field(..., description="University, College, or Institution name")
    degree: str = Field(..., description="Degree and major (e.g. 'B.S. in Computer Science')")
    graduation_year: str = Field(..., description="Graduation year or date range (e.g. '2020')")
    details: Optional[str] = Field(default="", description="GPA, Honors, Dean's List, or relevant coursework if applicable")


class ProjectItem(BaseModel):
    name: str = Field(..., description="Project or Certification title")
    description: str = Field(..., description="Brief description of impact, technologies used, or credential details")
    url: Optional[str] = Field(default="", description="Project repository, demo link, or credential URL")


class SkillCategory(BaseModel):
    category: str = Field(..., description="Category name (e.g., 'Languages', 'AI & Machine Learning', 'Cloud & Infrastructure')")
    skills: List[str] = Field(..., description="List of skills in this category")


class TailoredResumePayload(BaseModel):
    contact_info: ContactInfo = Field(..., description="Contact details")
    summary: str = Field(..., description="Concise, 2-3 sentence tailored executive summary highlighting core value proposition for this specific role")
    work_experience: List[WorkExperienceItem] = Field(..., description="Chronological work experiences with tailored, high-impact bullet points")
    technical_skills: List[SkillCategory] = Field(
        ...,
        description="Categorized technical & professional skills"
    )
    education: List[EducationItem] = Field(default_factory=list, description="Education history")
    certifications_or_projects: List[ProjectItem] = Field(default_factory=list, description="Key projects or certifications relevant to the target role")


# ---------------------------------------------------------------------------
# 3. Cover Letter Schemas
# ---------------------------------------------------------------------------

class CoverLetterPayload(BaseModel):
    sender_name: str = Field(..., description="Candidate's full name")
    recipient_name: str = Field(default="Hiring Team", description="Name of recipient or 'Hiring Manager' / 'Hiring Team'")
    company: str = Field(..., description="Target company name")
    job_title: str = Field(..., description="Target position title")
    opening_paragraph: str = Field(..., description="Compelling opening hook introducing candidate interest, role, and overarching value")
    body_paragraphs: List[str] = Field(..., description="2-3 focused paragraphs demonstrating specific relevant achievements and cultural/technical fit")
    call_to_action: str = Field(..., description="Professional closing paragraph with call-to-action and enthusiasm for next steps")


# ---------------------------------------------------------------------------
# 4. Reviewer / ATS Feedback Schemas
# ---------------------------------------------------------------------------

class ReviewFeedback(BaseModel):
    pass_review: bool = Field(..., description="True if resume and cover letter meet high ATS standards (score >= 85) and have strong action verbs/keywords")
    ats_score: int = Field(..., ge=0, le=100, description="ATS readiness & keyword match score (0-100)")
    critique: str = Field(..., description="Executive recruiter critique of phrasing, impact, missing keywords, and flow")
    suggestions: List[str] = Field(default_factory=list, description="Concrete improvement points for the next drafting iteration")


# ---------------------------------------------------------------------------
# 5. Market Demand & Career Intelligence Schemas
# ---------------------------------------------------------------------------

class MarketSkillDemand(BaseModel):
    skill_name: str = Field(..., description="Name of the skill, tool, or technology")
    frequency_score: int = Field(..., ge=0, le=100, description="Relative demand intensity (0-100) across scanned job openings")
    importance: str = Field(..., description="'Core / Must-Have', 'High-Demand', or 'Emerging / Differentiator'")
    category: str = Field(..., description="Category (e.g. 'Languages', 'Frameworks & Libraries', 'Cloud & DevOps', 'Databases', 'AI & Machine Learning')")
    sample_use_cases: List[str] = Field(default_factory=list, description="Concrete real-world applications mentioned in job postings")


class ExperienceTierExpectation(BaseModel):
    band: str = Field(..., description="Seniority band (e.g. 'Junior / Entry', 'Mid-Level', 'Senior / Lead')")
    expectation: str = Field(..., description="Key technical, ownership, and experience expectations")


class MarketDemandReport(BaseModel):
    query: str = Field(..., description="Job role or search query analyzed")
    location: str = Field(..., description="Target geographic hub analyzed")
    sample_size: int = Field(..., description="Number of job postings synthesized")
    market_summary: str = Field(..., description="Executive market overview summarizing hiring velocity, tech stack trends, and talent expectations")
    top_hard_skills: List[MarketSkillDemand] = Field(default_factory=list, description="Ranked list of technical skills in highest demand")
    top_soft_skills: List[str] = Field(default_factory=list, description="Crucial soft skills, teamwork, or leadership competencies sought")
    emerging_trends: List[str] = Field(default_factory=list, description="Breakout tools, libraries, or architectural paradigms on the rise")
    experience_expectations: List[ExperienceTierExpectation] = Field(default_factory=list, description="Typical expectations across Junior, Mid, and Senior bands")
    salary_insights: str = Field(..., description="Estimated market compensation range, trends, or currency breakdown")
    top_hiring_companies: List[str] = Field(default_factory=list, description="Notable companies or industries actively recruiting for this profile")


# ---------------------------------------------------------------------------
# 6. Employability & Upskilling Schemas
# ---------------------------------------------------------------------------

class LearningResource(BaseModel):
    title: str = Field(..., description="Title of course, certification, tutorial, or bootcamp")
    provider: str = Field(..., description="Provider name (e.g. Coursera, Udemy, YouTube / FreeCodeCamp, AWS Official, Next Academy, 42KL)")
    resource_type: str = Field(..., description="'Online Course', 'Professional Certification', 'Documentation / Self-Paced', or 'Physical / Bootcamp Hub'")
    cost_tier: str = Field(..., description="'Free / RM0', 'Budget (< RM150 / $30)', 'Professional Cert (RM400 - RM1,800)', or 'Bootcamp / Subsidized'")
    estimated_duration: str = Field(..., description="Estimated time commitment (e.g. '15 hours', '4 weeks @ 5 hrs/wk')")
    search_url: str = Field(..., description="Direct website, search link, or documentation reference")
    malaysia_subsidy_eligible: bool = Field(default=False, description="True if eligible for HRD Corp, MDEC, or Malaysian governmental upskilling grants")


class SkillGapItem(BaseModel):
    skill: str = Field(..., description="Name of the missing or underrepresented skill")
    tier: str = Field(..., description="'Tier 1: Deal-Breaker' (auto-rejection risk), 'Tier 2: High-Leverage Booster' (+20% match), or 'Tier 3: Learn-on-the-Job'")
    why_it_matters: str = Field(..., description="Why hiring managers mandate or favor this skill for this role")
    learning_pathway: List[LearningResource] = Field(default_factory=list, description="Curated multi-tier learning options tailored to this skill")


class ProofOfWorkProject(BaseModel):
    title: str = Field(..., description="Compelling, portfolio-ready project name")
    target_industry: str = Field(..., description="Target industry vertical (e.g. Fintech, Logistics, Healthcare, E-Commerce)")
    problem_statement: str = Field(..., description="Real-world business or engineering problem this project solves")
    tech_stack: List[str] = Field(default_factory=list, description="Core languages, frameworks, and cloud tools to utilize")
    architecture_overview: str = Field(..., description="System design and architecture description (components, data flow, API design)")
    resume_bullet_point: str = Field(..., description="XYZ-formula bullet point ready to place directly onto a resume once completed")
    github_readme_starter: str = Field(..., description="Markdown starter template for the project repository README")


class InterviewGapQuestion(BaseModel):
    skill_gap: str = Field(..., description="The underlying skill or experience gap being probed")
    question: str = Field(..., description="Realistic, challenging interview question a hiring manager will ask")
    recruiter_intent: str = Field(..., description="What the interviewer is specifically evaluating or trying to uncover")
    recommended_star_response: str = Field(..., description="Recommended response framework using the STAR method (Situation, Task, Action, Result) to ethically reframe experience")


class EmployabilityRoadmap(BaseModel):
    target_role: str = Field(..., description="Target job title or career track analyzed")
    current_readiness_score: int = Field(..., ge=0, le=100, description="Readiness score (0-100) based on current resume vs market benchmarks")
    time_to_ready_estimate: str = Field(..., description="Estimated timeline to achieve 85%+ employability (e.g. '3-5 weeks at 8 hrs/week')")
    executive_summary: str = Field(..., description="High-level strategic diagnosis of candidate positioning and highest-ROI actions")
    skill_gaps: List[SkillGapItem] = Field(default_factory=list, description="Prioritized 80/20 skill gap items with tailored learning resources")
    sprint_30_days: List[str] = Field(default_factory=list, description="Actionable week-by-week sprint milestones for the first 30 days (Tier 1 Deal-Breakers)")
    sprint_60_days: List[str] = Field(default_factory=list, description="Milestones for days 31-60 (Tier 2 High-Leverage Boosters & Project Build)")
    sprint_90_days: List[str] = Field(default_factory=list, description="Milestones for days 61-90 (Interview readiness & targeted applications)")
    portfolio_projects: List[ProofOfWorkProject] = Field(default_factory=list, description="Custom portfolio projects that provide undeniable proof of capability")
    interview_gap_questions: List[InterviewGapQuestion] = Field(default_factory=list, description="Key gap-focused interview questions with STAR answer frameworks")

