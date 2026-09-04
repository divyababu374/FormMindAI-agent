import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.form import Form
from app.models.user import User
from app.api.forms import sync_latest_responses

db = SessionLocal()
form = db.query(Form).filter(Form.id == "754ee58e-55be-4271-badc-8b08edbba18b").first()
user = db.query(User).filter(User.id == form.user_id).first()

print(f"Form: {form.title}, User: {user.email}, Google connected: {user.is_google_connected}")
try:
    res = sync_latest_responses(form.id, db=db, current_user=user)
    print("Sync succeeded:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
