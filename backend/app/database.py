from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# If using SQLite, check_same_thread needs to be False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db_schema():
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
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
                ("last_synced_at", "DATETIME")
            ]
            for col_name, col_type in new_cols:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE forms ADD COLUMN {col_name} {col_type}"))

            resp_res = conn.execute(text("PRAGMA table_info(form_responses)")).fetchall()
            resp_cols = {row[1] for row in resp_res}
            if "google_response_id" not in resp_cols:
                conn.execute(text("ALTER TABLE form_responses ADD COLUMN google_response_id VARCHAR(255)"))
            
            conn.commit()
        except Exception:
            pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
