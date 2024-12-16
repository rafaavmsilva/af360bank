from app import db

def upgrade():
    # Add the new columns
    db.engine.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE')
    db.engine.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS is_comissoes_admin BOOLEAN DEFAULT FALSE')
    db.engine.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS is_financeiro_admin BOOLEAN DEFAULT FALSE')

def downgrade():
    # Remove the columns if needed
    db.engine.execute('ALTER TABLE users DROP COLUMN IF EXISTS is_admin')
    db.engine.execute('ALTER TABLE users DROP COLUMN IF EXISTS is_comissoes_admin')
    db.engine.execute('ALTER TABLE users DROP COLUMN IF EXISTS is_financeiro_admin')
