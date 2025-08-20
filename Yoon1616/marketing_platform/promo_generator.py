import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


@dataclass
class PromoRequest:
    product_name: str
    category: str
    usp: str
    target_audience: str
    tone: str
    keywords: List[str]
    cta: str


def _client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 필요합니다")
    return OpenAI(api_key=api_key)


def generate_blogger_writing_kit(req: PromoRequest) -> Dict[str, str]:
    """
    블로거에게 전달할 '작성 틀(템플릿)'과 발송용 이메일 제목/본문을 생성
    반환: { 'kit_markdown': str, 'email_subject': str, 'email_body': str }
    """
    system_prompt = (
        "당신은 한국어 마케팅 카피라이터이자 블로그 에디터입니다. "
        "블로거가 제품을 소개하는 글을 쉽게 작성할 수 있도록, 작성 틀과 가이드를 만드세요."
    )

    user_prompt = f"""
제품명: {req.product_name}
카테고리: {req.category}
USP: {req.usp}
타겟 독자: {req.target_audience}
브랜드 톤: {req.tone}
핵심 키워드: {', '.join(req.keywords)}
권장 CTA: {req.cta}

출력 형식은 아래 3개 블록을 구분 기호로 정확히 감싸서 제공하세요.

[EMAIL_SUBJECT]
블로거에게 전달할 이메일 제목 (한 줄)
[/EMAIL_SUBJECT]

[EMAIL_BODY]
블로거에게 전달할 이메일 본문. 아래 내용을 포함:
- 제안 목적(제품 협업/리뷰 제안)
- 제품 요약(USP 반영 1~2문장)
- 보상/마감/연락방법은 placeholder로 명시
- 아래 '작성 틀'을 첨부했다는 안내
- 정중한 마무리
[/EMAIL_BODY]

[WRITING_KIT_MD]
# 블로그 글 작성 틀(Template)
- 예상 길이: 1200~1800자
- 권장 소제목(H2/H3) 구조
- SEO 키워드(필수/보조)와 밀도 가이드
- 썸네일/본문 이미지 가이드
- 포함 권장 정보: 스펙, 사용 시나리오, 비교 포인트, 가격/프로모션, FAQ 3~5개, CTA
- 금지 표현/유의사항(광고 표기 등)

## 아웃라인 예시
- H2 도입: 문제 공감/타깃 페인포인트
- H2 해결책: 제품 소개와 USP
- H2 사용 후기/케이스: 실제 시나리오 2~3개
- H2 장단점/비교: 대안 대비 포지셔닝
- H2 마무리: CTA와 혜택 정리

## 키워드 세트
- 필수: [키워드 나열]
- 보조: [키워드 나열]
- 해시태그: 최소 10개 (카테고리+제품 혼합)

## 문장 가이드
- 톤 앤 매너: {req.tone}
- 금지: 과장/미확인 정보
- CTA 예시: "{req.cta}"

## 작성 템플릿(복사해서 사용)
제목: [독자의 문제/효과를 제목에 드러내기]

소제목1(H2): [문제 공감]
- [경험/페인포인트]

소제목2(H2): [{req.product_name} 소개]
- USP: [핵심 이점 2~3개]
- 주요 기능: [목록]

소제목3(H2): [사용 시나리오/후기]
- [사례1]
- [사례2]

소제목4(H2): [비교/장단점]
- [경쟁/대안 대비 포인트]

마무리(H2): [요약+CTA]
- 혜택/프로모션: [placeholder]
- CTA: [{req.cta}]
[/WRITING_KIT_MD]
"""

    client = _client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1100,
        temperature=0.7,
    )

    content = resp.choices[0].message.content or ""

    def _extract(block: str) -> str:
        start = content.find(f"[{block}]")
        end = content.find(f"[/{block}]")
        if start == -1 or end == -1:
            return ""
        return content[start + len(block) + 2 : end].strip()

    email_subject = _extract("EMAIL_SUBJECT")
    email_body = _extract("EMAIL_BODY")
    kit_md = _extract("WRITING_KIT_MD")

    return {
        "kit_markdown": kit_md or content,
        "email_subject": email_subject or f"[{req.product_name}] 협업 제안",
        "email_body": email_body or "안녕하세요, 협업 제안드립니다.",
    }


# 하위 호환: 기존 함수 유지 (마크다운만 반환)
def generate_promo_copy(req: PromoRequest) -> Dict[str, str]:
    out = generate_blogger_writing_kit(req)
    return {"markdown": out.get("kit_markdown", "")}

