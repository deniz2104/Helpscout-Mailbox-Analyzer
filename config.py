"""Configuration settings for HelpScout data fetcher"""
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("HELPSCOUT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("HELPSCOUT_CLIENT_SECRET")

MAILBOX_ID = 21530