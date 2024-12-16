from app import db
from migrations.add_admin_columns import upgrade

if __name__ == '__main__':
    print("Running database migration...")
    upgrade()
    print("Migration completed successfully!")
