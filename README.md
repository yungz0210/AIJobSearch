# AI Job Search & Application Generation System

An autonomous, multi-agent CLI & Web application powered by **Google Gemini 3.6 Flash** (`gemini-3.6-flash`), **Google GenAI SDK**, **Pydantic v2**, and modern document rendering engines.

Directly replicates and enhances the multi-agent workflow of [ai-job-search](https://github.com/MadsLorentzen/ai-job-search).

---

## 🌟 Key Features

1. **Autonomous Live Job Finder (Malaysia & Global)**:
   - Search active job postings directly across **LinkedIn Malaysia**, **Indeed Malaysia**, and **Google Jobs** without needing API keys or accounts.
   - Filter by Malaysian technology hubs: **Kuala Lumpur**, **Selangor / Cyberjaya / PJ**, **Penang**, **Johor Bahru**, or **Remote**.
   - **⚡ 1-Click Tailor Application**: Click one button on any job card to automatically launch the full multi-agent pipeline and generate tailored resumes and cover letters for that listing.

2. **Direct Input & Universal Scraping Support**:
   - Supports pasting links from **JobStreet Malaysia** (`my.jobstreet.com`), **LinkedIn**, **Indeed**, **Greenhouse**, **Lever**, **Workday**, or pasting the job description text directly.
   - Accepts base resumes in `.docx`, `.pdf`, `.md`, or `.txt`.

3. **Multi-Pass Agent Pipeline**:
   - **Pass 1 (Evaluator & Scraper):** Extracts structured job requirements (`JobAnalysis`) and computes qualification overlap with gap analysis (`MatchEvaluation`).
   - **Pass 2 (Drafter Agent):** Tailors an ATS-optimized 1-page modern resume (`TailoredResumePayload`) and corporate cover letter (`CoverLetterPayload`) using the **XYZ impact formula** without fabricating facts.
   - **Pass 3 (ATS Validator & Refinement Loop):** Simulates executive recruiters and ATS keyword scanners (`ReviewFeedback`). Iteratively refines content up to target benchmarks ($\ge 85\%$).

4. **Fast Generation & Auto-Failover**:
   - Built on blazing fast **`gemini-3.6-flash`** (~1-2s response) with automated failover to `gemini-3.5-flash` on rate limits (`429` / `503`).

5. **Multi-Format Export**:
   - `analysis.json` (Structured qualification match and recruiter critique)
   - `tailored_resume.pdf`, `tailored_resume.html`, `tailored_resume.md`
   - `cover_letter.pdf`, `cover_letter.html`, `cover_letter.md`

---

## ⚡ Quick Start Shortcuts (Windows)

| Shortcut | Description | Action |
|---|---|---|
| `run_web.bat` | Launches the interactive Streamlit Web Studio in your browser | **Double-click** `run_web.bat` |
| `run_cli.bat` | Runs CLI pipeline with sample files | **Double-click** `run_cli.bat` |

---

## 🚀 Usage Guide

### 1. Interactive Web Studio (Recommended)

Run:
```bash
streamlit run app.py
# or
python main.py --web
```

Inside the Web Studio:
- **Tab 1: 🔍 Auto Job Finder (Malaysia & Global)**: Enter your target keywords and Malaysian state/city to browse live openings and click `⚡ 1-Click Tailor`.
- **Tab 2: 📋 Direct Input**: Paste any URL (JobStreet, LinkedIn, etc.) or paste description text to tailor immediately.

---

### 2. Command Line Interface (CLI)

#### Search live jobs in Malaysia:
```bash
python main.py --search-jobs "Software Engineer" --location "Kuala Lumpur, Malaysia" --results-count 5
```

#### Tailor resume for a job posting:
```bash
python main.py --resume "Chin Yung Wei Resume - Aug 2026.docx" --job "test_job.txt"
```

#### Tailor resume from a live job link:
```bash
python main.py --resume "Chin Yung Wei Resume - Aug 2026.docx" --job "https://example.com/job-posting-url"
```

---

## 📁 Output Artifacts Structure

All generated files are saved into `./outputs/`:
```
outputs/
├── analysis.json                  # Parsed job info, match scores, and ATS recruiter critique
├── tailored_resume.pdf            # 1-page modern ATS-optimized resume (Compiled PDF)
├── tailored_resume.html           # Rendered HTML template
├── tailored_resume.md             # Clean Markdown source
├── cover_letter.pdf               # Professional corporate cover letter (Compiled PDF)
├── cover_letter.html              # Rendered HTML template
└── cover_letter.md                # Clean Markdown source
```
