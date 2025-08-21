# 🏥 건강 관리 운동 추천 앱

개인 맞춤형 운동 루틴과 건강 관리 가이드를 제공하는 React 웹 애플리케이션입니다.

## ✨ 주요 기능

### 🎯 개인 맞춤 운동 추천
- **증상 기반 추천**: 거북목, 둥근 어깨, 디스크 탈출증, 손목 터널 증후군
- **통증 위치 및 심각도** 분석
- **작업 환경별** 맞춤 운동 (사무실, 서서하는 작업, 육체 노동 등)
- **운동 모드** 선택 (예방, 운동, 재활)

### 📱 사용자 정보 입력
- 증상 다중 선택
- 통증 위치 및 심각도 평가
- 작업 환경 및 일상 습관 분석
- 나이, 근무 시간, 위치 정보

### 🎬 YouTube 운동 비디오 추천
- 증상별 관련 운동 비디오 검색
- 댓글 분석을 통한 사용자 적합도 평가
- 평점 및 조회수 기반 추천

### ⏰ 스마트 알림 시스템
- 휴식 시간 알림 (60분마다)
- 운동 알림 (매일 오전 9시, 오후 6시)
- 브라우저 알림 지원

### 💡 건강 관리 팁
- 자세 교정 가이드
- 휴식 시간 관리
- 규칙적 운동 권장사항
- 수분 섭취 안내

## 🚀 시작하기

### 필수 요구사항
- Node.js 14.0 이상
- npm 또는 yarn

### 설치 및 실행

1. **프로젝트 클론**
```bash
git clone <repository-url>
cd health-exercise-app
```

2. **의존성 설치**
```bash
npm install
```

3. **개발 서버 실행**
```bash
npm start
```

4. **브라우저에서 확인**
```
http://localhost:3000
```

### 빌드
```bash
npm run build
```

## 🛠️ 기술 스택

- **Frontend**: React 18, TypeScript
- **스타일링**: CSS3, CSS Grid, Flexbox
- **상태 관리**: React Hooks
- **외부 API**: YouTube Data API v3
- **알림**: Web Notifications API

## 📁 프로젝트 구조

```
src/
├── components/           # React 컴포넌트
│   ├── UserInfoForm.tsx      # 사용자 정보 입력 폼
│   ├── UserInfoForm.css
│   ├── ExerciseRecommendation.tsx  # 운동 추천 결과
│   └── ExerciseRecommendation.css
├── services/            # 서비스 로직
│   ├── youtubeService.ts     # YouTube API 연동
│   └── notificationService.ts # 알림 서비스
├── data/               # 정적 데이터
│   └── exercises.ts         # 운동 데이터
├── types/              # TypeScript 타입 정의
│   └── index.ts
├── App.tsx             # 메인 앱 컴포넌트
├── App.css
└── index.tsx           # 앱 진입점
```

## 🔧 설정

### YouTube API 설정
1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. YouTube Data API v3 활성화
3. API 키 생성
4. `src/services/youtubeService.ts`에서 API 키 설정:
```typescript
const YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY';
```

### 환경 변수 설정 (권장)
```bash
# .env 파일 생성
REACT_APP_YOUTUBE_API_KEY=your_api_key_here
```

## 📱 사용법

### 1. 사용자 정보 입력
- 증상 선택 (복수 선택 가능)
- 통증 위치 및 심각도 평가
- 작업 환경 및 일상 습관 입력
- 개인 정보 입력 (나이, 근무 시간 등)

### 2. 운동 추천 받기
- 입력된 정보를 바탕으로 맞춤 운동 루틴 생성
- YouTube 운동 비디오 추천
- 알림 설정 활성화

### 3. 운동 실행
- 추천된 운동 루틴 따라하기
- 비디오 시청 및 운동 수행
- 정기적인 휴식 알림 확인

## 🎨 UI/UX 특징

- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **직관적 인터페이스**: 사용자 친화적인 폼과 결과 표시
- **시각적 피드백**: 로딩 애니메이션, 호버 효과
- **접근성**: 키보드 네비게이션, 스크린 리더 지원

## 🔒 보안 및 개인정보

- 모든 데이터는 클라이언트 측에서만 처리
- 서버에 개인정보 전송하지 않음
- 브라우저 로컬 스토리지 활용
- YouTube API 키는 환경 변수로 관리

## 🐛 알려진 이슈

- YouTube API 할당량 초과 시 모의 데이터 사용
- 일부 브라우저에서 알림 기능 제한
- 모바일에서 일부 CSS 애니메이션 성능 이슈

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 이슈를 통해 제출해 주세요.

---

**건강한 하루 되세요! 💪**
