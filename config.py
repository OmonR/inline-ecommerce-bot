import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
API_CRYPTO_TOKEN = os.getenv("API_CRYPTO_TOKEN")
ADMIN_ID = [int(admin_id) for admin_id in os.getenv("ADMIN_ID").split(",")]

SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME")
MIN_ORDER_PRICE = os.getenv("MIN_ORDER_PRICE")
ADDRESSES = os.getenv("ADDRESSES").split(",")
