import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# YouTube API 설정
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Gemini AI 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Supabase 데이터베이스 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Google Sheets 설정
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

# Slack 설정
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Gmail 설정
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")

# 작업 시간 설정
WORK_START_TIME = os.getenv("WORK_START_TIME", "09:00")
WORK_END_TIME = os.getenv("WORK_END_TIME", "18:00")
REST_INTERVAL = os.getenv("REST_INTERVAL", "30")

# 쿠팡 파트너스 설정
COUPANG_PARTNER_ID = os.getenv("COUPANG_PARTNER_ID", "AF6363203")

# AdSense 설정
ADSENSE_PUBLISHER_ID = os.getenv("ADSENSE_PUBLISHER_ID", "")

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "")

# 로그 레벨
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
