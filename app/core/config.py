import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    SERVER_NAME = os.getenv("SERVER_NAME", "localhost")
    SERVER_HOST = os.getenv("SERVER_HOST", "http://localhost:8000")
    
    # Database Settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./legal_obligations.db")
    
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # JIRA Settings
    JIRA_SERVER_URL = os.getenv("JIRA_SERVER_URL")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "KAN")
    JIRA_ISSUE_TYPE = os.getenv("JIRA_ISSUE_TYPE", "Task")
    
    # Project Management Settings
    DEFAULT_PROJECT_MANAGEMENT_TOOL = os.getenv("DEFAULT_PROJECT_MANAGEMENT_TOOL", "jira").lower()
    
    # Background Task Settings
    MAX_BACKGROUND_WORKERS = int(os.getenv("MAX_BACKGROUND_WORKERS", "4"))

settings = Settings()