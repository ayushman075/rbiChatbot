# from scraper.rbi_scraper import scrape_rbi_documents

# if __name__ == "__main__":
#     scrape_rbi_documents(limit=200)

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000)

