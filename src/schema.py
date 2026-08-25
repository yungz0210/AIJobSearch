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
