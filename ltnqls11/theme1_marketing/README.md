# 온라인 마케팅 연계 플랫폼

기업이 채널/인플루언서를 고르고, 맞춤형 홍보 문구를 자동 생성·배포·관리하는 올인원 플랫폼입니다.

## 📁 프로젝트 구조

```
ltnqls11/
├── 마케팅_플랫폼_설계서.md      # 전체 플랫폼 설계 문서
├── backend_api_spec.md          # 백엔드 API 명세서
├── n8n_workflows.md             # n8n 자동화 워크플로우 설계
├── start.bat                    # Windows 실행 스크립트
├── README.md                    # 이 파일
└── marketing-integration-platform/  # React 프론트엔드
    ├── src/
    │   ├── components/          # React 컴포넌트
    │   ├── pages/              # 페이지 컴포넌트
    │   ├── services/           # API 서비스
    │   ├── types/              # TypeScript 타입 정의
    │   ├── App.tsx             # 메인 앱 컴포넌트
    │   └── App.css             # 스타일시트
    ├── public/
    ├── package.json
    └── .env.example            # 환경 변수 예시
```

## 🚀 빠른 시작

### 1. 프론트엔드 실행

Windows에서 간편하게 실행:
```bash
start.bat
```

수동 실행:
```bash
cd marketing-integration-platform
npm install
set NODE_OPTIONS=--openssl-legacy-provider
npm start
```

### 2. 환경 설정

`.env.example` 파일을 `.env`로 복사하고 필요한 설정을 수정하세요:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 핵심 기능

### 1. 문구 자동화
- 제품/경쟁사/사례를 학습해 채널별 톤·SEO 구조로 문구 생성
- 네이버 블로그, 인스타그램, 카카오채널 등 채널별 최적화

### 2. 매칭·연계
- 카테고리·도달·참여율에 맞춰 나노/마이크로 인플루언서 추천
- 자동 연락 및 응답 추적

### 3. 운영 자동화
- n8n으로 수집→정제→생성→발송→로그→리포트까지 파이프라인화
- 실시간 성과 모니터링

## 🛠 기술 스택

### 프론트엔드
- **React** + TypeScript
- **Tailwind CSS** (스타일링)
- **Axios** (API 통신)
- **React Router** (라우팅)

### 백엔드 (설계)
- **FastAPI** + PostgreSQL
- **SQLAlchemy/SQLModel** (ORM)
- **Celery** + Redis (백그라운드 작업)
- **JWT** (인증)

### 자동화
- **n8n** (워크플로우 오케스트레이션)
- **OpenAI API** (문구 생성)
- **SMTP/Gmail API** (이메일 발송)

## 📊 주요 화면

### 대시보드
- 진행중 캠페인 현황
- 오늘 할 일 (승인 대기 문구, 보낸 제안, 답장)
- 주요 성과 지표

### 캠페인 관리
- 캠페인 생성 및 편집
- 채널별 문구 생성 및 승인
- 인플루언서 매칭 및 연락

### 성과 분석
- 채널별 성과 비교
- 인플루언서별 성과 추적
- 주간/월간 리포트

## 🔧 개발 가이드

### 컴포넌트 구조
```typescript
// 캠페인 타입 정의
interface Campaign {
  id: string;
  title: string;
  objective: string;
  budget: number;
  channels: Channel[];
  keywords: string[];
  status: 'draft' | 'active' | 'paused' | 'completed';
}

// API 서비스 예시
export const createCampaign = async (data: Omit<Campaign, 'id'>): Promise<Campaign> => {
  const response = await axios.post('/api/campaigns', data);
  return response.data;
};
```

### 스타일링 가이드
- Tailwind CSS 유틸리티 클래스 사용
- 컴포넌트별 일관된 디자인 시스템
- 반응형 디자인 지원

## 📋 다음 단계

### Phase 1: MVP 개발
- [ ] 백엔드 API 구현 (FastAPI)
- [ ] 데이터베이스 스키마 구축
- [ ] 기본 CRUD 기능 완성

### Phase 2: 자동화 구축
- [ ] n8n 워크플로우 구현
- [ ] OpenAI API 연동
- [ ] 이메일 발송 자동화

### Phase 3: 고도화
- [ ] 크리에이터 크롤링 시스템
- [ ] 성과 분석 대시보드
- [ ] 실시간 알림 시스템

## 🔒 보안 고려사항

- API 키 환경 변수 관리
- 개인정보 암호화 저장
- Rate Limiting 구현
- CORS 설정
- SQL Injection 방지

## 📞 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요.

---

**주의사항**: 이 프로젝트는 현재 프론트엔드 프로토타입 단계입니다. 실제 운영을 위해서는 백엔드 API와 데이터베이스 구축이 필요합니다.