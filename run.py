import sys
import os

# Add project directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

# Then continue with importing app and creating it
from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
