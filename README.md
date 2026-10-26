# AI Job Search & Career Acceleration Studio

An autonomous, multi-agent Career Intelligence and Application Generation Platform powered by **Google Gemini 3.8 Flash**, **Google GenAI SDK**, **Pydantic v2**, **Plotly**, and modern document rendering engines.

Directly replicates and significantly expands upon the multi-agent workflow of [ai-job-search](https://github.com/MadsLorentzen/ai-job-search).

---

## 🌟 Key Capabilities

### 1. 📄 Application Studio (1-Click Tailored Applications)
- **Live Multi-Board Job Finder**: Search active job postings directly across **LinkedIn Malaysia**, **Indeed Malaysia**, and **Google Jobs** without needing API keys or accounts.
- **Malaysian Tech Hub Filtering**: Kuala Lumpur, Selangor, Cyberjaya, Penang, Johor Bahru, Singapore, or Remote.
- **Universal Scraping Support**: Paste any posting link (**JobStreet Malaysia**, **LinkedIn**, **Indeed**, **Greenhouse**, **Lever**, **Workday**) or paste raw text.
- **3-Pass Multi-Agent Optimization Pipeline**:
  - **Pass 1 (Evaluator & Scraper):** Extracts requirements (`JobAnalysis`) and computes qualification overlap with gap analysis (`MatchEvaluation`).
  - **Pass 2 (Drafter Agent):** Tailors an ATS-optimized 1-page modern resume (`TailoredResumePayload`) and corporate cover letter (`CoverLetterPayload`) using the **XYZ impact formula** without fabricating facts.
  - **Pass 3 (ATS Validator & Refinement Loop):** Simulates executive recruiters and ATS scanners (`ReviewFeedback`). Iteratively refines content up to target benchmarks ($\ge 85\%$).
- **Multi-Format Export**: PDF, HTML, and Markdown for both resumes and cover letters.

### 2. 📈 Live Market Radar & Skill Pulse
- **Live Market Sampling**: Batch-scrape and synthesize 10–30 live postings across multiple boards in real-time.
- **Quantitative Skill Demand Heatmaps**: Interactive Plotly charts ranking in-demand hard skills by relative market frequency (0–100%).
- **Tiers of In-Demand Tech**: Distinct categorization for **Core / Must-Haves**, **High-Demand**, and **Emerging / Differentiators**.
- **Market Compensation & Hiring Velocity**: Real-time salary ranges (MYR, SGD, USD) and active hiring companies/sectors.

### 3. 🎯 Employability & Upskilling Navigator
- **Pareto 80/20 Gap Diagnosis**: Identifies candidate weak spots and categorizes them into:
  - 🔴 **Tier 1 (Deal-Breakers):** Auto-rejection risks that must be fixed first.
  - 🟡 **Tier 2 (High-Leverage Boosters):** Differentiators that increase interview callbacks by +20–30%.
  - 🟢 **Tier 3 (Learn-on-the-Job):** Competencies acceptable to pick up after hiring.
- **Budget-Adaptive Learning Paths**:
  - **Free / RM0:** Official documentation, high-yield YouTube series (FreeCodeCamp, Traversy), CS50, open-source repos.
  - **Budget (< RM150 / $30):** Udemy bestseller sales, Coursera financial aid/audit modes.
  - **Professional Certifications:** AWS Certified Solutions Architect, Google Cloud, CKA, Terraform.
  - **Physical Hubs & Malaysian Subsidies:** HRD Corp claimable corporate training, MDEC initiatives, 42KL, Next Academy.
- **30 / 60 / 90-Day Career Sprints**: Actionable milestones calibrated to the candidate's available study hours per week.
- **Proof-of-Work Project Blueprints**: Real-world portfolio specs with architecture overviews, starter `README.md` templates, and pre-written XYZ resume bullet points.

### 4. 🎙️ Tough Gap Interview Simulator
- Simulates tough technical and behavioral interview questions targeting the candidate's **exact identified skill gaps**.
- Unpacks what the recruiter is secretly testing (intellectual honesty, transferability, learning agility).
- Provides recommended **STAR-method** (Situation, Task, Action, Result) response frameworks.
- Interactive drill module: Practice your response in-browser and receive instant AI recruiter feedback and ratings.

---

## ⚡ Quick Start Shortcuts (Windows)

| Shortcut | Description | Action |
|---|---|---|
| `run_web.bat` | Launches the interactive multi-page Studio in your browser | **Double-click** `run_web.bat` |
| `run_cli.bat` | Runs CLI pipeline with sample files | **Double-click** `run_cli.bat` |

---

## 🚀 Usage Guide

### 1. Interactive Multi-Page Web Studio (Recommended)

Run:
```bash
streamlit run app.py
# or
python main.py --web
```

Use the modern sidebar to switch between:
- **📄 Application Studio**: Live job search + 1-click tailored resume & cover letter generation.
- **📈 Market Radar & Skill Pulse**: Live market scanning, skill frequency intensity charts, and salary insights.
- **🎯 Employability & Upskilling**: Candidate readiness score, 80/20 gaps, budget-tiered learning pathways, and portfolio project blueprints.
- **🎙️ Tough Gap Interview Simulator**: Practice interview drills addressing your specific weak spots.

---

### 2. Command Line Interface (CLI)

#### Scan live market skill demand:
```bash
python main.py --scan-market "AI Engineer" --location "Kuala Lumpur, Malaysia" --results-count 15
```

#### Run employability diagnostic & upskilling roadmap:
```bash
python main.py --roadmap --resume "Chin Yung Wei Resume - Aug 2026.docx" --target-role "Senior Full Stack Developer"
```

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
python main.py --resume "Chin Yung Wei Resume - Aug 2026.docx" --job "https://my.jobstreet.com/jobs/..."
```

---

## 📁 Output Artifacts Structure

Generated files are saved into `./outputs/`:
```
outputs/
├── analysis.json                  # Parsed job info, match scores, and ATS recruiter critique
├── tailored_resume.pdf            # 1-page modern ATS-optimized resume (Compiled PDF)
├── tailored_resume.html           # Rendered HTML template
├── tailored_resume.md             # Clean Markdown source
├── cover_letter.pdf               # Professional corporate cover letter (Compiled PDF)
├── cover_letter.html              # Rendered HTML template
├── cover_letter.md                # Clean Markdown source
└── market_reports/                # Cached Market Demand Intelligence JSON snapshots
```
