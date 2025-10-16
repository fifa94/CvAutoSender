import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class JobPosting:
    def __init__(self, url, heading=None, text=None, source=None):
        self.url = url
        self.heading = heading
        self.text = text
        self.source = source or self._detect_source(url)
        self.extracted_at = datetime.now().isoformat()

    def _detect_source(self, url):
        """Detekuje zdroj podle URL"""
        if "jobs.cz" in url:
            return "jobs.cz"
        elif "tuvsud.jobs.cz" in url:
            return "tuvsud.jobs.cz"
        elif "siemens-mobility.jobs.cz" in url:
            return "siemens-mobility.jobs.cz"
        else:
            return "unknown"

    def to_dict(self):
        """Převede objekt na slovník pro JSON export"""
        return {
            "url": self.url,
            "heading": self.heading,
            "text": self.text,
            "source": self.source,
            "extracted_at": self.extracted_at
        }

    def __str__(self):
        return f"JobPosting({self.heading or 'No heading'}, {self.source}, {self.extracted_at})"

class JobScraper:
    def __init__(self, urls, delay=1.0):
        """
        urls : list[str] - seznam URL inzerátů
        delay: float - pauza mezi požadavky (v sekundách) pro ochranu serveru
        """
        if not isinstance(urls, list) or not all(isinstance(u, str) for u in urls):
            raise TypeError("urls musí být seznam stringů")
        self.urls = urls
        self.delay = delay
        self.results = []

    def fetch_page(self, url):
        """Stáhne stránku a vrátí BeautifulSoup objekt nebo None při chybě"""
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup
        except requests.exceptions.RequestException as e:
            logger.error(f"Chyba při stahování {url}: {e}")
            return None

    def extract_from_page(self, soup):
        """Vyextrahuje heading a text z BeautifulSoup objektu — původní verze"""
        if soup is None:
            return None, None

        # Původní extrakce — pouze konkrétní třídy
        heading = soup.find("div", class_="JobDescriptionHeading")
        heading_text = heading.get_text(strip=True) if heading else None

        text = soup.select_one("div.RichContent.mb-1400")
        text_content = text.get_text(strip=True) if text else None

        return heading_text, text_content

    def scrape_all(self):
        """Scrapuje všechny URL a uloží výsledky do self.results jako JobPosting objekty"""
        for url in self.urls:
            logger.info(f"Scraping: {url}")
            soup = self.fetch_page(url)
            heading, text = self.extract_from_page(soup)
            job = JobPosting(url, heading, text)
            self.results.append(job)
            time.sleep(self.delay)  # pauza mezi požadavky
        return self.results

# --------- Příklad použití ---------
if __name__ == "__main__":
    urls = [
        "https://www.jobs.cz/rpd/2000526046/?searchId=6705e21a-eae6-45cf-9af3-5ac5497eb18a&rps=233",
        "https://www.jobs.cz/rpd/2000401261/?searchId=6705e21a-eae6-45cf-9af3-5ac5497eb18a&rps=233",
        "https://www.jobs.cz/rpd/2000759916/?searchId=0184aea6-cf18-422a-8c1d-84b252d0d082&rps=233"
    ]
    scraper = JobScraper(urls, delay=1.5)
    results = scraper.scrape_all()

    # ukázka výsledků
    for job in results:
        print("\nURL:", job.url)
        print("Heading:", job.heading)
        print("Text (prvních 200 znaků):", job.text[:200] if job.text else "None")
        print("Source:", job.source)
        print("Extracted at:", job.extracted_at)
