# Google Sheets 연결 설정 가이드

## 🚨 문제 상황

`app.py`에서 Google Sheets 연결 시 다음과 같은 오류가 발생합니다:
```
Google Sheets 연결 실패: ('invalid_grant: Invalid JWT Signature.', {'error': 'invalid_grant', 'error_description': 'Invalid JWT Signature.'})
```

## 🔍 오류 원인 분석

**"Invalid JWT Signature"** 오류는 다음 중 하나의 문제로 발생합니다:

1. **서비스 계정 키 파일 손상**: `credentials.json` 파일이 잘못되었거나 손상됨
2. **만료된 키**: 서비스 계정 키가 만료됨
3. **잘못된 권한**: 스프레드시트에 대한 접근 권한이 없음
4. **잘못된 스코프**: API 권한 범위가 부족함

## 🔧 해결 방법

### 1단계: Google Cloud Console에서 새 서비스 계정 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. **IAM 및 관리** → **서비스 계정** 클릭
4. **서비스 계정 만들기** 클릭
5. **서비스 계정 이름**: `vdt-health-manager` 입력
6. **서비스 계정 ID**: 자동 생성됨
7. **설명**: `VDT 증후군 관리 시스템용 서비스 계정` 입력
8. **만들고 계속하기** 클릭

### 2단계: 권한 설정

1. **역할 선택**:
   - **기본** → **편집자** 선택
   - 또는 **사용자 정의** → 필요한 권한만 선택

2. **필요한 권한**:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive`

3. **완료** 클릭

### 3단계: 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭 클릭
3. **키 추가** → **새 키 만들기** 클릭
4. **JSON** 선택
5. **만들기** 클릭
6. `credentials.json` 파일이 자동으로 다운로드됨

### 4단계: 파일 배치

1. 다운로드된 `credentials.json` 파일을 프로젝트 루트 디렉토리에 복사
2. 파일 경로 확인: `./credentials.json`

### 5단계: Google Sheets API 활성화

1. **API 및 서비스** → **라이브러리** 클릭
2. **Google Sheets API** 검색
3. **Google Sheets API** 클릭
4. **사용** 클릭

### 6단계: 스프레드시트 공유

1. Google Sheets에서 새 스프레드시트 생성
2. **공유** 버튼 클릭
3. **사용자 및 그룹 추가** 클릭
4. **이메일 주소 또는 이름**: `vdt-health-manager@[PROJECT_ID].iam.gserviceaccount.com` 입력
5. **역할**: **편집자** 선택
6. **알림 보내기** 체크 해제
7. **완료** 클릭

### 7단계: 환경변수 설정

`.env` 파일에 다음 내용 추가:

```env
# Google Sheets 설정
SPREADSHEET_ID=your_spreadsheet_id_here
```

**스프레드시트 ID 찾는 방법**:
- Google Sheets URL에서 찾기
- `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
- `[SPREADSHEET_ID]` 부분을 복사

## 🚀 자동 연결 기능

수정된 `app.py`는 다음과 같은 자동 연결 기능을 제공합니다:

### 자동 연결 시도
- 앱 시작 시 자동으로 Google Sheets 연결 시도
- 필요한 조건이 모두 충족되면 자동 연결

### 연결 테스트
- **🧪 연결 테스트** 버튼으로 연결 상태 확인
- 상세한 오류 메시지 제공

### 수동 연결
- **🔌 수동 연결** 버튼으로 강제 연결 시도
- 연결 실패 시 재시도 가능

## 📊 연결 상태 모니터링

### 홈 화면
- Google Sheets 연결 상태 실시간 표시
- 자동 연결 성공/실패 알림

### 사이드바
- 연결 상태 요약 표시
- 환경변수 상태 확인

### 디버깅 정보
- 상세한 연결 오류 정보
- 환경변수 설정 상태

## 🔍 문제 해결 체크리스트

### 기본 확인사항
- [ ] `credentials.json` 파일이 프로젝트 루트에 있음
- [ ] `SPREADSHEET_ID` 환경변수가 설정됨
- [ ] Google Sheets API가 활성화됨
- [ ] 서비스 계정이 스프레드시트에 공유됨

### 권한 확인사항
- [ ] 서비스 계정에 **편집자** 권한 부여
- [ ] 스프레드시트가 공개되지 않음 (보안상 권장)
- [ ] Google Cloud 프로젝트가 활성화됨

### 라이브러리 확인사항
- [ ] `gspread` 라이브러리가 설치됨
- [ ] `google-auth` 라이브러리가 설치됨

## 💡 추가 팁

### 보안 강화
- 서비스 계정 키는 절대 공개 저장소에 업로드하지 마세요
- `.gitignore`에 `credentials.json` 추가
- 정기적으로 서비스 계정 키 갱신

### 성능 최적화
- 연결은 앱 시작 시 한 번만 수행
- 불필요한 API 호출 최소화
- 에러 발생 시 적절한 재시도 로직 구현

### 모니터링
- 연결 상태를 실시간으로 확인
- 오류 발생 시 즉시 알림
- 정기적인 연결 상태 점검

---

**💡 핵심**: 올바른 서비스 계정 설정과 권한 부여가 가장 중요합니다!
