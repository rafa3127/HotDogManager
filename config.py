"""
Configuration module that loads environment variables.

Author: Rafael Correa
Date: November 12, 2025
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub configuration
GITHUB_OWNER = os.getenv('GITHUB_OWNER', '')
GITHUB_REPO = os.getenv('GITHUB_REPO', '')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')

# Data directory
DATA_DIR = os.getenv('DATA_DIR', 'data')