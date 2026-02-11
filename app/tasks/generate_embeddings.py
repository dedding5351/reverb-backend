import logging
import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.post import Post
from app.services.gemini_service import get_gemini_service, GeminiService
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_embeddings():
    logger.info("Starting Embedding Generation Task...")
    
    db: Session = SessionLocal()
    gemini_service: GeminiService = get_gemini_service()
    
    try:
        # Fetch posts that have content but no embedding
        posts_to_process = db.query(Post).filter(
            Post.content.isnot(None),
            Post.embedding.is_(None)
        ).all()
        
        logger.info(f"Found {len(posts_to_process)} posts to process.")
        
        for post in posts_to_process:
            logger.info(f"Processing post: {post.title}")
            retry_count = 0
            max_retries = 8
            base_delay = 5  # Start with 5s delay
            
            # Initial politeness
            await asyncio.sleep(2)
            
            while retry_count < max_retries:
                try:
                    # Generate embedding
                    embedding = await gemini_service.generate_embedding(post.content)
                    post.embedding = embedding
                    db.commit()
                    
                    # Sync to Vector DB
                    # generic 'posts' table has a hidden rowid we can use
                    # We need to find the rowid for this post
                    # It's safer to use the same transaction, but for now strict separation is fine
                    # or we can just Execute SQL directly


                    # Polite delay
                    await asyncio.sleep(1)
                    break
                except Exception as e:
                    if "429" in str(e):
                        delay = base_delay * (2 ** retry_count)
                        logger.warning(f"Rate limited for '{post.title}'. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        retry_count += 1
                    else:
                        logger.error(f"Failed to generate embedding for post '{post.title}': {e}")
                        db.rollback()
                        break
            else:
                 logger.error(f"Max retries exceeded for post '{post.title}'. Skipping.")
                
        logger.info("Embedding Generation Task Completed.")
        
    except Exception as e:
        logger.error(f"Task failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(generate_embeddings())
