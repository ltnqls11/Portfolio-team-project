"""
이메일 발송 서비스
포스팅 제안 메일을 블로거에게 발송하는 서비스
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """이메일 발송 서비스"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "마케팅 연계 플랫폼")
    
    async def send_proposal_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        blogger_name: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """포스팅 제안 메일 발송"""
        
        try:
            # SMTP 설정 확인
            if not self.smtp_user or not self.smtp_password:
                logger.error("SMTP 설정이 완료되지 않았습니다.")
                return False
            
            # 메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 형태로 본문 구성
            html_content = self._format_html_content(content, blogger_name)
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 첨부파일 추가 (있는 경우)
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._add_attachment(msg, file_path)
            
            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"메일 발송 성공: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"메일 발송 실패 ({to_email}): {str(e)}")
            return False
    
    def _format_html_content(self, content: str, blogger_name: str) -> str:
        """텍스트 내용을 HTML 형태로 포맷팅"""
        
        # 줄바꿈을 <br>로 변환
        html_content = content.replace('\n', '<br>')
        
        # 이모지와 특수 문자 처리
        html_content = html_content.replace('📌', '📌')
        html_content = html_content.replace('🤝', '🤝')
        html_content = html_content.replace('💬', '💬')
        html_content = html_content.replace('📋', '📋')
        html_content = html_content.replace('📝', '📝')
        html_content = html_content.replace('✨', '✨')
        html_content = html_content.replace('📧', '📧')
        html_content = html_content.replace('📞', '📞')
        
        # HTML 템플릿 적용
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>포스팅 제안</title>
            <style>
                body {{
                    font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .email-container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #4CAF50;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #4CAF50;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    font-size: 14px;
                    line-height: 1.8;
                }}
                .highlight {{
                    background-color: #f0f8ff;
                    padding: 15px;
                    border-left: 4px solid #4CAF50;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }}
                .button {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🤝 협업 제안</h1>
                    <p>온라인 마케팅 연계 플랫폼</p>
                </div>
                
                <div class="content">
                    {html_content}
                </div>
                
                <div class="footer">
                    <p>이 메일은 온라인 마케팅 연계 플랫폼을 통해 발송되었습니다.</p>
                    <p>협업에 관심이 있으시면 이 메일에 직접 회신해 주세요.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """첨부파일 추가"""
        
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            filename = os.path.basename(file_path)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"첨부파일 추가 실패 ({file_path}): {str(e)}")
    
    async def send_bulk_emails(
        self,
        email_list: List[dict],
        subject_template: str,
        content_template: str
    ) -> dict:
        """대량 메일 발송"""
        
        results = {
            "total": len(email_list),
            "sent": 0,
            "failed": 0,
            "failed_emails": []
        }
        
        for email_data in email_list:
            try:
                # 템플릿에 개별 데이터 적용
                personalized_subject = subject_template.format(**email_data)
                personalized_content = content_template.format(**email_data)
                
                success = await self.send_proposal_email(
                    to_email=email_data['email'],
                    subject=personalized_subject,
                    content=personalized_content,
                    blogger_name=email_data.get('blogger_name', '')
                )
                
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
                    results["failed_emails"].append(email_data['email'])
                    
            except Exception as e:
                logger.error(f"대량 메일 발송 중 오류: {str(e)}")
                results["failed"] += 1
                results["failed_emails"].append(email_data.get('email', 'unknown'))
        
        return results
    
    def validate_email_settings(self) -> dict:
        """이메일 설정 유효성 검사"""
        
        validation = {
            "is_valid": True,
            "issues": []
        }
        
        if not self.smtp_user:
            validation["is_valid"] = False
            validation["issues"].append("SMTP_USER가 설정되지 않았습니다.")
        
        if not self.smtp_password:
            validation["is_valid"] = False
            validation["issues"].append("SMTP_PASSWORD가 설정되지 않았습니다.")
        
        if not self.smtp_host:
            validation["is_valid"] = False
            validation["issues"].append("SMTP_HOST가 설정되지 않았습니다.")
        
        return validation
    
    async def test_email_connection(self) -> bool:
        """이메일 서버 연결 테스트"""
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            
            logger.info("이메일 서버 연결 테스트 성공")
            return True
            
        except Exception as e:
            logger.error(f"이메일 서버 연결 테스트 실패: {str(e)}")
            return False
    
    async def send_test_email(self, to_email: str) -> bool:
        """테스트 메일 발송"""
        
        subject = "[테스트] 마케팅 연계 플랫폼 메일 발송 테스트"
        content = """
        안녕하세요!
        
        이 메일은 마케팅 연계 플랫폼의 메일 발송 기능 테스트입니다.
        
        메일이 정상적으로 수신되었다면 시스템이 올바르게 설정된 것입니다.
        
        감사합니다.
        
        ---
        마케팅 연계 플랫폼 팀
        """
        
        return await self.send_proposal_email(
            to_email=to_email,
            subject=subject,
            content=content,
            blogger_name="테스트 사용자"
        )