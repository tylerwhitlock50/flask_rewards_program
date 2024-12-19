from app import create_app
from config import ProductionConfig as Config
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv('PROD_DATABASE_URL'))

app = create_app(Config)

if __name__ == "__main__":
    app.run(debug=True)
