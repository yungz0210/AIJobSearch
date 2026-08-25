"""
Autonomous Job Finder module with multi-board aggregation (LinkedIn, Indeed, Google Jobs)
and specialized support for Malaysia & Global locations.
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd

try:
    from jobspy import scrape_jobs
except ImportError:
    scrape_jobs = None

logger = logging.getLogger(__name__)


@dataclass
class JobListing:
    id: str
    title: str
    company: str
    location: str
    site: str
    job_url: str
    description: str
    date_posted: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_interval: Optional[str] = None
    job_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JobFinder:
    """Aggregates and queries live job boards for target positions and locations."""

    MALAYSIA_LOCATIONS = [
        "Malaysia",
        "Kuala Lumpur, Malaysia",
        "Selangor, Malaysia",
        "Petaling Jaya, Selangor, Malaysia",
        "Cyberjaya, Selangor, Malaysia",
        "Penang, Malaysia",
        "Johor Bahru, Johor, Malaysia",
        "Remote, Malaysia",
    ]

    SUPPORTED_SITES = ["linkedin", "indeed", "google"]

    @classmethod
    def search(
        cls,
        search_term: str,
        location: str = "Malaysia",
        sites: Optional[List[str]] = None,
        results_wanted: int = 10,
        hours_old: Optional[int] = None,
        is_remote: bool = False,
    ) -> List[JobListing]:
        """
        Search live job openings across selected job boards.
        """
        if scrape_jobs is None:
            raise ImportError(
                "JobSpy is required for automated job searching. Run: pip install python-jobspy"
            )

        if not search_term or not search_term.strip():
            return []

        active_sites = [s.lower() for s in (sites or cls.SUPPORTED_SITES) if s.lower() in cls.SUPPORTED_SITES]
        if not active_sites:
            active_sites = ["linkedin", "indeed"]

        # Determine country code for Indeed
        country_indeed = "malaysia" if "malaysia" in location.lower() else "usa"

        kwargs: Dict[str, Any] = {
            "site_name": active_sites,
            "search_term": search_term.strip(),
            "location": location.strip(),
            "results_wanted": max(1, min(results_wanted, 50)),
            "country_indeed": country_indeed,
        }

        if hours_old:
            kwargs["hours_old"] = hours_old
        if is_remote:
            kwargs["is_remote"] = True

        try:
            logger.info(f"Searching jobs: query='{search_term}', loc='{location}', sites={active_sites}")
            df_jobs = scrape_jobs(**kwargs)

            if df_jobs is None or df_jobs.empty:
                return []

            results: List[JobListing] = []
            for idx, row in df_jobs.iterrows():
                # Filter out entries missing titles or URLs
                title = str(row.get("title") or "").strip()
                if not title or title.lower() == "nan":
                    continue

                company = str(row.get("company") or "Confidential").strip()
                if company.lower() == "nan":
                    company = "Confidential"

                loc = str(row.get("location") or location).strip()
                if loc.lower() == "nan":
                    loc = location

                site = str(row.get("site") or "Web").capitalize()
                job_url = str(row.get("job_url") or "").strip()
                desc = str(row.get("description") or "").strip()
                if desc.lower() == "nan":
                    desc = ""

                date_posted = str(row.get("date_posted") or "") if pd.notna(row.get("date_posted")) else None
                job_type = str(row.get("job_type") or "") if pd.notna(row.get("job_type")) else None

                min_sal = float(row["min_amount"]) if pd.notna(row.get("min_amount")) else None
                max_sal = float(row["max_amount"]) if pd.notna(row.get("max_amount")) else None
                interval = str(row.get("interval")) if pd.notna(row.get("interval")) else None

                listing = JobListing(
                    id=f"{site.lower()}-{idx}-{abs(hash(job_url)) % 100000}",
                    title=title,
                    company=company,
                    location=loc,
                    site=site,
                    job_url=job_url,
                    description=desc,
                    date_posted=date_posted,
                    salary_min=min_sal,
                    salary_max=max_sal,
                    salary_interval=interval,
                    job_type=job_type,
                )
                results.append(listing)

            return results

        except Exception as e:
            logger.error(f"Error during job search: {e}", exc_info=True)
            return []
