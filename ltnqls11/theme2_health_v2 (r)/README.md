# VDT 증후군 관리 시스템 (React 버전)

직장인 근무 환경 개선을 위한 맞춤형 운동 관리 시스템을 React로 구현한 버전입니다.

## 🎯 프로젝트 개요

이 프로젝트는 원본 Streamlit 애플리케이션을 React로 완전히 재구현한 것으로, VDT(Visual Display Terminal) 증후군으로 고생하는 직장인들을 위한 맞춤형 건강 관리 솔루션을 제공합니다.

## ✨ 주요 기능

### 1. 🏥 증상 선택 및 통증 평가
- 거북목, 라운드숄더, 허리디스크, 손목터널증후군 등 주요 VDT 증후군 증상 선택
- 이모티콘 기반 통증 척도 (0-10점)로 직관적인 통증 수준 평가
- 주관적 상태 설명 입력

### 2. 👤 개인정보 입력
- 기본 정보 (나이, 성별, 경력, 작업시간 등)
- 생활 습관 (운동, 흡연, 음주, 수면)
- 고객 이력 관리 (초진/재진 구분)

### 3. 🖥️ 작업환경 평가
- 책상, 의자, 모니터, 키보드/마우스 환경 평가
- 100점 만점 환경 점수 자동 계산
- 올바른 자세 가이드 제공

### 4. 📅 개인 운동 설문조사
- 운동 가능 요일 및 시간 설정
- 운동 목표 및 난이도 수준 선택
- 현재 체력 수준 및 부상 이력 확인

### 5. 🤖 AI 기반 운동 추천
- 개인 상태 분석을 통한 운동 목적 자동 추천
- 맞춤형 운동 루틴 생성
- 요일별 상세 운동 계획 제공

### 6. ⏰ 휴식 알리미 설정
- 이메일/Slack 알림 설정
- 작업 강도별 맞춤 휴식 간격
- 알림 미리보기 및 테스트 기능

### 7. 📊 운동 관리 대시보드
- 실시간 운동 현황 모니터링
- 운동 기록 및 통증 개선 추적
- 개인화된 분석 리포트

## 🛠️ 기술 스택

- **Frontend**: React 18, React Router DOM
- **Styling**: CSS3 (CSS Variables, Grid, Flexbox)
- **Icons**: React Icons
- **Charts**: Recharts (차트 기능용)
- **HTTP Client**: Axios
- **Styling Library**: Styled Components

## 📦 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd vdt-health-management-react
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 개발 서버 실행
```bash
npm start
```

브라우저에서 `http://localhost:3000`으로 접속하여 애플리케이션을 확인할 수 있습니다.

### 4. 빌드
```bash
npm run build
```

## 📁 프로젝트 구조

```
src/
├── components/
│   ├── common/
│   │   ├── ProgressHeader.js      # 진행률 표시 컴포넌트
│   │   ├── PainScale.js           # 통증 척도 컴포넌트
│   │   └── *.css                  # 공통 컴포넌트 스타일
│   ├── Home.js                    # 홈 페이지
│   ├── ConditionSelection.js      # 증상 선택
│   ├── PersonalInfo.js            # 개인정보 입력
│   ├── WorkEnvironment.js         # 작업환경 평가
│   ├── ExerciseSurvey.js          # 운동 설문조사
│   ├── ExerciseRecommendation.js  # 운동 추천
│   ├── NotificationSetup.js       # 알리미 설정
│   ├── ExerciseManagement.js      # 운동 관리
│   ├── Sidebar.js                 # 사이드바 네비게이션
│   └── *.css                      # 각 컴포넌트별 스타일
├── App.js                         # 메인 앱 컴포넌트
├── App.css                        # 앱 전체 스타일
├── index.js                       # 앱 진입점
└── index.css                      # 전역 스타일
```

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary Blue**: #3b82f6 (메인 브랜드 컬러)
- **Accent Green**: #10b981 (성공, 완료 상태)
- **Accent Orange**: #f59e0b (경고, 주의 상태)
- **Accent Red**: #ef4444 (오류, 위험 상태)
- **Neutral Gray**: #6b7280 (보조 텍스트)

### 반응형 디자인
- **Desktop**: 1200px 이상
- **Tablet**: 768px - 1199px
- **Mobile**: 767px 이하

## 🔧 주요 기능 설명

### 세션 상태 관리
React의 `useState`를 사용하여 Streamlit의 `st.session_state`와 동일한 기능을 구현했습니다.

```javascript
const [sessionState, setSessionState] = useState({
  userData: {},
  selectedConditions: [],
  assessmentComplete: false,
  currentStep: 0,
  stepsCompleted: [false, false, false, false, false, false],
  // ... 기타 상태
});
```

### 라우팅 시스템
React Router를 사용하여 SPA(Single Page Application) 구조로 구현했습니다.

### 컴포넌트 기반 아키텍처
재사용 가능한 컴포넌트들로 구성되어 유지보수성과 확장성을 높였습니다.

## 🚀 배포

### Netlify 배포
```bash
npm run build
# build 폴더를 Netlify에 업로드
```

### Vercel 배포
```bash
npm run build
# Vercel CLI 또는 웹 인터페이스를 통해 배포
```

## 🔮 향후 개선 계획

1. **백엔드 API 연동**
   - 실제 데이터베이스 연동
   - 사용자 인증 시스템
   - 운동 기록 저장/조회

2. **고급 기능 추가**
   - 실시간 알림 시스템
   - 소셜 기능 (운동 친구, 그룹 챌린지)
   - 웨어러블 디바이스 연동

3. **성능 최적화**
   - 코드 스플리팅
   - 이미지 최적화
   - PWA 지원

4. **접근성 개선**
   - 스크린 리더 지원
   - 키보드 네비게이션
   - 고대비 모드

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이나 버그 리포트는 Issues 탭을 이용해주세요.

---

**건강한 개발 생활을 위한 첫 걸음을 함께 시작해보세요! 💪**