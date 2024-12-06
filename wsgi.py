import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Add Comissoes.af360bank to Python path
comissoes_path = os.path.join(project_root, 'Comissoes.af360bank')
sys.path.append(comissoes_path)

from app import app

if __name__ == "__main__":
    app.run()
