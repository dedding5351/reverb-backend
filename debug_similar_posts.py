import asyncio
from app.services.search_service import get_search_service
from app.database import SessionLocal
from app.models.post import Post
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

async def test_similar_posts():
    db = SessionLocal()
    try:
        # Get a random post id
        post = db.query(Post).filter(Post.embedding.isnot(None)).first()
        if not post:
            print("No posts with embeddings found.")
            return

        print(f"Testing similar posts for: {post.title} (ID: {post.id})")
        service = get_search_service()
        results = await service.get_similar_posts(post.id)
        
        print(f"Found {len(results)} similar posts:")
        for p, dist in results:
            print(f"- {p.title} (Distance: {dist})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_similar_posts())
