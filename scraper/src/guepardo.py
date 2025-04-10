import re
from typing import Optional

from ..base import BaseScraper
from ..utils import extract_date
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()

class GuepardoScraper(BaseScraper):
    
    def __init__(self, pipeline: DatabasePipeline):
        super().__init__()

        self.gestora = "Guepardo"
        self.base_url = "https://www.guepardoinvest.com.br/cartas-da-gestora/"
    
        self.pipeline = pipeline

    def extract_text(self, url: str, title: str) -> str:
        text = pdf.extract_text(url)

        if text:
            text = text.replace(title, "")
            text = re.sub(r'Guepardo Investimentos.*?\+55 \(11\) 3103-9200', '', text, flags=re.DOTALL)

            if "Aviso Legal" in text:
                text = text.split("Aviso Legal")[0]

        return text

    def scrape(self, limit: Optional[int] = None):
        letters = []
        
        soup = self.parse(self.base_url)
        
        baixar_links = soup.find_all("span", string=lambda s: s and "baixar pdf" in s.lower())
     
        for span in baixar_links:
            title_tag = span.find_previous(lambda tag: tag.name in ["h3"] and "Relatório de Gestão" in tag.get_text())
            date_tag = span.find_previous(lambda tag: tag.name == "h4")

            if not title_tag:
                continue

            title = " ".join([title_tag.get_text(strip=True), date_tag.get_text(strip=True)])
            
            if self.should_skip(title):
                continue

            href = span.find_previous("a").get("href")
            
            date = extract_date(date_tag.get_text(strip=True))
            text = self.extract_text(href, title_tag.get_text(strip=True))

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date,
                "url": href,
                "content": text
            }

            letters.append(letter)
            
            if limit and len(letters) >= limit:
                return letters # for testing purposes

        for li in soup.find_all("li"):
            span = li.find("span", class_="elementor-icon-list-text")
            
            if span and "Carta aos Investidores" in span.get_text():
                title = span.get_text(strip=True)
                
                if self.pipeline.exists(self.gestora, title):
                    continue
                
                url = li.find("a", href=True)["href"]
                date = extract_date(title)
                text = self.extract_text(url, title)

                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": date,
                    "url": url,
                    "content": text
                }

                letters.append(letter)

        return letters


if __name__ == "__main__":
    pipeline = DummyPipeline()

    scraper = GuepardoScraper(pipeline)
    letters = scraper.scrape(limit=None)
    
    print(len(letters))
