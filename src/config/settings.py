import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_NAME = os.getenv("BOT_NAME", "AutomationBot")
PROXY_URL = os.getenv("PROXY_URL", "")
