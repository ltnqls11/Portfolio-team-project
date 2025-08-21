#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gmail API를 사용한 이메일 자동 발송 클라이언트
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import GMAIL_CREDENTIALS_FILE


class GmailClient:
    def __init__(self):
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/gmail.send']
        self.authenticate()
    
    def authenticate(self):
        """Gmail API 인증"""
        creds = None
        token_file = 'gmail_token.json'
        
        # 기존 토큰 파일이 있으면 로드
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, self.scopes)
        
        # 유효한 인증 정보가 없으면 새로 인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"{GMAIL_CREDENTIALS_FILE} 파일이 없습니다. "
                        "Google Cloud Console에서 Gmail API 인증 파일을 다운로드하세요."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS_FILE, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # 토큰 저장
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Gmail API 인증 완료")
    
    def create_message(self, to_email, subject, body, from_email='me'):
        """이메일 메시지 생성"""
        try:
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            message['from'] = from_email
            
            # HTML 형식으로 본문 추가
            msg_body = MIMEText(body, 'html', 'utf-8')
            message.attach(msg_body)
            
            # 메시지를 base64로 인코딩
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            return {'raw': raw_message}
            
        except Exception as e:
            print(f"이메일 메시지 생성 중 오류: {e}")
            return None
    
    def send_email(self, to_email, subject, body):
        """이메일 발송"""
        try:
            message = self.create_message(to_email, subject, body)
            if not message:
                return False
            
            result = self.service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            print(f"✓ 이메일 발송 성공: {to_email} (메시지 ID: {result['id']})")
            return True
            
        except HttpError as error:
            print(f"✗ 이메일 발송 실패 ({to_email}): {error}")
            return False
        except Exception as e:
            print(f"✗ 이메일 발송 중 예상치 못한 오류 ({to_email}): {e}")
            return False
    
    def send_bulk_emails(self, blogger_list, product_name, sender_name="마케팅팀"):
        """블로거들에게 대량 이메일 발송"""
        print(f"\n📧 {len(blogger_list)}명의 블로거에게 이메일 발송 시작...")
        
        success_count = 0
        failed_count = 0
        
        for i, blogger in enumerate(blogger_list, 1):
            try:
                blog_name = blogger.get('blog_name', '블로거')
                email = blogger.get('email', '')
                blog_url = blogger.get('blog_url', '')
                
                if not email:
                    print(f"[{i}/{len(blogger_list)}] {blog_name}: 이메일 주소 없음, 건너뜀")
                    failed_count += 1
                    continue
                
                # 이메일 제목 생성
                subject = f"{blog_name} 블로거님, 특별한 마케팅 제휴를 제안합니다."
                
                # 이메일 본문 생성 (HTML 형식)
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2c3e50;">안녕하세요, {blog_name}님!</h2>
                        
                        <p>저희는 이번에 새로 출시한 <strong style="color: #e74c3c;">'{product_name}'</strong> 제품의 홍보를 함께할 파트너를 찾고 있습니다.</p>
                        
                        <p>블로거님의 <a href="{blog_url}" style="color: #3498db; text-decoration: none;">{blog_name}</a>에서 보여주시는 전문성 있는 리뷰는 저희 제품에 큰 도움이 될 것입니다.</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h3 style="color: #2c3e50; margin-top: 0;">제휴 혜택</h3>
                            <ul>
                                <li>무료 제품 체험 기회</li>
                                <li>리뷰 작성 시 소정의 협찬비 지급</li>
                                <li>장기 파트너십 기회</li>
                            </ul>
                        </div>
                        
                        <p>관심이 있으시다면 이 이메일로 회신 부탁드립니다.</p>
                        
                        <p style="margin-top: 30px;">
                            감사합니다.<br>
                            <strong>{sender_name}</strong>
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="font-size: 12px; color: #666;">
                            이 이메일은 블로그 마케팅 제휴 제안을 위해 발송되었습니다.<br>
                            더 이상 이메일을 받고 싶지 않으시면 회신으로 알려주세요.
                        </p>
                    </div>
                </body>
                </html>
                """
                
                print(f"[{i}/{len(blogger_list)}] {blog_name} ({email})에게 이메일 발송 중...")
                
                if self.send_email(email, subject, body):
                    success_count += 1
                else:
                    failed_count += 1
                
                # API 호출 제한을 위한 잠시 대기
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"[{i}/{len(blogger_list)}] {blogger.get('blog_name', '알 수 없음')} 처리 중 오류: {e}")
                failed_count += 1
                continue
        
        print(f"\n📊 이메일 발송 완료!")
        print(f"✓ 성공: {success_count}건")
        print(f"✗ 실패: {failed_count}건")
        print(f"📈 성공률: {(success_count/(success_count+failed_count)*100):.1f}%" if (success_count+failed_count) > 0 else "0%")
        
        return success_count, failed_count