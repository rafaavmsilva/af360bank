from app import db, User
from werkzeug.security import generate_password_hash

def create_admin_user(email, password):
    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        # Update existing user to admin if not already
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
            print(f"User {email} has been updated to admin status.")
        else:
            print(f"User {email} is already an admin.")
        return

    # Create new admin user
    admin = User(
        email=email,
        password_hash=generate_password_hash(password),
        email_verified=True,
        is_admin=True
    )
    
    try:
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user {email} created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

if __name__ == "__main__":
    # Replace these with your desired admin credentials
    admin_email = "admin@example.com"
    admin_password = "Admin@123"  # Make sure to use a strong password in production
    
    create_admin_user(admin_email, admin_password)
