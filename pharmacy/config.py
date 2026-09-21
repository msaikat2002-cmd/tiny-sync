"""
Configuration settings for Pharmacy Billing v0.1
All paths are relative to the project root.
"""

import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'pharmacy.db')

# Backup directory
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')

# Server configuration
HOST = '127.0.0.1'
PORT = 8080

# Application info
APP_NAME = 'MediStore'
APP_VERSION = 'v0.1'
