"""
Configuration module for environment variables and logging setup.

This module loads and exposes environment variables required for the
Stripe–GitHub integration service. It also sets up structured logging
for consistent tracking in both local and cloud (Render) environments.
"""

import os
import logging
from dotenv import load_dotenv

# Load local environment variables only in development
load_dotenv()

# --- Environment Variables ---
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER")
REPO_NAME = os.getenv("REPO_NAME")

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("wix_stripe_github_access")
