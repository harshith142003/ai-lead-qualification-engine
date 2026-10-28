from datetime import datetime, timezone
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from app.scraper.fetcher import scrape_companies
from app.database.client import supabase
from app.qualification.scoring import qualify_lead
from urllib.parse import urlparse
from app.qualification.scoring import qualify_lead
app = FastAPI(
    title="AI Lead Scraping & Qualification Engine",
    description="Collect, score, and retrieve public company leads.",
    version="1.0.0",
)

# Temporary in-memory storage so we can test the API first.
# We'll replace this with Supabase persistence in a later step.
leads = {}


class Lead(BaseModel):
    company_name: str
    website: str
    detected_tech_stack: list[str] = Field(default_factory=list)
    icp_score: int = Field(ge=1, le=100)
    key_signals: list[str] = Field(default_factory=list)
    recommended_pitch_angle: str
    source_url: str = ""
    scraped_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@app.get("/")
def root():
    return {
        "project": "AI Lead Scraping & Qualification Engine",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}



@app.post("/crawl")
def crawl():
    try:
        companies = scrape_companies(limit=10)
    except Exception as exc:
        return {
            "message": "Scraping failed",
            "error": str(exc),
            "leads_saved": 0,
        }

    saved = 0
    for company in companies:
        website = company.get("website", "").strip()
        if not website: 
            continue

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        parsed = urlparse(website)
        domain = (parsed.hostname or "").lower().removeprefix("www.")
        if not domain:
            continue

        try:
            qualification = qualify_lead(company)

            lead_data = {
                "company_name": company["company_name"],
                "website": website,
                "domain": domain,
                "description": company.get("description", ""),
                "detected_tech_stack": qualification["detected_tech_stack"],
                "icp_score": qualification["icp_score"],
                "key_signals": qualification["key_signals"],
                "recommended_pitch_angle": qualification["recommended_pitch_angle"],
                "qualification_method": qualification["qualification_method"],
                "source_url": company.get("source_url", ""),
            }

            if supabase is None:
                return {
                    "message": "Supabase is not configured",
                    "leads_saved": saved,
                }

            supabase.table("leads").upsert(
                lead_data, on_conflict="domain"
            ).execute()
            saved += 1
        except Exception as exc:
            print(f"Could not save {company.get('company_name', 'unknown')}: {exc}")
            continue

    return {
        "message": "Scraping completed",
        "projects_found": len(companies),
        "new_leads_saved": saved,
        "note": (
            "Score 50 is temporary, not AI-generated. "
            "Storage is temporary until Supabase is connected."
        ),
    }

@app.get("/leads", response_model=list[Lead])
def list_leads(
    min_score: int = Query(default=0, ge=0, le=100),
    since: datetime | None = None,
):
    results = supabase.table("leads").select("*").execute().data if supabase else []

    if since:
        results = [
            lead for lead in results if lead.scraped_at >= since
        ]

    results = [
        lead for lead in results if lead.get("icp_score", 0) >= min_score
    ]

    return sorted(results, key=lambda lead: lead.get("icp_score", 0), reverse=True)


