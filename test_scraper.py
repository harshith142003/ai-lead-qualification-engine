from app.scraper.fetcher import scrape_companies

companies = scrape_companies(limit=5)

print("Projects collected:", len(companies))

for company in companies:
    print("-" * 30)
    print("Name:", company["company_name"])
    print("Website:", company["website"])
    print("Source:", company["source_url"])
