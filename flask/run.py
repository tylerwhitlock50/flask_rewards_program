from app import create_app
from config import DevelopmentConfig as Config
from dotenv import load_dotenv

load_dotenv()
app = create_app(Config)

if __name__ == "__main__":
    app.run(debug=True)
