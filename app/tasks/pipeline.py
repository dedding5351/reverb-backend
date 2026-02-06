import json
import logging
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

import argparse
import sys

def run_pipeline():
    # Parse Arguments
    parser = argparse.ArgumentParser(description="Run the scraper pipeline.")
    parser.add_argument("--source", type=str, help="ID of the source to scrape (e.g., 'uber')")
    args = parser.parse_args()

    logger.info("Starting Scraper Pipeline...")
    
    # 1. Initialize Repository
    repo = PostRepository()
    
    # 2. Load Sources
    all_sources = load_sources()
    
    # Filter sources if flag provided
    if args.source:
        sources = [s for s in all_sources if s.get("id") == args.source]
        if not sources:
            logger.error(f"Source with ID '{args.source}' not found.")
            sys.exit(1)
        logger.info(f"Filtered to 1 source: {args.source}")
    else:
        sources = all_sources
        logger.info(f"Loaded {len(sources)} sources.")

    # 3. Process each source
    for source in sources:
        name = source["name"]
        url = source["url"]
        source_id = source.get("id", "unknown")
        logger.info(f"Scraping: {name} ({url})")
        
        try:
            scraper = ScraperFactory.get_scraper(url)
            posts_found = 0
            
            for post_meta in scraper.crawl(url):
                posts_found += 1
                
                if not post_meta.url:
                     continue
                
                # Create SQLAlchemy Post instance
                # Convert HttpUrl to string for DB
                domain_post = Post(
                    title=post_meta.title,
                    url=str(post_meta.url),
                    description=post_meta.description,
                    authors=post_meta.authors,
                    published_date=post_meta.published_date,
                    site_name=post_meta.site_name or name,
                    source_id=source_id,
                    image_url=str(post_meta.image_url) if post_meta.image_url else None
                )
                
                repo.create_or_update(domain_post)
                
            logger.info(f"Completed {name}. Found {posts_found} posts.")

        except Exception as e:
            logger.error(f"Failed to scrape {name}: {e}")

    logger.info("Pipeline Finished.")

if __name__ == "__main__":
    run_pipeline()
