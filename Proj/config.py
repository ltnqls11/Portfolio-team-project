import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Google Sheets API 설정
GOOGLE_SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = os.getenv('GOOGLE_SHEETS_CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.getenv('GOOGLE_SHEETS_TOKEN_FILE', 'token.json')

# Gmail API 설정
GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'gmail_credentials.json')

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
NAVER_CAFE_ID = os.getenv('NAVER_CAFE_ID')
NAVER_MENU_ID = os.getenv('NAVER_MENU_ID')

# 네이버 검색 설정
NAVER_SEARCH_BASE_URL = "https://search.naver.com/search.naver"
BLOG_TAB_SELECTOR = "a[data-tab='blog']"

# n8n 웹훅 설정
N8N_BASE_URL = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
N8N_EMAIL_WEBHOOK_ID = os.getenv('N8N_EMAIL_WEBHOOK_ID', 'webhook-email-start')
N8N_CAFE_WEBHOOK_ID = os.getenv('N8N_CAFE_WEBHOOK_ID', 'webhook-cafe-post')

# API 서버 설정
API_SERVER_HOST = os.getenv('API_SERVER_HOST', 'localhost')
API_SERVER_PORT = int(os.getenv('API_SERVER_PORT', 5000))

# 이메일 정규식 패턴 (요구사항에서 명시한 정확한 패턴)
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# 브라우저 설정
BROWSER_TIMEOUT = int(os.getenv('BROWSER_TIMEOUT', 10))
PAGE_LOAD_DELAY = int(os.getenv('PAGE_LOAD_DELAY', 2))

# 기본 설정
DEFAULT_SHEET_ID = os.getenv('DEFAULT_SHEET_ID', '')
DEFAULT_SHEET_NAME = os.getenv('DEFAULT_SHEET_NAME', 'Sheet1')

# 보안 설정
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')