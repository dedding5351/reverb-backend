from typing import List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.engine.blog_scraper import BlogScraper
from app.engine.models import PostMetadata
import dateutil.parser

class UberScraper(BlogScraper):
    def _get_post_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        links = []
        # Uber specific: Articles are usually in <a> tags
        # We need to filter strictly for engineering blog posts
        
        # NOTE: Uber often uses <a> with class or specific structure. 
        # But for robust Generic-like discovery (since classes change),
        # let's look for links that START with the base_url path (minus page suffix)
        
        # Specifically, we want to IGNORE the category sidebars.
        # Often the main content is in a <main> or specific div.
        # But simply using the ID list we discovered earlier is quite robust.
        
        ignored_paths = [
            "/las-vegas/", "/advertising/", "/earn/", 
            "/ride/", "/eat/", "/merchants/", 
            "/business/", "/freight/", "/health/",
            "/higher-education/", "/transit/", "/community-support/",
            "/research/" 
            # Note: We want to KEEP /engineering/ 
        ]
        
        for a in soup.find_all("a", href=True):
            href = a['href']
            # Normalize
            full_url = urljoin(base_url, href)
            
            # Domain check
            if urlparse(full_url).netloc != urlparse(base_url).netloc:
                continue
                
            # Path check
            path = urlparse(full_url).path
            
            # Must contain "engineering" since that's what we are scraping
            # (Unless the base url is different, but for this scraper we assume engineering target)
            if "engineering" not in path:
                # Uber Engineering blog posts usually are /blog/engineering/something or /blog/something
                # Wait, actually: https://www.uber.com/blog/introducing-ufowarder/
                # The posts are NOT always under /engineering/ !
                # They are under /blog/ROOT.
                
                # So we CANNOT require "engineering" in the post URL.
                # Just require it DOES NOT have the other categories.
                pass

            # Ignore Archives/Categories
            if any(ignore in path for ignore in ignored_paths):
                continue
            
            # Ignore pagination links in the list
            if "/page/" in path:
                continue

            # Heuristic: Valid post usually has /blog/ + slug.
            # And usually length > X
            if "/blog/" in path and len(path.split("/")) > 2:
                if full_url not in links and full_url != base_url:
                     links.append(full_url)
                     
        return links

    def _get_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        # 1. Try <link rel="next"> (Best standard)
        link_next = soup.find("link", rel="next")
        if link_next and link_next.get("href"):
             return urljoin(base_url, link_next["href"])

        import re
        # 2. Try "Next Page" button (aria-label) - Case Insensitive
        a_next = soup.find("a", attrs={"aria-label": re.compile(r"Next Page", re.IGNORECASE)})
        if a_next and a_next.get("href"):
             return urljoin(base_url, a_next["href"])
             
        # 3. Try "View more stories" (Page 1 specific)
        view_more = soup.find("a", string=re.compile(r"View more stories", re.IGNORECASE))
        if view_more and view_more.get("href"):
             return urljoin(base_url, view_more["href"])

        return None

    def _extract_post_metadata(self, soup: BeautifulSoup, post_url: str) -> Optional[PostMetadata]:
        # Reuse the generic logic logic or implement specific lookup
        
        # 1. Title
        # Try specific Uber title class first or fallback to OG
        title = None
        # <h1 class="article-title"> ? Classes change.
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title["content"]
        else:
            title = soup.title.string if soup.title else "No Title"
            
        if "Archives" in title:
            return None

        # 2. Description
        description = None
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            description = og_desc["content"]

        # 3. Authors
        authors = []
        # Uber specific: <a rel="author"> often works
        for author_tag in soup.find_all("a", rel="author"):
            if author_tag.string:
                authors.append(author_tag.string.strip())
        
        # Fallback to meta
        if not authors:
             meta_auth = soup.find("meta", attrs={"name": "author"})
             if meta_auth:
                 authors.append(meta_auth["content"])

        # 4. Date
        published_date = None
        # Filter for article:published_time
        pub_meta = soup.find("meta", property="article:published_time")
        if pub_meta:
            try:
                published_date = dateutil.parser.parse(pub_meta["content"])
            except:
                pass

        # 5. Image
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image_url = og_image["content"]

        # 6. Content
        content = None
        main = soup.find("main")
        if main:
            content = main.get_text(separator="\n\n", strip=True)

        return PostMetadata(
            title=title,
            url=post_url,
            description=description,
            authors=authors,
            published_date=published_date,
            site_name="Uber Engineering", # Hardcoded or scraped
            image_url=image_url,
            content=content
        )
