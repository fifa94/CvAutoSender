import requests
from bs4 import BeautifulSoup


class  TextextractorEasy:
    def __init__(self, url:str):
        # kontrola jestli vstupni url je string
        if not isinstance(url, str):
            raise TypeError("url must be a string")
        self.url: str = url

    def fetch_page(self):
        try:
            resp = requests.get(self.url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            return soup
        except requests.exceptions.RequestException as e:
            print(f"Chyba při stahování stránky: {e}")
            return None
        except Exception as e:
            print(f"Neočekávaná chyba: {e}")
            return None

    def extract(self):

        soup = self.fetch_page()

        # najdi konkrétní třídu
        heading = soup.find("div", class_="JobDescriptionHeading")
        if heading:
            print("=== HEADING ===")
            print(heading.get_text(strip=True))

        # najdi text celeho inzeratu
        text = soup.find("div", class_="RichContent mb-1400")
        if text:
            print("=== TEXT ===")
            print(text.get_text(strip=True))

        return heading, text

if __name__=="__main__":
    # url1 = "https://www.jobs.cz/rpd/2000768059/?searchId=04419d52-b694-4ed5-a1f6-828f83549e52&rps=233"
    url2 = "https://www.jobs.cz/rpd/2000768059/?searchId=04419d52-b694-4ed5-a1f6-828f83549e52&rps=233"
    TextExtractor = TextextractorEasy(url2)
    TextExtractor.extract()