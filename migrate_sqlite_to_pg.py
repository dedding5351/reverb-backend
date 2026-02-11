import sqlite3
import json
import logging
from app.database import SessionLocal, engine, Base
from app.models.post import Post
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data():
    logger.info("Starting migration from SQLite to PostgreSQL...")
    
    # 1. Initialize Postgres Tables
    # Create extension first
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL tables created.")
    
    # 2. Read from SQLite
    sqlite_db_path = "reverb.db"
    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    def sanitize(text):
        if isinstance(text, str):
            return text.replace("\x00", "")
        return text

    try:
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} posts in SQLite.")
        
        pg_db = SessionLocal()
        
        for row in rows:
            # Convert row to dict
            data = dict(row)
            
            # Handle embedding
            embedding = None
            if data["embedding"]:
                try:
                    embedding = json.loads(data["embedding"])
                except:
                    pass
            
            # Handle authors
            authors = []
            if data["authors"]:
                try:
                    authors = json.loads(data["authors"])
                except:
                    pass

            # Create Post object
            post = Post(
                id=data["id"],
                title=sanitize(data["title"]),
                url=data["url"],
                description=sanitize(data["description"]),
                authors=authors,
                published_date=data["published_date"], 
                site_name=sanitize(data["site_name"]),
                source_id=data["source_id"],
                image_url=data["image_url"],
                content=sanitize(data["content"]),
                embedding=embedding,
                read_time_minutes=data.get("read_time_minutes"),
                created_at=data["created_at"]
            )
            
            # Check if exists (idempotency)
            existing = pg_db.query(Post).filter(Post.id == post.id).first()
            if not existing:
                pg_db.add(post)
                
        pg_db.commit()
        logger.info("Migration complete.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        pg_db.rollback()
    finally:
        conn.close()
        pg_db.close()

if __name__ == "__main__":
    migrate_data()
