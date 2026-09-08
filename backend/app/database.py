import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("formmind.database")

# Configure database engine arguments based on dialect
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
}

if not is_sqlite:
    # Production PostgreSQL connection pooling settings
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": 30
    })

try:
    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
except Exception as e:
    logger.error(f"Failed to create database engine for URL: {settings.DATABASE_URL}. Error: {e}")
    # Fallback to local SQLite if remote DB connection URL fails
    fallback_url = "sqlite:////tmp/formmind.db" if settings.DATABASE_URL.startswith("sqlite") else "sqlite:///./formmind.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False}, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db_schema():
    """
    Initializes database tables and applies lightweight schema migrations.
    """
    try:
        Base.metadata.create_all(bind=engine)
        if is_sqlite:
            with engine.connect() as conn:
                try:
                    res = conn.execute(text("PRAGMA table_info(forms)")).fetchall()
                    existing_cols = {row[1] for row in res}
                    
                    new_cols = [
                        ("form_metadata_status", "VARCHAR(50) DEFAULT 'ready'"),
                        ("response_access_status", "VARCHAR(50) DEFAULT 'ready'"),
                        ("response_sync_status", "VARCHAR(50) DEFAULT 'synced'"),
                        ("analysis_status", "VARCHAR(50) DEFAULT 'ready'"),
                        ("attachment_status", "VARCHAR(50) DEFAULT 'none'"),
                        ("last_synced_at", "DATETIME"),
                        ("connected_email", "VARCHAR(255)")
                    ]
                    for col_name, col_type in new_cols:
                        if col_name not in existing_cols:
                            conn.execute(text(f"ALTER TABLE forms ADD COLUMN {col_name} {col_type}"))

                    resp_res = conn.execute(text("PRAGMA table_info(form_responses)")).fetchall()
                    resp_cols = {row[1] for row in resp_res}
                    if "google_response_id" not in resp_cols:
                        conn.execute(text("ALTER TABLE form_responses ADD COLUMN google_response_id VARCHAR(255)"))
                    
                    conn.commit()
                except Exception as ex:
                    logger.debug(f"SQLite migration check notice: {ex}")
    except Exception as e:
        logger.warning(f"Database schema initialization warning: {e}")

def check_db_connectivity() -> bool:
    """
    Executes a lightweight query to verify active database health for readiness probes.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connectivity check failed: {e}")
        return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
