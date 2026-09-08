"""
Database backup and snapshot utility for FormMind AI.
Creates timestamped backups of the active database.
"""
import os
import shutil
import datetime
from pathlib import Path

def backup_database():
    root_dir = Path(__file__).resolve().parent.parent
    db_file = root_dir / "formmind.db"
    backup_dir = root_dir / "backups"
    
    if not db_file.exists():
        print(f"No local SQLite database found at {db_file}")
        return

    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"formmind_backup_{timestamp}.db"

    shutil.copy2(db_file, backup_path)
    print(f"Database backup created successfully at: {backup_path}")

if __name__ == "__main__":
    backup_database()
