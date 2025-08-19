# Marketing Automation RPA System

마케팅 자동화를 위한 React 기반 RPA(Robotic Process Automation) 시스템입니다.

## 프로젝트 구조

```
├── frontend/          # React + Vite 프론트엔드
├── backend/           # Python Flask 백엔드
├── database/          # SQLite 데이터베이스 파일
├── n8n/              # n8n 워크플로우 설정
└── docs/             # 프로젝트 문서
```

## 기술 스택

### Frontend
- React 18
- Vite
- TypeScript
- Material-UI
- Axios

### Backend
- Python 3.9+
- Flask
- SQLAlchemy
- SQLite
- OpenAI API

### Automation
- n8n (워크플로우 자동화)

## 개발 환경 설정

### 백엔드 설정
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 프론트엔드 설정
```bash
cd frontend
npm install
npm run dev
```

### n8n 설정
```bash
cd n8n
npx n8n start
```

## 환경 변수

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///database/marketing_automation.db
SECRET_KEY=your_secret_key
FLASK_ENV=development
```