# 개발 환경 설정 가이드

## 시스템 요구사항

- Python 3.9 이상
- Node.js 16 이상
- SQLite 3

## 1. 프로젝트 클론 및 환경 변수 설정

```bash
# 환경 변수 파일 생성
cp .env.example .env

# .env 파일을 편집하여 필요한 값들을 설정
# - OPENAI_API_KEY: OpenAI API 키
# - SECRET_KEY: Flask 시크릿 키
```

## 2. 백엔드 설정

```bash
cd backend

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 초기화
cd ../database
python init_db.py

# Flask 서버 실행
cd ../backend
python app.py
```

백엔드 서버는 http://localhost:5000 에서 실행됩니다.

## 3. 프론트엔드 설정

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드는 http://localhost:3000 에서 실행됩니다.

## 4. n8n 설정

```bash
cd n8n

# n8n 설치
npm install

# n8n 실행
npm start
```

n8n은 http://localhost:5678 에서 실행됩니다.

## 5. 전체 시스템 실행 순서

1. 백엔드 서버 실행 (포트 5000)
2. n8n 서버 실행 (포트 5678)
3. 프론트엔드 개발 서버 실행 (포트 3000)

## 6. 개발 도구

### 데이터베이스 관리

```bash
# 데이터베이스 초기화 (모든 데이터 삭제)
cd database
python init_db.py --reset

# 샘플 데이터와 함께 초기화
python init_db.py
```

### API 테스트

```bash
# 헬스 체크
curl http://localhost:5000/health

# API 상태 확인
curl http://localhost:5000/
```

## 7. 문제 해결

### 포트 충돌
- 백엔드: 5000 포트가 사용 중인 경우 app.py에서 포트 변경
- 프론트엔드: 3000 포트가 사용 중인 경우 vite.config.ts에서 포트 변경
- n8n: 5678 포트가 사용 중인 경우 환경 변수로 포트 변경

### 의존성 오류
```bash
# Python 의존성 업데이트
pip install --upgrade -r requirements.txt

# Node.js 의존성 업데이트
npm update
```

### 데이터베이스 오류
```bash
# 데이터베이스 파일 삭제 후 재생성
rm database/marketing_automation.db
python database/init_db.py
```