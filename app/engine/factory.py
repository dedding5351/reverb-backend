import httpx
from bs4 import BeautifulSoup
from app.engine.base import BaseScraper
from app.engine.strategies.uber import UberScraper
from app.engine.strategies.stripe import StripeScraper
from app.engine.strategies.airbnb import AirbnbScraper
from app.engine.strategies.lyft import LyftScraper

class ScraperFactory:
    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        if "uber.com" in url:
             return UberScraper()
        
        if "stripe.com" in url:
            return StripeScraper()
            
        if "airbnb.tech" in url:
            return AirbnbScraper()

        if "eng.lyft.com" in url:
            return LyftScraper()

        raise NotImplementedError("No scraper found for URL: " + url)
