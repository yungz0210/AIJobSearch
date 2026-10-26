"""
AI Job Search & Application Generation CLI
Powered by Gemini 3.6 Flash, Pydantic v2, and Multi-Agent ATS Optimization Engine.
"""
import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from src.parser import InputParser
from src.agent import JobSearchAgent, KeyManager
from src.renderer import Renderer
from src.job_finder import JobFinder

console = Console(force_terminal=True, legacy_windows=False)


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option(
    "--resume", "-r",
    type=str,
    required=False,
    help="Path to candidate resume/CV (.docx, .pdf, .md, .txt) or base profile"
)
@click.option(
    "--job", "-j",
    type=str,
    required=False,
    help="Target job posting (local file path, web URL, or raw text)"
)
@click.option(
    "--search-jobs", "-s",
    type=str,
    required=False,
    help="Search live job openings across Malaysia / Global (e.g. 'Software Engineer')"
)
@click.option(
    "--location", "-l",
    type=str,
    default="Malaysia",
    show_default=True,
    help="Location filter for job search (e.g. 'Kuala Lumpur, Malaysia', 'Selangor, Malaysia')"
)
@click.option(
    "--results-count", "-n",
    type=int,
    default=5,
    show_default=True,
    help="Max number of search results to return"
)
@click.option(
    "--output-dir", "-o",
    type=click.Path(),
    default="./outputs",
    show_default=True,
    help="Directory to save generated JSON, Markdown, HTML, and PDF artifacts"
)
@click.option(
    "--pdf/--no-pdf",
    default=True,
    show_default=True,
    help="Toggle PDF document compilation"
)
@click.option(
    "--model", "-m",
    default="gemini-3.8-flash",
    show_default=True,
    help="Target Gemini model name"
)
@click.option(
    "--max-retries",
    default=1,
    show_default=True,
    help="Maximum ATS review refinement iterations"
)
@click.option(
    "--add-key",
    type=str,
    default=None,
    help="Additional Google Gemini API key to append to rotation pool"
)
@click.option(
    "--scan-market",
    type=str,
    required=False,
    help="Scan live market skill demand and salary trends (e.g. 'AI Engineer')"
)
@click.option(
    "--roadmap",
    is_flag=True,
    default=False,
    help="Generate Employability Diagnostic & Upskilling Roadmap from resume"
)
@click.option(
    "--target-role",
    type=str,
    default="Software Engineer",
    show_default=True,
    help="Target role/track when generating an employability roadmap"
)
@click.option(
    "--web",
    is_flag=True,
    default=False,
    help="Launch the interactive Streamlit Web UI"
)
def cli(resume, job, search_jobs, location, results_count, output_dir, pdf, model, max_retries, add_key, scan_market, roadmap, target_role, web):
    """
    AI Job Search: Autonomous multi-agent pipeline to search live openings,
    analyze job requirements, score candidate match, draft tailored 1-page ATS resumes,
    and generate corporate cover letters.
    """
    if web:
        console.print("[bold cyan]🚀 Launching AI Job Search Web Interface...[/bold cyan]")
        app_path = Path(__file__).parent / "app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
        return

    # If user wants to search live jobs
    if search_jobs:
        console.print(Panel.fit(
            f"[bold cyan]🔍 Searching Live Jobs on LinkedIn, Indeed, Google Jobs[/bold cyan]\n"
            f"[dim]Query: [bold]{search_jobs}[/bold] | Location: [bold]{location}[/bold] | Max: [bold]{results_count}[/bold][/dim]",
            border_style="cyan"
        ))
        with console.status("[bold blue]Querying live job boards...", spinner="dots"):
            listings = JobFinder.search(
                search_term=search_jobs,
                location=location,
                results_wanted=results_count
            )

        if not listings:
            console.print("[yellow]No job openings found matching your criteria.[/yellow]")
            return

        table = Table(title=f"Live Job Openings in {location}", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="center", style="dim")
        table.add_column("Portal", style="bold")
        table.add_column("Job Title", style="cyan")
        table.add_column("Company", style="green")
        table.add_column("Location")
        table.add_column("URL", style="blue")

        for idx, item in enumerate(listings, 1):
            table.add_row(
                str(idx),
                item.site,
                item.title,
                item.company,
                item.location,
                item.job_url or "N/A"
            )

        console.print(table)
        console.print(f"\n[green]💡 Tip:[/green] To auto-tailor for one of these jobs, run:\n"
                      f"[white]python main.py --resume \"Chin Yung Wei Resume - Aug 2026.docx\" --job \"<job_url>\"[/white]\n"
                      f"Or launch the interactive web studio: [cyan]python main.py --web[/cyan]\n")
        return

    # If user wants to scan live market demand
    if scan_market:
        console.print(Panel.fit(
            f"[bold cyan]📈 Scanning Market Demand & Skill Pulse[/bold cyan]\n"
            f"[dim]Role: [bold]{scan_market}[/bold] | Hub: [bold]{location}[/bold] | Samples: [bold]{results_count}[/bold][/dim]",
            border_style="cyan"
        ))
        key_manager = KeyManager()
        if add_key:
            key_manager.add_key(add_key)
        agent = JobSearchAgent(key_manager=key_manager, model=model)

        with console.status("[bold blue]Sampling live postings across LinkedIn, Indeed, and Google Jobs...", spinner="dots"):
            listings, corpus = JobFinder.sample_market_corpus(
                query=scan_market,
                location=location,
                sample_size=max(10, results_count)
            )

        with console.status("[bold magenta]Synthesizing macro skill frequencies, salary, and emerging trends...", spinner="dots"):
            report = agent.analyze_market_demand(
                query=scan_market,
                location=location,
                sample_size=len(listings) if listings else results_count,
                market_corpus=corpus
            )

        console.print(f"\n[bold green]✔ Market Report Synthesized ({len(listings)} postings analyzed)[/bold green]\n")
        console.print(Panel(
            f"[bold]Market Summary:[/bold]\n{report.market_summary}\n\n"
            f"[bold]Salary & Compensation Insights:[/bold]\n{report.salary_insights}\n\n"
            f"[bold]Top Hiring Companies / Sectors:[/bold]\n{', '.join(report.top_hiring_companies) if report.top_hiring_companies else 'Various'}",
            title=f"[bold cyan]Macro Market Pulse: {scan_market} ({location})[/bold cyan]",
            border_style="cyan"
        ))

        table = Table(title="Top In-Demand Technical Skills", show_header=True, header_style="bold magenta")
        table.add_column("Skill Name", style="bold cyan")
        table.add_column("Demand Index", justify="center")
        table.add_column("Importance", style="bold")
        table.add_column("Category", style="dim")
        table.add_column("Sample Use Cases")

        for s in report.top_hard_skills:
            imp_style = "red" if "must" in s.importance.lower() or "core" in s.importance.lower() else ("blue" if "high" in s.importance.lower() else "green")
            table.add_row(
                s.skill_name,
                f"{s.frequency_score}%",
                f"[{imp_style}]{s.importance}[/{imp_style}]",
                s.category,
                "; ".join(s.sample_use_cases[:2]) if s.sample_use_cases else "N/A"
            )
        console.print(table)
        return

    # If user wants an employability roadmap
    if roadmap:
        if not resume:
            console.print("[bold red]Error: --roadmap requires --resume <file> to diagnose candidate gaps.[/bold red]")
            sys.exit(1)

        console.print(Panel.fit(
            f"[bold cyan]🎯 Employability & Upskilling Diagnostic[/bold cyan]\n"
            f"[dim]Resume: [bold]{resume}[/bold] | Target Role: [bold]{target_role}[/bold][/dim]",
            border_style="cyan"
        ))
        key_manager = KeyManager()
        if add_key:
            key_manager.add_key(add_key)
        agent = JobSearchAgent(key_manager=key_manager, model=model)

        with console.status("[bold blue]Parsing candidate base resume...", spinner="dots"):
            resume_content = InputParser.load_content(resume)

        with console.status("[bold magenta]Diagnosing Pareto 80/20 gaps and generating budget-adaptive learning paths...", spinner="dots"):
            road = agent.generate_employability_roadmap(
                base_resume=resume_content,
                target_role=target_role,
                budget_preference="All Tiers"
            )

        console.print(Panel(
            f"[bold]Target Role:[/bold] {road.target_role}\n"
            f"[bold]Current Readiness Score:[/bold] [bold cyan]{road.current_readiness_score}%[/bold cyan]\n"
            f"[bold]Estimated Timeline to 85%+ Match:[/bold] [bold green]{road.time_to_ready_estimate}[/bold green]\n\n"
            f"[bold]Executive Career Strategy:[/bold]\n{road.executive_summary}",
            title="[bold green]Employability Diagnostic Summary[/bold green]",
            border_style="green"
        ))

        # Skill Gaps Table
        gap_table = Table(title="Pareto 80/20 Skill Gaps & Curated Recommendations", show_header=True, header_style="bold yellow")
        gap_table.add_column("Gap", style="bold")
        gap_table.add_column("Tier", style="bold")
        gap_table.add_column("Why It Matters")
        gap_table.add_column("Curated Recommendations", style="cyan")

        for g in road.skill_gaps:
            tier_style = "red" if "1" in g.tier else ("blue" if "2" in g.tier else "green")
            recs = []
            for r in g.learning_pathway[:2]:
                sub = " [MY-Subsidized]" if r.malaysia_subsidy_eligible else ""
                recs.append(f"• {r.title} ({r.provider}, {r.cost_tier}){sub}")
            gap_table.add_row(
                g.skill,
                f"[{tier_style}]{g.tier}[/{tier_style}]",
                g.why_it_matters,
                "\n".join(recs) if recs else "Self-study / Docs"
            )
        console.print(gap_table)

        console.print("\n[bold red]🔴 30-Day Sprint Milestones (Tier 1 Deal-Breakers):[/bold red]")
        for s in road.sprint_30_days:
            console.print(f"  • {s}")
        console.print(f"\n[dim]To view complete interactive blueprints, run: [cyan]python main.py --web[/cyan][/dim]\n")
        return

    if not resume or not job:
        console.print(Panel(
            "[bold yellow]Missing required parameters![/bold yellow]\n\n"
            "Please provide both [green]--resume[/green] and [green]--job[/green] options, or use [cyan]--web[/cyan] to open the browser interface.\n\n"
            "Examples:\n"
            "  [white]python main.py --resume \"Chin Yung Wei Resume - Aug 2026.docx\" --job \"https://example.com/job\"[/white]\n"
            "  [white]python main.py --search-jobs \"Software Engineer\" --location \"Malaysia\"[/white]\n"
            "  [white]python main.py --web[/white]",
            title="[bold red]Usage Error[/bold red]",
            border_style="red"
        ))
        sys.exit(1)

    console.print(Panel.fit(
        "[bold cyan]AI Job Search & Application Generation Engine[/bold cyan]\n"
        f"[dim]Model: [bold]{model}[/bold] | Output: [bold]{output_dir}[/bold] | PDF: [bold]{pdf}[/bold][/dim]",
        border_style="cyan"
    ))

    # Initialize Key Manager
    key_manager = KeyManager()
    if add_key:
        key_manager.add_key(add_key)
        console.print(f"[green]✔ Added custom API key to rotation pool.[/green]")

    # 1. Parse Inputs
    with console.status("[bold blue]Loading and parsing resume and job posting...", spinner="dots"):
        try:
            resume_content = InputParser.load_content(resume)
            job_content = InputParser.load_content(job)
        except Exception as e:
            console.print(f"[bold red]❌ Intake Error:[/bold red] {e}")
            sys.exit(1)

    console.print(f"[green]✔ Intake parsed successfully.[/green] Base Profile: [bold]{len(resume_content)}[/bold] chars | Job Posting: [bold]{len(job_content)}[/bold] chars\n")

    # 2. Run Multi-Agent Workflow
    agent = JobSearchAgent(key_manager=key_manager, model=model)
    renderer = Renderer()
    output_path = Path(output_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Initializing Multi-Agent Pipeline...", total=5)

        def progress_cb(msg: str, step: int):
            progress.update(task, description=f"[cyan]{msg}", completed=step)

        try:
            job_analysis, match_eval, tailored_resume, cover_letter, review_feedback = agent.run_pipeline(
                job_raw_text=job_content,
                base_resume_text=resume_content,
                max_refinement_retries=max_retries,
                progress_callback=progress_cb
            )
        except Exception as e:
            console.print(f"\n[bold red]❌ Multi-Agent Pipeline Failed:[/bold red] {e}")
            sys.exit(1)

    # 3. Present Results & Scoring
    console.print("\n" + "="*70 + "\n")

    # Job & Candidate Match Card
    match_color = "green" if match_eval.overall_score >= 80 else "yellow" if match_eval.overall_score >= 60 else "red"
    ats_color = "green" if review_feedback.ats_score >= 85 else "yellow"

    match_table = Table(title="[bold]Evaluation & ATS Readiness Score[/bold]", show_header=True, header_style="bold magenta")
    match_table.add_column("Metric", style="dim")
    match_table.add_column("Score", justify="center")
    match_table.add_column("Details")

    match_table.add_row(
        "Candidate Match",
        f"[{match_color}][bold]{match_eval.overall_score} / 100[/bold][/{match_color}]",
        f"[bold]Role:[/bold] {job_analysis.title} @ {job_analysis.company} ({job_analysis.experience_level})"
    )
    match_table.add_row(
        "ATS Validator Score",
        f"[{ats_color}][bold]{review_feedback.ats_score} / 100[/bold][/{ats_color}]",
        f"[bold]Status:[/bold] {'✅ Approved / High ATS Pass' if review_feedback.pass_review else '⚠️ Passed with remarks'}"
    )

    console.print(match_table)

    # Strategic Alignment & Gaps
    console.print(Panel(
        f"[bold]Alignment Strategy:[/bold]\n{match_eval.alignment_strategy}\n\n"
        f"[bold]Key Strengths Aligned:[/bold]\n• " + "\n• ".join(match_eval.matching_qualifications[:5]) + "\n\n"
        f"[bold]Identified Gaps Addressed:[/bold]\n• " + ("\n• ".join(match_eval.missing_gaps) if match_eval.missing_gaps else "None identified"),
        title="[bold green]Strategic Positioning[/bold green]",
        border_style="green"
    ))

    # Recruiter Critique
    console.print(Panel(
        f"[bold]ATS Critique:[/bold] {review_feedback.critique}\n\n"
        f"[bold]Optimization Notes:[/bold]\n• " + "\n• ".join(review_feedback.suggestions if review_feedback.suggestions else ["Clean formatting and strong action verbs applied"]),
        title="[bold blue]Executive ATS Review[/bold blue]",
        border_style="blue"
    ))

    # 4. Render & Export Artifacts
    with console.status("[bold green]Compiling Markdown, HTML, and PDF documents...", spinner="dots"):
        artifacts = renderer.export_all(
            output_dir=output_path,
            job_analysis=job_analysis,
            match_evaluation=match_eval,
            tailored_resume=tailored_resume,
            cover_letter=cover_letter,
            review_feedback=review_feedback,
            generate_pdf=pdf
        )

    # Artifacts Output Table
    console.print("\n[bold green]✨ All Application Artifacts Generated Successfully![/bold green]\n")
    artifact_table = Table(title="[bold]Generated Artifacts[/bold]", show_header=True, header_style="bold cyan")
    artifact_table.add_column("Artifact", style="bold")
    artifact_table.add_column("Format")
    artifact_table.add_column("File Path")

    for key, file_path in artifacts.items():
        fmt = file_path.suffix.upper().replace(".", "")
        artifact_table.add_row(key.replace("_", " ").title(), f"[bold]{fmt}[/bold]", str(file_path.resolve()))

    console.print(artifact_table)
    console.print(f"\n[dim]Open [bold]{output_dir}[/bold] to inspect your tailored application package.[/dim]\n")


if __name__ == "__main__":
    cli()
