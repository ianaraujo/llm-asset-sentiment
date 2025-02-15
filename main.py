from scrapers.base import BaseScraper

def main():
    count = 0
    for ScraperClass in BaseScraper.registry:
        scraper = ScraperClass()  # instância o scraper específico
        try:
            letters = scraper.scrape()
            len_letters = len(letters)

            count += len_letters
            print(f"{scraper.gestora} ({len_letters})")
        
        except Exception as e:
            print(f"Erro no scraper {scraper.gestora}: {e}")

    print(f"Total: {count} cartas")

if __name__ == "__main__":
    main()