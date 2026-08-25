"""
HTML, Markdown, and PDF Rendering Engine with WeasyPrint and Headless Chromium/Edge Fallback.
"""
import os
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader

from src.schema import (
    TailoredResumePayload,
    CoverLetterPayload,
    JobAnalysis,
    MatchEvaluation,
    ReviewFeedback
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


class Renderer:
    """Renders resume and cover letter payloads into HTML, Markdown, and PDF formats."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    # -----------------------------------------------------------------------
    # HTML Rendering
    # -----------------------------------------------------------------------

    def render_resume_html(self, payload: TailoredResumePayload) -> str:
        """Render TailoredResumePayload to HTML."""
        template = self.jinja_env.get_template("resume_template.html")
        return template.render(payload=payload)

    def render_cover_letter_html(self, payload: CoverLetterPayload) -> str:
        """Render CoverLetterPayload to HTML."""
        template = self.jinja_env.get_template("cover_letter.html")
        date_str = datetime.now().strftime("%B %d, %Y")
        return template.render(payload=payload, date_str=date_str)

    # -----------------------------------------------------------------------
    # Markdown Rendering
    # -----------------------------------------------------------------------

    @staticmethod
    def render_resume_markdown(payload: TailoredResumePayload) -> str:
        """Render TailoredResumePayload into clean, formatted Markdown."""
        lines = []
        c = payload.contact_info
        lines.append(f"# {c.full_name}")
        
        contacts = []
        if c.email:
            contacts.append(f"Email: {c.email}")
        if c.phone:
            contacts.append(f"Phone: {c.phone}")
        if c.location:
            contacts.append(f"Location: {c.location}")
        if c.linkedin:
            contacts.append(f"[LinkedIn]({c.linkedin})")
        if c.github:
            contacts.append(f"[GitHub]({c.github})")
        if c.website:
            contacts.append(f"[Portfolio]({c.website})")
        
        lines.append(" | ".join(contacts))
        lines.append("\n---\n")

        if payload.summary:
            lines.append("## Professional Summary")
            lines.append(payload.summary)
            lines.append("")

        if payload.work_experience:
            lines.append("## Professional Experience")
            for exp in payload.work_experience:
                loc = f" ({exp.location})" if exp.location else ""
                lines.append(f"### {exp.role} | **{exp.company}**{loc}")
                lines.append(f"*{exp.dates}*")
                lines.append("")
                for bullet in exp.achievements:
                    lines.append(f"- {bullet}")
                lines.append("")

        if payload.technical_skills:
            lines.append("## Technical Skills")
            for item in payload.technical_skills:
                if hasattr(item, "category") and hasattr(item, "skills"):
                    lines.append(f"- **{item.category}:** {', '.join(item.skills)}")
                elif isinstance(item, dict):
                    cat = item.get("category", "")
                    sks = item.get("skills", [])
                    lines.append(f"- **{cat}:** {', '.join(sks)}")
            lines.append("")

        if payload.education:
            lines.append("## Education")
            for edu in payload.education:
                lines.append(f"- **{edu.degree}** – {edu.institution} (*{edu.graduation_year}*)")
                if edu.details:
                    lines.append(f"  - {edu.details}")
            lines.append("")

        if payload.certifications_or_projects:
            lines.append("## Projects & Certifications")
            for item in payload.certifications_or_projects:
                url_str = f" [[Link]({item.url})]" if item.url else ""
                lines.append(f"- **{item.name}**{url_str}: {item.description}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def render_cover_letter_markdown(payload: CoverLetterPayload) -> str:
        """Render CoverLetterPayload into clean Markdown."""
        date_str = datetime.now().strftime("%B %d, %Y")
        lines = [
            f"# Cover Letter - {payload.sender_name}",
            f"**Application for:** {payload.job_title} at {payload.company}",
            f"**Date:** {date_str}",
            f"**To:** {payload.recipient_name} ({payload.company})",
            "\n---\n",
            f"Dear {payload.recipient_name},",
            "",
            payload.opening_paragraph,
            ""
        ]
        for para in payload.body_paragraphs:
            lines.append(para)
            lines.append("")
        lines.append(payload.call_to_action)
        lines.append("")
        lines.append("Sincerely,")
        lines.append(f"**{payload.sender_name}**")
        return "\n".join(lines)

    # -----------------------------------------------------------------------
    # PDF Rendering with Headless Browser Fallback
    # -----------------------------------------------------------------------

    @staticmethod
    def render_pdf_from_html(html_path: Path, output_pdf_path: Path) -> bool:
        """
        Convert HTML to PDF. First attempts WeasyPrint. If GTK libraries are missing
        (common on Windows), falls back to native Edge / Chrome headless print-to-pdf.
        """
        # Try WeasyPrint
        try:
            from weasyprint import HTML
            HTML(filename=str(html_path)).write_pdf(str(output_pdf_path))
            if output_pdf_path.exists() and output_pdf_path.stat().st_size > 0:
                return True
        except Exception as e:
            pass  # Fallback to headless browser

        # Fallback: Find Microsoft Edge or Google Chrome executable
        browser_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            shutil.which("msedge"),
            shutil.which("chrome"),
            shutil.which("chromium")
        ]

        valid_browser = next((p for p in browser_paths if p and os.path.exists(p)), None)

        if valid_browser:
            try:
                cmd = [
                    valid_browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    f"--print-to-pdf={str(output_pdf_path.resolve())}",
                    str(html_path.resolve().as_uri())
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
                if output_pdf_path.exists() and output_pdf_path.stat().st_size > 0:
                    return True
            except Exception as e:
                print(f"[Warning] Headless browser PDF compilation failed: {e}")

        return False

    # -----------------------------------------------------------------------
    # Comprehensive Export Pipeline
    # -----------------------------------------------------------------------

    def export_all(
        self,
        output_dir: Path,
        job_analysis: JobAnalysis,
        match_evaluation: MatchEvaluation,
        tailored_resume: TailoredResumePayload,
        cover_letter: CoverLetterPayload,
        review_feedback: Optional[ReviewFeedback] = None,
        generate_pdf: bool = True
    ) -> Dict[str, Path]:
        """
        Exports all artifacts (JSON, Markdown, HTML, PDF) to output_dir.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        artifacts = {}

        # 1. Export Analysis JSON
        analysis_data = {
            "job_analysis": job_analysis.model_dump(),
            "match_evaluation": match_evaluation.model_dump(),
            "review_feedback": review_feedback.model_dump() if review_feedback else None,
            "exported_at": datetime.now().isoformat()
        }
        analysis_json_path = output_dir / "analysis.json"
        analysis_json_path.write_text(json.dumps(analysis_data, indent=2), encoding="utf-8")
        artifacts["analysis_json"] = analysis_json_path

        # 2. Render Resume Files
        resume_md = self.render_resume_markdown(tailored_resume)
        resume_md_path = output_dir / "tailored_resume.md"
        resume_md_path.write_text(resume_md, encoding="utf-8")
        artifacts["resume_md"] = resume_md_path

        resume_html = self.render_resume_html(tailored_resume)
        resume_html_path = output_dir / "tailored_resume.html"
        resume_html_path.write_text(resume_html, encoding="utf-8")
        artifacts["resume_html"] = resume_html_path

        if generate_pdf:
            resume_pdf_path = output_dir / "tailored_resume.pdf"
            if self.render_pdf_from_html(resume_html_path, resume_pdf_path):
                artifacts["resume_pdf"] = resume_pdf_path

        # 3. Render Cover Letter Files
        cover_md = self.render_cover_letter_markdown(cover_letter)
        cover_md_path = output_dir / "cover_letter.md"
        cover_md_path.write_text(cover_md, encoding="utf-8")
        artifacts["cover_letter_md"] = cover_md_path

        cover_html = self.render_cover_letter_html(cover_letter)
        cover_html_path = output_dir / "cover_letter.html"
        cover_html_path.write_text(cover_html, encoding="utf-8")
        artifacts["cover_letter_html"] = cover_html_path

        if generate_pdf:
            cover_pdf_path = output_dir / "cover_letter.pdf"
            if self.render_pdf_from_html(cover_html_path, cover_pdf_path):
                artifacts["cover_letter_pdf"] = cover_pdf_path

        return artifacts
