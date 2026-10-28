# Open-Source Lead Scraping & AI Qualification Engine

## Overview
A Python-based lead generation engine that discovers public startup information, evaluates potential customers using an AI model, and stores qualified leads in Supabase.

## Features
- Scrapes public startup information from Hacker News Show HN using the Algolia API.
- Uses an LLM through Groq to score leads from 1 to 100.
- Identifies relevant business signals and potential pitch angles.
- Stores lead information in Supabase.
- Provides REST API endpoints using FastAPI.
- Uses environment variables to protect credentials.

## Technology Stack
- Python
- FastAPI
- Pydantic
- Groq API
- Supabase
- Hacker News Algolia API
- Uvicorn

## Project Structure
- `app/main.py` - FastAPI application entry point.
- `app/scraper/` - Collects public startup information.
- `app/qualification/` - AI lead scoring and qualification.
- `app/routes/` - API endpoints.
- `app/database/` - Database integration.
- `migrations/` - Database schema and indexes.
- `tests/` - Project tests.
- `requirements.txt` - Python dependencies.
- `.env.example` - Example environment configuration.

## Setup

1. Clone the repository:

   `git clone https://github.com/harshith142003/ai-lead-qualification-engine.git`

2. Enter the project directory:

   `cd ai-lead-qualification-engine`

3. Create and activate a virtual environment:

   `python3 -m venv .venv`

   `source .venv/bin/activate`

4. Install dependencies:

   `pip install -r requirements.txt`

5. Create a `.env` file using `.env.example` and configure the required Groq and Supabase credentials.

6. Start the API:

   `uvicorn app.main:app --reload`

7. Open the interactive API documentation:

   `http://127.0.0.1:8000/docs`

## API Usage

### Health Check

`curl http://127.0.0.1:8000/health`

### Crawl and Qualify Leads

`curl -X POST http://127.0.0.1:8000/crawl`

### Retrieve Leads

`curl http://127.0.0.1:8000/leads`

Check `/docs` for the exact request parameters and response schemas supported by the running application.

## Database Design
The leads table stores company name, website, domain, description, detected technology stack, qualification score, key signals, pitch angle, source URL, and timestamps.

A unique constraint on domain prevents duplicate company records. Indexes on qualification score and scrape time support efficient filtering and sorting.

## Security
- Never commit `.env` or real API credentials.
- Keep `.env` in `.gitignore`.
- Use `.env.example` with placeholder values only.
- Rotate credentials if they are exposed.

## Limitations and Future Improvements
- Add more public lead sources.
- Improve retry handling and rate-limit backoff.
- Add scheduled scraping and monitoring.
- Evaluate lead-scoring accuracy against human-reviewed examples.
- Add authentication and deployment monitoring.

## License
For educational and demonstration purposes.
