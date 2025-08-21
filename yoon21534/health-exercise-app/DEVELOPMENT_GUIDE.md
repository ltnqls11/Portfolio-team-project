# 🚀 건강 관리 운동 추천 앱 - 개발 가이드

## 📋 프로젝트 개요

이 프로젝트는 React와 TypeScript를 사용하여 개발된 건강 관리 운동 추천 웹 애플리케이션입니다. 사용자의 증상, 작업 환경, 개인 정보를 바탕으로 맞춤형 운동 루틴을 제공하고, YouTube API를 활용한 운동 비디오 추천 및 스마트 알림 시스템을 포함합니다.

## 🎯 주요 기능 구현 가이드

### 1. 사용자 정보 입력 시스템

#### 구현 포인트
- **증상 다중 선택**: 체크박스를 활용한 복수 선택 기능
- **통증 심각도 평가**: 1-5점 라디오 버튼 시스템
- **작업 환경 분석**: 드롭다운을 통한 환경별 분류
- **폼 검증**: 필수 입력 항목 검증 및 사용자 피드백

#### 코드 예시
```typescript
// 증상 선택 핸들러
const handleSymptomChange = (symptom: Symptom) => {
  setFormData(prev => ({
    ...prev,
    symptoms: prev.symptoms?.includes(symptom)
      ? prev.symptoms.filter(s => s !== symptom)
      : [...(prev.symptoms || []), symptom]
  }));
};

// 폼 제출 검증
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  if (formData.symptoms && formData.symptoms.length > 0) {
    onSubmit(formData as UserInfo);
  } else {
    alert('최소 하나의 증상을 선택해주세요.');
  }
};
```

### 2. 운동 추천 알고리즘

#### 구현 포인트
- **증상별 운동 매핑**: 각 증상에 맞는 운동 루틴 연결
- **작업 환경별 추가 운동**: 환경에 따른 추가 운동 추천
- **난이도 조정**: 사용자 수준에 맞는 운동 난이도 설정

#### 코드 예시
```typescript
// 증상별 운동 루틴 추천
const generateRecommendations = () => {
  const routines: ExerciseRoutine[] = [];
  
  // 증상별 기본 루틴
  userInfo.symptoms.forEach(symptom => {
    const symptomRoutines = exerciseRoutines[symptom] || [];
    routines.push(...symptomRoutines);
  });

  // 작업 환경별 추가 운동
  const workEnvExercises = workEnvironmentExercises[userInfo.workEnvironment] || [];
  if (workEnvExercises.length > 0) {
    routines.push({
      id: 'work_env_routine',
      name: `${getWorkEnvironmentLabel(userInfo.workEnvironment)} 맞춤 루틴`,
      exercises: workEnvExercises,
      totalDuration: workEnvExercises.reduce((sum, ex) => sum + ex.duration, 0),
      frequency: '근무 중 2-3회',
      description: '작업 환경에 맞춘 간단한 스트레칭 루틴입니다.'
    });
  }
  
  return routines;
};
```

### 3. YouTube API 연동

#### 구현 포인트
- **API 키 관리**: 환경 변수를 통한 안전한 API 키 관리
- **비디오 검색**: 증상별 키워드 기반 비디오 검색
- **댓글 분석**: 사용자 피드백 기반 적합도 평가
- **에러 핸들링**: API 실패 시 모의 데이터 사용

#### 코드 예시
```typescript
// YouTube 비디오 검색
export const searchExerciseVideos = async (
  symptoms: string[],
  maxResults: number = 10
): Promise<YouTubeVideo[]> => {
  try {
    const keywords = symptoms
      .map(symptom => exerciseKeywords[symptom] || [])
      .flat()
      .slice(0, 3);

    const searchQuery = keywords.join(' OR ');
    
    const response = await fetch(
      `${YOUTUBE_API_BASE_URL}/search?part=snippet&q=${encodeURIComponent(searchQuery)}&type=video&maxResults=${maxResults}&key=${YOUTUBE_API_KEY}`
    );

    if (!response.ok) {
      throw new Error('YouTube API 요청 실패');
    }

    const data = await response.json();
    return processVideoData(data);
  } catch (error) {
    console.error('YouTube 비디오 검색 오류:', error);
    return getMockExerciseVideos(); // 폴백 데이터
  }
};
```

### 4. 알림 시스템

#### 구현 포인트
- **권한 요청**: 브라우저 알림 권한 관리
- **타이머 설정**: 정기적인 알림 스케줄링
- **작업 시간 체크**: 근무 시간 내 알림 제한
- **사용자 설정**: 알림 간격 및 유형 설정

#### 코드 예시
```typescript
// 알림 권한 요청
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!('Notification' in window)) {
    console.log('이 브라우저는 알림을 지원하지 않습니다.');
    return false;
  }

  if (Notification.permission === 'granted') {
    return true;
  }

  const permission = await Notification.requestPermission();
  return permission === 'granted';
};

// 휴식 시간 알림 시작
export const startBreakNotifications = (interval: number): NodeJS.Timeout | null => {
  if (!('Notification' in window) || Notification.permission !== 'granted') {
    return null;
  }

  return setInterval(() => {
    new Notification('휴식 시간입니다!', {
      body: '잠시 일어나서 스트레칭을 해보세요.',
      icon: '/favicon.ico',
      tag: 'break-notification'
    });
  }, interval * 60 * 1000);
};
```

## 🛠️ 개발 환경 설정

### 1. TypeScript 설정
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

### 2. 환경 변수 설정
```bash
# .env
REACT_APP_YOUTUBE_API_KEY=your_youtube_api_key_here
REACT_APP_APP_NAME=건강 관리 운동 추천
```

### 3. 의존성 관리
```json
// package.json 주요 의존성
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.28",
    "@types/react-dom": "^18.0.11",
    "@types/react-router-dom": "^5.3.3",
    "typescript": "^4.9.5"
  }
}
```

## 🎨 UI/UX 개발 가이드

### 1. 반응형 디자인
```css
/* CSS Grid를 활용한 반응형 레이아웃 */
.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

/* 모바일 최적화 */
@media (max-width: 768px) {
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .time-inputs {
    grid-template-columns: 1fr;
  }
}
```

### 2. 접근성 고려사항
```typescript
// 키보드 네비게이션 지원
const handleKeyPress = (event: React.KeyboardEvent, callback: () => void) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    callback();
  }
};

// 스크린 리더 지원
<button 
  aria-label="증상 선택"
  onKeyPress={(e) => handleKeyPress(e, () => handleSymptomChange(symptom))}
>
  {symptom.label}
</button>
```

### 3. 로딩 상태 관리
```typescript
// 로딩 상태 컴포넌트
const LoadingSpinner: React.FC = () => (
  <div className="loading">
    <div className="spinner"></div>
    <p>맞춤 운동을 분석하고 있습니다...</p>
  </div>
);

// 조건부 렌더링
{loading ? <LoadingSpinner /> : <ExerciseRecommendation />}
```

## 🔧 디버깅 및 테스트

### 1. 콘솔 로깅
```typescript
// 개발 환경에서만 로그 출력
const DEBUG = process.env.NODE_ENV === 'development';

export const logDebug = (message: string, data?: any) => {
  if (DEBUG) {
    console.log(`[DEBUG] ${message}`, data);
  }
};
```

### 2. 에러 바운더리
```typescript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>문제가 발생했습니다. 페이지를 새로고침해주세요.</h1>;
    }

    return this.props.children;
  }
}
```

### 3. 단위 테스트 예시
```typescript
// UserInfoForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import UserInfoForm from './UserInfoForm';

test('증상 선택 기능', () => {
  const mockOnSubmit = jest.fn();
  render(<UserInfoForm onSubmit={mockOnSubmit} />);
  
  const symptomCheckbox = screen.getByLabelText('거북목');
  fireEvent.click(symptomCheckbox);
  
  expect(symptomCheckbox).toBeChecked();
});
```

## 📱 성능 최적화

### 1. 컴포넌트 최적화
```typescript
// React.memo를 활용한 불필요한 리렌더링 방지
const ExerciseItem = React.memo<{ exercise: Exercise }>(({ exercise }) => {
  return (
    <div className="exercise-item">
      <h3>{exercise.name}</h3>
      <p>{exercise.description}</p>
    </div>
  );
});

// useMemo를 활용한 계산 결과 캐싱
const recommendedRoutines = useMemo(() => {
  return generateRecommendations(userInfo);
}, [userInfo.symptoms, userInfo.workEnvironment]);
```

### 2. 이미지 최적화
```typescript
// 지연 로딩을 위한 Intersection Observer 활용
const LazyImage: React.FC<{ src: string; alt: string }> = ({ src, alt }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { threshold: 0.1 }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <img
      ref={imgRef}
      src={isInView ? src : ''}
      alt={alt}
      onLoad={() => setIsLoaded(true)}
      className={isLoaded ? 'loaded' : 'loading'}
    />
  );
};
```

## 🚀 배포 가이드

### 1. 빌드 최적화
```bash
# 프로덕션 빌드
npm run build

# 빌드 분석
npm install -g serve
serve -s build -l 3000
```

### 2. 환경별 설정
```typescript
// config/environment.ts
const config = {
  development: {
    apiUrl: 'http://localhost:3000',
    youtubeApiKey: process.env.REACT_APP_YOUTUBE_API_KEY,
    enableLogging: true
  },
  production: {
    apiUrl: 'https://your-production-domain.com',
    youtubeApiKey: process.env.REACT_APP_YOUTUBE_API_KEY,
    enableLogging: false
  }
};

export default config[process.env.NODE_ENV || 'development'];
```

## 📚 추가 학습 리소스

### React & TypeScript
- [React 공식 문서](https://reactjs.org/docs/getting-started.html)
- [TypeScript 핸드북](https://www.typescriptlang.org/docs/)
- [React Hooks 가이드](https://reactjs.org/docs/hooks-intro.html)

### API 연동
- [YouTube Data API v3 문서](https://developers.google.com/youtube/v3)
- [Fetch API 가이드](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

### UI/UX
- [CSS Grid 가이드](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [반응형 디자인 패턴](https://www.smashingmagazine.com/2011/01/guidelines-for-responsive-web-design/)

### 성능 최적화
- [React 성능 최적화](https://reactjs.org/docs/optimizing-performance.html)
- [웹 성능 모니터링](https://web.dev/performance/)

---

## 💡 개발 팁

1. **컴포넌트 분리**: 단일 책임 원칙에 따라 컴포넌트를 적절히 분리하세요.
2. **타입 안전성**: TypeScript의 타입 시스템을 최대한 활용하세요.
3. **에러 핸들링**: 사용자 친화적인 에러 메시지를 제공하세요.
4. **접근성**: 모든 사용자가 앱을 사용할 수 있도록 접근성을 고려하세요.
5. **성능**: 불필요한 리렌더링을 방지하고 최적화를 지속적으로 수행하세요.

**건강한 코드 작성하세요! 💻💪**
