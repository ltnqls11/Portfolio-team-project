import requests
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

# -------------------------------
# 1️⃣ 데이터 클래스 정의
# -------------------------------
@dataclass
class Product:
    product_name: str
    category: str
    usp: str
    target_audience: str
    tone: str
    keywords: List[str]
    cta: str
    images: List[str]  # 로컬 이미지 경로 배열

# -------------------------------
# 2️⃣ 블로그 작성 함수
# -------------------------------
def generate_blogger_writing_kit(product: Product) -> dict:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    system_prompt = (
        "당신은 한국어 마케팅 카피라이터이자 블로그 에디터입니다. "
        "블로거가 제품을 소개하는 글을 쉽게 작성할 수 있도록, 작성 틀과 가이드를 만드세요."
    )
    
    user_prompt = f"""
제품명: {product.product_name}
카테고리: {product.category}
USP: {product.usp}
타겟 독자: {product.target_audience}
브랜드 톤: {product.tone}
핵심 키워드: {', '.join(product.keywords)}
권장 CTA: {product.cta}

출력: 이메일 제목, 이메일 본문, 블로그 작성 틀
"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    content = resp.choices[0].message.content or ""
    return {"blog_content": content}

# -------------------------------
# 3️⃣ Instagram 게시물 JSON 생성
# -------------------------------
def generate_instagram_payload(product: Product) -> dict:
    return {
        "product_name": product.product_name,
        "category": product.category,
        "usp": product.usp,
        "target_audience": product.target_audience,
        "tone": product.tone,
        "keywords": product.keywords,
        "cta": product.cta,
        "images": product.images
    }

# -------------------------------
# 4️⃣ n8n Webhook 전송 (멀티 제품)
# -------------------------------
def send_multiple_to_n8n(products: List[Product]):
    WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")  # n8n Webhook URL
    
    for product in products:
        insta_payload = generate_instagram_payload(product)
        response = requests.post(WEBHOOK_URL, json=insta_payload)
        
        if response.status_code == 200:
            print(f"{product.product_name} → n8n 요청 성공!")
        else:
            print(f"{product.product_name} → 오류 발생: {response.status_code}")
            print(response.text)

# -------------------------------
# 5️⃣ 사용 예제
# -------------------------------
if __name__ == "__main__":
    products = [
        Product(
            product_name="스마트공기청정기 A100",
            category="가전제품",
            usp="AI 기반 자동 공기질 최적화",
            target_audience="알레르기 민감 가정",
            tone="친근하고 신뢰감 있는 톤",
            keywords=["공기청정기","미세먼지","AI공기관리"],
            cta="지금 바로 체험해보세요!",
            images=[
                "/Users/jw/Projects/images/product1.jpg",
                "/Users/jw/Projects/images/product2.jpg"
            ]
        ),
        Product(
            product_name="무선청소기 V200",
            category="가전제품",
            usp="강력 흡입 + 긴 배터리",
            target_audience="바쁜 직장인 가정",
            tone="활기차고 신뢰감 있는 톤",
            keywords=["무선청소기","강력흡입","편리한청소"],
            cta="지금 바로 구매하세요!",
            images=[
                "/Users/jw/Projects/images/v200_1.jpg",
                "/Users/jw/Projects/images/v200_2.jpg",
                "/Users/jw/Projects/images/v200_3.jpg"
            ]
        )
    ]
    
    # 블로그 작성 + n8n 전송
    for product in products:
        blog_output = generate_blogger_writing_kit(product)
        print(f"=== {product.product_name} 블로그 작성 결과 ===")
        print(blog_output["blog_content"])
    
    # Instagram 다중 제품 Webhook 전송
    send_multiple_to_n8n(products)
