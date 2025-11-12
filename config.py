import os
from datetime import timedelta

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-to-random-secret-key'
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    QUEST_FILE = os.path.join(BASE_DIR, "data", "questions.xlsx")
    RESP_FILE = os.path.join(BASE_DIR, "data", "responses.csv")  # Changed to CSV
    STUDENTS_FILE = os.path.join(BASE_DIR, "data", "passwords", "students.xlsx")   # ✅ NEW
    
    # Quiz settings
    QUIZ_DURATION_MINUTES = 1
    NUM_QUESTIONS = 10
    
    # Security settings
    
    # Mapping of lab workstation IPs to workstation names
    WORKSTATION_MAP = {
        "127.0.0.1":"WS-local" ,
        "192.168.1.1":"WS-01" ,
        "192.168.1.2": "WS-02",
        "192.168.1.3": "WS-03",
        "192.168.1.4": "WS-04",
        "192.168.1.5": "WS-05",
        "192.168.1.6": "WS-06",
        "192.168.1.7": "WS-07",
        "192.168.1.8": "WS-08",
        "192.168.1.9": "WS-09",
        "192.168.1.10": "WS-10",
        "192.168.1.11": "WS-11",
        "192.168.1.12": "WS-12",
        "192.168.1.13": "WS-13",
        "192.168.1.14": "WS-14",
        "192.168.1.16": "WS-16",
        "192.168.1.15": "WS-15",
        "192.168.1.17": "WS-17",
        "192.168.1.18": "WS-18",
        "192.168.1.19": "WS-19",
        "192.168.1.20": "WS-20",
        "192.168.1.21": "WS-21",
        "192.168.1.22": "WS-22",
        "192.168.1.23": "WS-23",
        "192.168.1.24": "WS-24",
        "192.168.1.25": "WS-25",
        "192.168.1.26": "WS-26",
        "192.168.1.27": "WS-27",
        "192.168.1.28": "WS-28",
        "192.168.1.29": "WS-29",
        "192.168.1.30": "WS-30",
        "192.168.1.31": "WS-31",
        
        "192.168.1.30": "WS-32",
    }
    ALLOWED_IPS = list(WORKSTATION_MAP.keys())
    
    # If True, only IPs in ALLOWED_IPS can access
    ENABLE_IP_RESTRICTION = True

    # Ngrok settings
    # Update this whenever you start a new ngrok tunnel
    # If running locally without ngrok, leave as empty string
    NGROK_DOMAIN = "endotrophic-kelli-cantharidean.ngrok-free.dev"
    
    # Proctoring settings
    ENABLE_FULLSCREEN_CHECK = True
    ENABLE_TAB_SWITCH_DETECTION = True
    FULLSCREEN_CHECK_INTERVAL = 1000  # milliseconds
    
    # ✅ Authentication settings
    ENABLE_PASSWORD_AUTH = True  # Set to False to allow login with just Roll Number
    
    # Admin credentials (for viewing results)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'  # Change this!
