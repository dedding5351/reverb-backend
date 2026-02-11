import asyncio
import httpx
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from app.engine.blog_scraper import BlogScraper
from app.engine.models import PostMetadata
import dateutil.parser
import datetime
import xml.etree.ElementTree as ET

class LyftScraper(BlogScraper):
    def __init__(self):
        # Lyft has SSL verification issues, so we disable it
        client = httpx.Client(timeout=10.0, follow_redirects=True, verify=False)
        super().__init__(client=client)
        self.rss_items: Dict[str, dict] = {} # Map link -> {title, date, author, image}
        self.rss_fetched = False

    async def _fetch_rss_data(self):
        """
        Fetches RSS feed to populate self.rss_items with rich metadata.
        """
        if self.rss_fetched:
            return

        rss_url = "https://eng.lyft.com/feed"
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(rss_url, follow_redirects=True)
                if response.status_code == 200:
                    root = ET.fromstring(response.text)
                    channel = root.find("channel")
                    items = channel.findall("item") if channel else []
                    if not items:
                         items = root.findall(".//item")

                    for item in items:
                        link_elem = item.find("link")
                        if link_elem is not None and link_elem.text:
                            # Clean link (remove query params like ?source=rss)
                            link = link_elem.text.strip().split('?')[0]
                            
                            title = item.find("title").text if item.find("title") is not None else None
                            pubDate = item.find("pubDate").text if item.find("pubDate") is not None else None
                            creator = None
                            for child in item:
                                if "creator" in child.tag:
                                    creator = child.text
                                    break
                            
                            # Extract image from content:encoded
                            image_url = None
                            content_encoded = None
                            for child in item:
                                if "encoded" in child.tag:
                                    content_encoded = child.text
                                    break
                            
                            if content_encoded:
                                # Quick/dirty parse for first img src in content
                                try:
                                    content_soup = BeautifulSoup(content_encoded, "html.parser")
                                    img = content_soup.find("img")
                                    if img:
                                        image_url = img.get("src")
                                except:
                                    pass

                            self.rss_items[link] = {
                                "title": title,
                                "date": pubDate,
                                "author": creator,
                                "image": image_url
                            }
        except Exception as e:
            print(f"Error fetching Lyft RSS: {e}")
        finally:
            self.rss_fetched = True

    def _get_post_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        # Implementation Note:
        # We override this to use Sitemap logic instead of scraping the page provided in 'soup'.
        # 'soup' here is likely the main page, which we don't strictly need if using sitemap.
        
        # 1. Trigger RSS fetch (async via sync wrapper for compatibility)
        if not self.rss_fetched:
             try:
                 asyncio.get_event_loop().run_until_complete(self._fetch_rss_data())
             except RuntimeError:
                 pass

        # 2. Fetch Sitemap
        links = []
        sitemap_url = "https://eng.lyft.com/sitemap/sitemap.xml"
        try:
             # We need a synchronous fetch here since _get_post_links is sync in base class?
             # Or we can use the same asyncio hack. 
             # Ideally we'd use 'httpx.get' sync if generic, but let's stick to async loop run
             # to be consistent with how we do things in this codebase context.
             # Actually, creating a new loop/client inside a sync method is risky if loop is running.
             # Using 'httpx.get' (sync) is safer if not already in an async context, but we likely ARE.
             # Let's try to reuse the loop or just do a quick sync call using httpx.Client()
             
             with httpx.Client(verify=False) as client:
                 resp = client.get(sitemap_url, follow_redirects=True)
                 if resp.status_code == 200 and "xml" in resp.headers.get("content-type", ""):
                     root = ET.fromstring(resp.text)
                     ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                     # Find all locs
                     urls = [elem.text for elem in root.findall(".//sm:loc", ns)]
                     
                     # Filter for posts
                     # Exclude tags, authors, and the main page
                     for u in urls:
                         if not u: continue
                         if u == "https://eng.lyft.com/": continue
                         if "/tagged/" in u: continue
                         if "/@" in u: continue
                         if u.endswith("/sitemap/sitemap.xml"): continue
                         
                         links.append(u)
        except Exception as e:
            print(f"Error fetching Lyft Sitemap: {e}")
            # Fallback: scrape the soup provided (the main page)
            # Find links with data-post-id or similar Medium patterns
            for a in soup.find_all("a"):
                href = a.get("href")
                if href and "-" in href and not href.startswith("http"):
                    # Relative link with slug
                    links.append(urljoin(base_url, href))
                elif href and "eng.lyft.com" in href and "-" in href:
                    links.append(href)

        return list(set(links)) # Dedupe

    def _get_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        return None # user wants full scrape via sitemap, so no pagination needed

    def _extract_post_metadata(self, soup: BeautifulSoup, post_url: str) -> Optional[PostMetadata]:
        # Check RSS cache first
        # RSS links might have different query params, so we cleaned them in storage.
        # Clean this url too
        clean_url = post_url.split('?')[0]
        rss_data = self.rss_items.get(clean_url)

        title = None
        published_date = None
        authors = []
        image_url = None
        description = None

        if rss_data:
            title = rss_data.get("title")
            if rss_data.get("date"):
                try:
                    published_date = dateutil.parser.parse(rss_data["date"])
                except:
                    pass
            if rss_data.get("author"):
                authors.append(rss_data["author"])
            image_url = rss_data.get("image")
        
        # HTML Fallback / Supplement
        if not title:
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else None
            if not title:
                 og_title = soup.find("meta", property="og:title")
                 if og_title: title = og_title["content"]

        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                description = og_desc["content"]
            else:
                desc_elem = soup.find("meta", attrs={"name": "description"})
                if desc_elem: description = desc_elem["content"]

        if not published_date:
            # Medium: meta property="article:published_time"
            pub_meta = soup.find("meta", property="article:published_time")
            if pub_meta:
                try:
                    published_date = dateutil.parser.parse(pub_meta["content"])
                except:
                    pass

        if not authors:
             author_meta = soup.find("meta", attrs={"name": "author"})
             if author_meta:
                 authors.append(author_meta["content"])

        if not image_url:
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image["content"]

            image_url = og_image["content"]

        # 6. Content
        content = None
        article = soup.find("article")
        if article:
            # Basic cleanup: remove styles, scripts
            for tag in article(["script", "style", "noscript"]):
                tag.decompose()
            content = article.get_text(separator="\n\n", strip=True)

        return PostMetadata(
            title=title,
            url=post_url,
            description=description,
            authors=authors,
            published_date=published_date,
            site_name="Lyft Engineering",
            image_url=image_url,
            content=content
        )
