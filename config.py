import os

from dotenv import load_dotenv

load_dotenv()

SECURITY_KEY = os.environ.get("SECURITY_KEY")
