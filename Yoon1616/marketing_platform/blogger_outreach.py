import os
import requests
from typing import List
from promo_generator import PromoRequest, generate_blogger_writing_kit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# ==============================
# 설정
# ==============================
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")  # n8n Webhook
CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")

# ==============================
# Selenium 댓글 작성
# ==============================
def post_comment(blog_url: str, comment: str):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options)
    try:
        driver.get(blog_url)
        time.sleep(3)  # 로딩 대기

        # 댓글 textarea 선택 (블로그 구조에 맞게 수정 필요)
        textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
        textarea.send_keys(comment)

        # 댓글 제출 버튼 클릭
        submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_btn.click()
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] 댓글 작성 실패: {e}")
    finally:
        driver.quit()

# ==============================
# n8n Webhook 전송
# ==============================
def send_to_n8n(payload: dict):
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] n8n Webhook 전송 실패: {e}")

# ==============================
# 블로거 처리
# ==============================
def process_bloggers(bloggers: List[dict], promo: PromoRequest):
    for blogger in bloggers:
        kit = generate_blogger_writing_kit(promo)
        email = blogger.get("email")
        blog_url = blogger.get("blog_url")
        blogger_name = blogger.get("name", "블로거님")

        if email:
            # 이메일 있는 블로거 → Webhook 전송
            payload = {
                "to": email,
                "subject": kit["email_subject"],
                "message": kit["email_body"],
                "meta": {
                    "blogger_name": blogger_name,
                    "blog_url": blog_url
                }
            }
            send_to_n8n(payload)
            print(f"[EMAIL] {email} 발송 완료")
        else:
            # 이메일 없는 블로거 → AI로 댓글 메시지 생성 후 Selenium 댓글 작성
            comment_text = f"안녕하세요 {blogger_name}! {promo.product_name} 관련 문의용 링크를 남깁니다: [폼/이메일]"
            post_comment(blog_url, comment_text)
            print(f"[COMMENT] {blog_url} 댓글 작성 완료")

# ==============================
# 예시 실행
# ==============================
if __name__ == "__main__":
    promo = PromoRequest(
        product_name="스마트공기청정기 A100",
        category="가전제품",
        usp="AI 기반 자동 공기질 최적화",
        target_audience="알레르기 민감 가정",
        tone="친근하고 신뢰감 있는 톤",
        keywords=["공기청정기","미세먼지","AI공기관리"],
        cta="지금 바로 체험해보세요!"
    )

    # 예시 블로거 목록
    bloggers = [
        {"name": "블로거1", "email": "blogger1@example.com", "blog_url": "https://m.blog.naver.com/blogger1/123"},
        {"name": "블로거2", "email": None, "blog_url": "https://m.blog.naver.com/blogger2/456"}
    ]

    process_bloggers(bloggers, promo)
