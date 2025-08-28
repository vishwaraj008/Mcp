# src/config/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Base URLs
MOAD_URL = os.getenv("MOAD_URL")
ATHENA_BASE_URL = os.getenv('ATHENA_BASE_URL')

# API Keys
MOAD_API_KEY = os.getenv("MOAD_API_KEY")
ATHENA_API_KEY = os.getenv("ATHENA_API_KEY")
