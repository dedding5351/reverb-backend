import asyncio
import httpx
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.engine.blog_scraper import BlogScraper
from app.engine.models import PostMetadata
import dateutil.parser
import re
import datetime

import xml.etree.ElementTree as ET

class AirbnbScraper(BlogScraper):
    def __init__(self):
        super().__init__()
        self.url_date_map: Dict[str, datetime.datetime] = {}
        self.url_author_map: Dict[str, str] = {}
        self.url_description_map: Dict[str, str] = {}
        self.rss_fetched = False

    async def _fetch_rss_dates(self):
        """
        Fetches the RSS feed to populate self.url_date_map, self.url_author_map, and self.url_description_map.
        """
        if self.rss_fetched:
            return

        base_rss_url = "https://airbnb.tech/feed/"
        page = 1
        
        try:
            async with httpx.AsyncClient() as client:
                while True:
                    rss_url = f"{base_rss_url}?paged={page}" if page > 1 else base_rss_url
                    try:
                        response = await client.get(rss_url, follow_redirects=True)
                        if response.status_code != 200:
                            break
                        
                        # Use ElementTree which is standard lib and handles XML correctly
                        root = ET.fromstring(response.text)
                        
                        # Standard RSS 2.0: channel -> item
                        channel = root.find("channel")
                        if channel:
                            items = channel.findall("item")
                        else:
                            # Fallback if root IS the channel or some atom format
                            items = root.findall(".//item")

                        if not items:
                            break
                            
                        for item in items:
                            link_elem = item.find("link")
                            date_elem = item.find("pubDate")
                            creator_elem = item.find("{http://purl.org/dc/elements/1.1/}creator")
                            desc_elem = item.find("description")
                            
                            if creator_elem is None:
                                # Try without namespace or typical variants
                                creator_elem = item.find("creator") or item.find("dc:creator")
                            
                            if link_elem is not None:
                                link = link_elem.text.strip() if link_elem.text else ""
                                
                                # Date
                                if date_elem is not None:
                                    date_str = date_elem.text.strip() if date_elem.text else ""
                                    if date_str:
                                        try:
                                            dt = dateutil.parser.parse(date_str)
                                            self.url_date_map[link] = dt
                                        except:
                                            pass
                                
                                # Author
                                if creator_elem is not None:
                                    author = creator_elem.text.strip() if creator_elem.text else ""
                                    if author:
                                        self.url_author_map[link] = author

                                # Description
                                if desc_elem is not None:
                                    desc = desc_elem.text.strip() if desc_elem.text else ""
                                    if desc:
                                        # RSS descriptions often have HTML entites or tags, maybe strip them?
                                        # For now, raw is probably safer than broken stripping, or minimal strip.
                                        # Let's clean simple HTML tags if present using regex or BS4?
                                        # Actually app often expects plain text. Let's try to simple strip.
                                        clean_desc = re.sub(r'<[^>]+>', '', desc)
                                        self.url_description_map[link] = clean_desc
                        
                        page += 1
                        # Safety break to avoid infinite loops if something is weird
                        if page > 50: 
                            break
                            
                    except Exception:
                        # Parsing error or other issue means we probably hit the end or invalid XML
                        break
                        
        except Exception as e:
            print(f"Error fetching RSS feed: {e}")
        finally:
            self.rss_fetched = True

    def _get_post_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        # Sync wrapper, but usually we'd want async. 
        # Since BlogScraper interface is sync for these methods (usually), 
        # we might have to run the async fetch synchronously or just trigger it once.
        # Ideally, we should check if the base class supports async setup. 
        # Assuming typical pattern, we'll just run the loop here or rely on lazy loading.
        # But wait, `_get_post_links` is called by `scrape`. 
        # I'll just run the async loop briefly here if not fetched.
        
        if not self.rss_fetched:
             try:
                 loop = asyncio.get_event_loop()
                 if loop.is_running():
                     # If loop is running, we can't use run_until_complete.
                     # This usually happens in async contexts.
                     # We can try to rely on the fact that _fetch_rss_dates is async 
                     # but _get_post_links is sync.
                     # If we are here, we are likely in a sync call stack.
                     pass 
                 else:
                     loop.run_until_complete(self._fetch_rss_dates())
             except Exception:
                 # Fallback: Try creating new loop
                 try:
                     asyncio.run(self._fetch_rss_dates())
                 except Exception:
                     pass

        links = []
        # Airbnb posts are usually <a> tags with "Read more" or inside <h3>
        # Targeted selector: a tag with "Read more" text
        read_more_links = soup.find_all("a", string="Read more")
        for a in read_more_links:
            href = a.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if full_url not in links:
                    links.append(full_url)
        
        # Backup: check h3 > a
        if not links:
            for h3 in soup.find_all("h3"):
                a = h3.find("a")
                if a and a.get("href"):
                    full_url = urljoin(base_url, a.get("href"))
                    if full_url not in links:
                        links.append(full_url)

        return links

    def _get_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        # Airbnb uses /page/2/ etc.
        # Look for "Older posts" link
        older_link = soup.find("a", string=re.compile("Older posts", re.IGNORECASE))
        if older_link and older_link.get("href"):
             return urljoin(base_url, older_link.get("href"))
             
        # Or look for "Next" in pagination
        next_link = soup.find("a", class_=lambda x: x and "next" in x.lower())
        if next_link and next_link.get("href"):
             return urljoin(base_url, next_link.get("href"))

        return None

    def _extract_post_metadata(self, soup: BeautifulSoup, post_url: str) -> Optional[PostMetadata]:
        # 1. Title
        title = None
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title["content"]
        else:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text().strip()

        # 2. Description
        description = None
        
        # Check RSS cache first
        if self.url_description_map.get(post_url):
            description = self.url_description_map[post_url]
            
        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                description = og_desc["content"]

        # 3. Authors
        authors = []
        
        # Check RSS cache first
        if self.url_author_map.get(post_url):
            authors.append(self.url_author_map[post_url])
        
        if not authors:
            meta_auth = soup.find("meta", attrs={"name": "author"})
            if meta_auth:
                 authors.append(meta_auth["content"])
            else:
                 # Try text pattern? 
                 pass

        # 4. Date
        published_date = self.url_date_map.get(post_url)
        
        if not published_date:
            # Fallback: Infer from image URL
            # Urls like .../uploads/sites/19/2025/11/...
            images = soup.find_all("img")
            for img in images:
                src = img.get("src")
                if not src:
                    continue
                
                # Check for year/month pattern
                match = re.search(r'/(\d{4})/(\d{2})/', src)
                if match:
                    year, month = match.groups()
                    try:
                        # Assume 1st of month
                        published_date = datetime.datetime(int(year), int(month), 1)
                        break
                    except:
                        pass
        
        # 5. Image
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image_url = og_image["content"]

        return PostMetadata(
            title=title,
            url=post_url,
            description=description,
            authors=authors,
            published_date=published_date,
            site_name="Airbnb Tech Blog",
            image_url=image_url
        )
