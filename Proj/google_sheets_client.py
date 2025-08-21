import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import GOOGLE_SHEETS_SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class GoogleSheetsClient:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Google Sheets API 인증"""
        creds = None
        
        # 토큰 파일이 있으면 기존 인증 정보 로드
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SHEETS_SCOPES)
        
        # 유효한 인증 정보가 없으면 새로 인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"{CREDENTIALS_FILE} 파일이 없습니다. "
                        "Google Cloud Console에서 인증 파일을 다운로드하세요."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, GOOGLE_SHEETS_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # 인증 정보 저장
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def initialize_sheet_headers(self, sheet_id, sheet_name):
        """
        요구사항: 결과를 저장할 시트의 헤더를 ['블로그명', '포스트URL', '블로그URL', '이메일']로 초기화한다.
        """
        headers = ['블로그명', '포스트URL', '블로그URL', '이메일']
        
        try:
            # 기존 데이터 확인
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f'{sheet_name}!A1:D1'
            ).execute()
            
            values = result.get('values', [])
            
            # 헤더가 없거나 다르면 새로 설정
            if not values or values[0] != headers:
                self.service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=f'{sheet_name}!A1:D1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                print(f"시트 헤더가 초기화되었습니다: {headers}")
            
        except HttpError as error:
            print(f"시트 헤더 초기화 중 오류 발생: {error}")
            raise
    
    def append_row(self, sheet_id, sheet_name, data):
        """새로운 행 추가"""
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f'{sheet_name}!A:D',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [data]}
            ).execute()
            print(f"데이터 추가됨: {data}")
            
        except HttpError as error:
            print(f"데이터 추가 중 오류 발생: {error}")
            raise
    
    def read_all_data(self, sheet_id, sheet_name):
        """시트의 모든 데이터 읽기"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f'{sheet_name}!A:D'
            ).execute()
            
            values = result.get('values', [])
            print(f"총 {len(values)}행의 데이터를 읽었습니다.")
            return values
            
        except HttpError as error:
            print(f"데이터 읽기 중 오류 발생: {error}")
            raise
    
    def read_range(self, sheet_id, sheet_name, range_notation):
        """특정 범위의 데이터 읽기"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f'{sheet_name}!{range_notation}'
            ).execute()
            
            values = result.get('values', [])
            print(f"범위 {range_notation}에서 {len(values)}행의 데이터를 읽었습니다.")
            return values
            
        except HttpError as error:
            print(f"범위 데이터 읽기 중 오류 발생: {error}")
            raise
    
    def get_blogger_data(self, sheet_id, sheet_name):
        """블로거 데이터를 딕셔너리 형태로 반환 (n8n 워크플로우용)"""
        try:
            data = self.read_all_data(sheet_id, sheet_name)
            
            if not data:
                return []
            
            # 헤더 제외하고 데이터만 처리
            headers = data[0] if data else ['블로그명', '포스트URL', '블로그URL', '이메일']
            blogger_list = []
            
            for row in data[1:]:  # 헤더 제외
                # 행의 길이가 부족한 경우 빈 문자열로 채움
                while len(row) < len(headers):
                    row.append('')
                
                blogger_info = {
                    'blog_name': row[0] if len(row) > 0 else '',
                    'post_url': row[1] if len(row) > 1 else '',
                    'blog_url': row[2] if len(row) > 2 else '',
                    'email': row[3] if len(row) > 3 else ''
                }
                
                # 이메일이 있는 블로거만 포함
                if blogger_info['email'].strip():
                    blogger_list.append(blogger_info)
            
            print(f"이메일이 있는 블로거 {len(blogger_list)}명을 찾았습니다.")
            return blogger_list
            
        except HttpError as error:
            print(f"블로거 데이터 읽기 중 오류 발생: {error}")
            raise