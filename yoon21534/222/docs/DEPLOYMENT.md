# 배포 가이드

## 개발 환경 설정

### 1. 사전 요구사항
- Node.js 18+ 
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 실제 값으로 변경
```

### 3. 의존성 설치
```bash
# 루트 디렉토리에서
npm install

# 각 서비스별 의존성 설치
cd frontend && npm install
cd ../backend && npm install
cd ../scraper && npm install
cd ../ml-service && pip install -r requirements.txt
```

### 4. 데이터베이스 설정
```bash
# PostgreSQL 데이터베이스 생성
createdb blog_rpa

# 스키마 적용
psql -d blog_rpa -f database/schema.sql

# 백엔드 마이그레이션 실행
cd backend && npm run db:migrate
```

### 5. 개발 서버 실행
```bash
# 모든 서비스 동시 실행
npm run dev

# 또는 개별 실행
npm run frontend:dev  # React 개발 서버 (포트 3000)
npm run backend:dev   # Express API 서버 (포트 5000)
npm run scraper:dev   # 스크래핑 서비스
npm run ml:dev        # ML 서비스 (포트 8000)
```

## Docker를 이용한 배포

### 1. Docker Compose로 전체 스택 실행
```bash
# 환경 변수 설정
cp .env.example .env

# 컨테이너 빌드 및 실행
docker-compose up --build -d

# 로그 확인
docker-compose logs -f
```

### 2. 개별 서비스 빌드
```bash
# 프론트엔드
docker build -t blog-rpa-frontend ./frontend

# 백엔드
docker build -t blog-rpa-backend ./backend

# 스크래퍼
docker build -t blog-rpa-scraper ./scraper

# ML 서비스
docker build -t blog-rpa-ml ./ml-service
```

## 프로덕션 배포

### 1. AWS ECS 배포
```bash
# ECR 레포지토리 생성
aws ecr create-repository --repository-name blog-rpa-frontend
aws ecr create-repository --repository-name blog-rpa-backend
aws ecr create-repository --repository-name blog-rpa-scraper
aws ecr create-repository --repository-name blog-rpa-ml

# 이미지 빌드 및 푸시
./scripts/deploy-aws.sh
```

### 2. Kubernetes 배포
```bash
# 네임스페이스 생성
kubectl create namespace blog-rpa

# 시크릿 생성
kubectl create secret generic blog-rpa-secrets \
  --from-env-file=.env \
  --namespace=blog-rpa

# 배포
kubectl apply -f k8s/ --namespace=blog-rpa
```

### 3. 환경별 설정

#### 개발 환경
- 로컬 PostgreSQL/Redis 사용
- 디버그 모드 활성화
- 핫 리로드 활성화

#### 스테이징 환경
- AWS RDS PostgreSQL 사용
- AWS ElastiCache Redis 사용
- SSL 인증서 적용
- 로그 수집 활성화

#### 프로덕션 환경
- 고가용성 데이터베이스 설정
- 로드 밸런서 구성
- 모니터링 및 알림 설정
- 백업 및 복구 전략 구현

## 모니터링 및 로깅

### 1. 애플리케이션 모니터링
```bash
# Prometheus + Grafana 설정
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. 로그 수집
- ELK Stack (Elasticsearch, Logstash, Kibana)
- 중앙화된 로그 관리
- 에러 추적 및 알림

### 3. 성능 모니터링
- API 응답 시간 모니터링
- 데이터베이스 쿼리 성능
- 스크래핑 작업 성공률
- 시스템 리소스 사용률

## 보안 설정

### 1. SSL/TLS 인증서
```bash
# Let's Encrypt 인증서 발급
certbot --nginx -d yourdomain.com
```

### 2. 방화벽 설정
```bash
# UFW 방화벽 설정
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. 데이터베이스 보안
- 강력한 패스워드 설정
- 네트워크 접근 제한
- 정기적인 백업
- 암호화 설정

## 백업 및 복구

### 1. 데이터베이스 백업
```bash
# 자동 백업 스크립트
./scripts/backup-db.sh

# 복구
./scripts/restore-db.sh backup_file.sql
```

### 2. 파일 백업
```bash
# 애플리케이션 파일 백업
tar -czf app-backup-$(date +%Y%m%d).tar.gz /app

# S3에 백업 업로드
aws s3 cp app-backup-*.tar.gz s3://your-backup-bucket/
```

## 트러블슈팅

### 1. 일반적인 문제
- 포트 충돌: `lsof -i :포트번호`로 확인
- 메모리 부족: 시스템 리소스 모니터링
- 데이터베이스 연결 실패: 연결 설정 확인

### 2. 로그 확인
```bash
# Docker 로그
docker-compose logs service_name

# 시스템 로그
journalctl -u service_name -f

# 애플리케이션 로그
tail -f logs/app.log
```

### 3. 성능 최적화
- 데이터베이스 인덱스 최적화
- Redis 캐싱 전략
- CDN 설정
- 이미지 최적화