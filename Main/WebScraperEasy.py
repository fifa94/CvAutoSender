import requests
from bs4 import BeautifulSoup
import time

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
            print(f"Chyba při stahování {url}: {e}")
            return None

    def extract_from_page(self, soup):
        """Vyextrahuje heading a text z BeautifulSoup objektu"""
        if soup is None:
            return None, None

        heading = soup.find("div", class_="JobDescriptionHeading")
        heading_text = heading.get_text(strip=True) if heading else None

        text = soup.select_one("div.RichContent.mb-1400")
        text_content = text.get_text(strip=True) if text else None

        return heading_text, text_content

    def scrape_all(self):
        """Scrapuje všechny URL a uloží výsledky do self.results"""
        for url in self.urls:
            print(f"Scraping: {url}")
            soup = self.fetch_page(url)
            heading, text = self.extract_from_page(soup)
            self.results.append({
                "url": url,
                "heading": heading,
                "text": text
            })
            time.sleep(self.delay)  # pauza mezi požadavky
        return self.results

# --------- Příklad použití ---------
if __name__ == "__main__":
    urls = [
        "https://www.jobs.cz/rpd/2000768059/?searchId=04419d52-b694-4ed5-a1f6-828f83549e52&rps=233",
        "https://www.jobs.cz/fp/ice-industrial-services-a-s-484254977/2000120680/?searchId=4242118c-6e7e-464a-b2ca-62b76043a80c&rps=233",
        # další URL sem
    ]
    scraper = JobScraper(urls, delay=1.5)
    results = scraper.scrape_all()

    # ukázka výsledků
    for r in results:
        print("\nURL:", r["url"])
        print("Heading:", r["heading"])
        print("Text (prvních 200 znaků):", r["text"][:200] if r["text"] else "None")
