import json
import os
from pathlib import Path
import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def qualify_lead(company: dict) -> dict:
    """Score a public project using AI when credentials are available."""

    name = company.get("company_name", "Unknown")
    website = company.get("website", "")
    description = company.get("description", "")

    if not GROQ_API_KEY:
        # This is a transparent fallback, not an AI-generated score.
        score = 40
        signals = ["Limited company information available"]

        if website:
            score += 10
            signals.append("A project website is available")

        if description:
            score += 10
            signals.append("A project description is available")

        return {
            "icp_score": min(score, 100),
            "detected_tech_stack": [],
            "key_signals": signals,
            "recommended_pitch_angle": (
                "Review the product and identify a relevant business "
                "need before proposing a solution."
            ),
            "qualification_method": "rule_based_fallback",
        }

    prompt = f"""
Evaluate this potential business lead using only the information supplied.

Company/project name: {name}
Website: {website}
Description: {description}

Score its potential as a business lead from 1 to 100.
Do not invent facts or technologies. If information is missing,
say so in key_signals.

Return ONLY a valid JSON object with these fields:
{{
  "icp_score": 1,
  "detected_tech_stack": [],
  "key_signals": [],
  "recommended_pitch_angle": "..."
}}
"""

    response = httpx.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You qualify business leads. Return valid JSON only."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=30,
    )
    print("Groq response:", response.status_code, response.text)
    if response.status_code != 200:
        raise RuntimeError(
            f"Groq returned {response.status_code}: {response.text}"
    )

    content = response.json()["choices"][0]["message"]["content"]
    result = json.loads(content)

    score = int(result["icp_score"])
    if not 1 <= score <= 100:
        raise ValueError("AI returned a score outside 1–100")

    return {
        "icp_score": score,
        "detected_tech_stack": result.get("detected_tech_stack", []),
        "key_signals": result.get("key_signals", []),
        "recommended_pitch_angle": result.get(
            "recommended_pitch_angle", ""
        ),
        "qualification_method": "groq_llm",
    }
if __name__ == "__main__":
    test_company = {
        "company_name": "Test AI Startup",
        "website": "https://example.com",
        "description": "AI automation software"
    }
    print(qualify_lead(test_company))