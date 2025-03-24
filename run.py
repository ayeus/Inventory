import os
import sys

# Add the Inventory directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Change the working directory to the backend directory
os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backend'))

from app import app

if __name__ == '__main__':
    app.run(debug=True)