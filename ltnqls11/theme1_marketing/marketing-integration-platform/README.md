# 온라인 마케팅 연계 플랫폼

기업이 채널/인플루언서를 고르고, 맞춤형 홍보 문구를 자동 생성·배포·관리하는 올인원 플랫폼입니다. 

## 핵심 기능

1. **문구 자동화**: 제품/경쟁사/사례를 학습해 채널별 톤·SEO 구조로 문구 생성
2. **매칭·연계**: 카테고리·도달·참여율에 맞춰 나노/마이크로 인플루언서를 추천 및 연락 자동화
3. **운영 자동화**: n8n으로 수집→정제→생성→발송→로그→리포트까지 파이프라인화

## 지원 채널

- 네이버 블로그
- 블로그스팟  
- 티스토리
- 카카오채널
- 인스타그램

## 기술 스택

- **Frontend**: React + TypeScript
- **Backend**: FastAPI + PostgreSQL  
- **자동화**: n8n
- **크롤링**: Python (Requests/BS4)

## 프로젝트 구조

- **src/components/MarketingWidget.tsx**: 캠페인 생성 및 관리를 위한 마케팅 위젯 컴포넌트
- **src/pages/Dashboard.tsx**: 진행중 캠페인과 오늘 할 일을 보여주는 대시보드 페이지
- **src/services/api.ts**: 캠페인 데이터 관리를 위한 API 호출 함수들
- **src/types/index.ts**: Campaign, Client, Creator, Outreach 등 데이터 모델 타입 정의

## 시작하기

1. 프로젝트 디렉토리로 이동:
   ```
   cd marketing-integration-platform
   ```

2. 의존성 설치:
   ```
   npm install
   ```

3. 개발 서버 실행:
   ```
   npm start
   ```

## 주요 기능 플로우

### 캠페인 생성
1. 기본 정보 입력 (제품명, 목표, 예산, 기간)
2. 키워드 및 참고링크 업로드
3. 홍보 채널 선택 (네이버/인스타/카카오 등)
4. 문구 자동 생성 (채널별 3안 제공)

### 인플루언서 매칭
1. 카테고리/팔로워/참여율 기반 필터링
2. 적합한 인플루언서 추천
3. 메일/DM 자동 발송
4. 응답 및 상태 추적

### 성과 리포트
1. 발송/응답/수락/게시 상태 모니터링
2. 기본 메트릭 수집 및 분석
3. 캠페인 성과 대시보드

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.