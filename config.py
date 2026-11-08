# config.py - Configuration settings for CleanConnect
# =====================================================
# Maps are now powered by FREE Leaflet.js + OpenStreetMap.
# No Google Maps API key needed!

import os

class Config:
    # Secret key for session security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cleanconnect-secret-key-change-this-2024'

    # ----------------------------------------------------
    # MYSQL DATABASE CONFIGURATION
    # ----------------------------------------------------
    # HOW TO FIND / RESET YOUR MYSQL ROOT PASSWORD:
    #
    #   Step 1: Open MySQL Workbench
    #   Step 2: Go to Server > Users and Privileges
    #   Step 3: Click 'root' > 'Change Password'
    #   Step 4: Set a new password (e.g. 'Admin@1234')
    #   Step 5: Click 'Apply'
    #   Step 6: Update MYSQL_PASSWORD below with that password
    #
    #   OR run in MySQL Workbench query window:
    #       ALTER USER 'root'@'localhost' IDENTIFIED BY 'Admin@1234';
    #       FLUSH PRIVILEGES;
    # ----------------------------------------------------
    MYSQL_HOST     = 'localhost'
    MYSQL_USER = 'cleanuser'
    MYSQL_PASSWORD = 'your_password_here'
    MYSQL_DB       = 'cleanconnect'

    # File upload settings
    UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}