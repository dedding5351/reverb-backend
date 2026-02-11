import json
import logging
import math
import argparse
import sys
from pathlib import Path
from app.engine.factory import ScraperFactory
from app.repositories.post import PostRepository
from app.models.post import Post

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_sources():
    config_path = Path(__file__).parent.parent / "config" / "sources.json"
    with open(config_path, "r") as f:
        return json.load(f)

def calculate_read_time(content: str) -> int:
    if not content:
        return 0
    word_count = len(content.split())
    read_time = math.ceil(word_count / 200)
    return max(1, read_time)

def sanitize(text):
    if isinstance(text, str):
        return text.replace("\x00", "")
    return text

def run_pipeline(source_id: str = None):
    logger.info("Starting Scraper Pipeline...")
    
    # 1. Initialize Repository & DB
    from app.database import engine, Base
    Base.metadata.create_all(bind=engine)
    repo = PostRepository()
    
    # 2. Load Sources
    all_sources = load_sources()
    
    # Filter sources if flag provided
    if source_id:
        sources = [s for s in all_sources if s.get("id") == source_id]
        if not sources:
            logger.error(f"Source with ID '{source_id}' not found.")
            sys.exit(1)
        logger.info(f"Filtered to 1 source: {source_id}")
    else:
        sources = all_sources
        logger.info(f"Loaded {len(sources)} sources.")

    # 3. Process each source
    for source in sources:
        name = source["name"]
        url = source["url"]
        s_id = source.get("id", "unknown")
        logger.info(f"Scraping: {name} ({url})")
        
        try:
            scraper = ScraperFactory.get_scraper(url)
            posts_found = 0
            
            for post_meta in scraper.crawl(url):
                posts_found += 1
                
                if not post_meta.url:
                     continue
                
                read_time = calculate_read_time(post_meta.content)

                # Create SQLAlchemy Post instance
                # Convert HttpUrl to string for DB
                domain_post = Post(
                    title=sanitize(post_meta.title),
                    url=str(post_meta.url),
                    description=sanitize(post_meta.description),
                    authors=post_meta.authors,
                    published_date=post_meta.published_date,
                    site_name=sanitize(post_meta.site_name or name),
                    source_id=s_id,
                    image_url=str(post_meta.image_url) if post_meta.image_url else None,
                    content=sanitize(post_meta.content),
                    read_time_minutes=read_time
                )
                
                try:
                    repo.create_or_update(domain_post)
                except Exception as e:
                    logger.error(f"Failed to save post {domain_post.title}: {e}")
                    repo.db.rollback()
                
            logger.info(f"Completed {name}. Found {posts_found} posts.")

        except Exception as e:
            logger.error(f"Failed to scrape {name}: {e}")

    logger.info("Pipeline Finished.")

if __name__ == "__main__":
    # Parse Arguments only when running as a script
    parser = argparse.ArgumentParser(description="Run the scraper pipeline.")
    parser.add_argument("--source", type=str, help="ID of the source to scrape (e.g., 'uber')")
    args = parser.parse_args()
    
    run_pipeline(source_id=args.source)
