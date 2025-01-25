from app import db
from models import User

def create_admin():
    admin = User(email='admin@example.com', password='admin_password', role='admin', is_active=True)
    db.session.add(admin)
    db.session.commit()
    print("Admin account created.")

if __name__ == '__main__':
    create_admin()
