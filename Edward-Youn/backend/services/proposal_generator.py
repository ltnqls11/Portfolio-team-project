"""
포스팅 제안 문구 생성 서비스
블로거에게 보낼 협찬 제안 메일 내용을 자동 생성
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from database.models import Campaign, Blogger


class ProposalTemplate(BaseModel):
    """포스팅 제안 템플릿"""
    subject: str
    content: str
    blogger_name: str
    blog_name: str
    company_name: str
    product_name: str


class ProposalGeneratorService:
    """포스팅 제안 문구 생성 서비스"""
    
    def __init__(self):
        self.collaboration_types = {
            "sponsored_post": "협찬 포스팅",
            "product_review": "제품 리뷰",
            "brand_mention": "브랜드 언급",
            "event_coverage": "이벤트 커버리지"
        }
        
        self.compensation_types = {
            "monetary": "금전적 보상",
            "product": "제품 제공",
            "both": "제품 + 금전적 보상"
        }
    
    async def generate_proposal(
        self,
        campaign: Campaign,
        blogger: Blogger,
        custom_message: Optional[str] = None,
        collaboration_type: str = "sponsored_post",
        compensation_type: str = "monetary",
        compensation_amount: Optional[str] = None,
        deadline: Optional[datetime] = None,
        requirements: Optional[List[str]] = None
    ) -> ProposalTemplate:
        """개별 맞춤 포스팅 제안 문구 생성"""
        
        # 기본 정보 추출
        company_name = campaign.client.name if hasattr(campaign, 'client') else "저희 회사"
        product_name = campaign.title
        blogger_name = blogger.blogger_name
        blog_name = blogger.blog_name
        category = blogger.category
        
        # 제목 생성
        subject = self._generate_subject(
            blogger_name=blogger_name,
            product_name=product_name,
            collaboration_type=collaboration_type
        )
        
        # 본문 생성
        content = self._generate_content(
            campaign=campaign,
            blogger=blogger,
            custom_message=custom_message,
            collaboration_type=collaboration_type,
            compensation_type=compensation_type,
            compensation_amount=compensation_amount,
            deadline=deadline,
            requirements=requirements
        )
        
        return ProposalTemplate(
            subject=subject,
            content=content,
            blogger_name=blogger_name,
            blog_name=blog_name,
            company_name=company_name,
            product_name=product_name
        )
    
    def _generate_subject(
        self,
        blogger_name: str,
        product_name: str,
        collaboration_type: str
    ) -> str:
        """메일 제목 생성"""
        
        collaboration_kr = self.collaboration_types.get(collaboration_type, "협업")
        
        subject_templates = [
            f"[{collaboration_kr} 제안] {blogger_name}님께 {product_name} 협업 제안드립니다",
            f"{blogger_name}님, {product_name} {collaboration_kr} 협업 문의드립니다",
            f"[협업 제안] {product_name} × {blogger_name}님 콜라보레이션 제안"
        ]
        
        # 블로거명 길이에 따라 적절한 템플릿 선택
        if len(blogger_name) > 10:
            return subject_templates[1]
        else:
            return subject_templates[0]
    
    def _generate_content(
        self,
        campaign: Campaign,
        blogger: Blogger,
        custom_message: Optional[str],
        collaboration_type: str,
        compensation_type: str,
        compensation_amount: Optional[str],
        deadline: Optional[datetime],
        requirements: Optional[List[str]]
    ) -> str:
        """메일 본문 생성"""
        
        # 기본 정보
        blogger_name = blogger.blogger_name
        blog_name = blogger.blog_name
        category = blogger.category
        post_count = blogger.post_count or "다수"
        
        company_name = campaign.client.name if hasattr(campaign, 'client') else "저희 회사"
        product_name = campaign.title
        objective = campaign.objective
        
        collaboration_kr = self.collaboration_types.get(collaboration_type, "협업")
        compensation_kr = self.compensation_types.get(compensation_type, "보상")
        
        # 본문 구성
        content_parts = []
        
        # 인사말
        content_parts.extend([
            f"안녕하세요, {blogger_name}님!",
            "",
            f"'{blog_name}' 블로그를 통해 {category} 분야의 유익하고 진정성 있는 콘텐츠를 공유해주시는 모습을 보고 연락드리게 되었습니다.",
            f"현재까지 {post_count}개의 포스팅을 통해 독자들에게 좋은 정보를 전달해주고 계시는 점이 정말 인상적이었습니다.",
            ""
        ])
        
        # 회사 및 제품 소개
        content_parts.extend([
            f"저희는 {company_name}입니다.",
            f"이번에 {product_name}에 대한 {collaboration_kr}을 제안드리고자 합니다.",
            "",
            f"📌 {objective}",
            ""
        ])
        
        # 맞춤 메시지 (있는 경우)
        if custom_message:
            content_parts.extend([
                "💬 추가 메시지:",
                custom_message,
                ""
            ])
        
        # 협업 내용
        content_parts.extend([
            "🤝 협업 내용:",
            f"• 협업 유형: {collaboration_kr}",
            f"• 보상 방식: {compensation_kr}"
        ])
        
        if compensation_amount:
            content_parts.append(f"• 보상 금액: {compensation_amount}")
        
        if deadline:
            deadline_str = deadline.strftime("%Y년 %m월 %d일")
            content_parts.append(f"• 마감일: {deadline_str}")
        
        content_parts.append("")
        
        # 요구사항 (있는 경우)
        if requirements:
            content_parts.extend([
                "📋 요구사항:",
                *[f"• {req}" for req in requirements],
                ""
            ])
        
        # 포스팅 가이드라인
        content_parts.extend([
            "📝 포스팅 가이드라인:",
            "• 자연스럽고 진정성 있는 후기 형태로 작성",
            "• 제품의 장점과 개인적인 사용 경험 포함",
            "• 독자들에게 도움이 되는 정보 중심으로 구성",
            "• 협찬 표기는 관련 법규에 따라 명시",
            ""
        ])
        
        # 블로거 맞춤 멘트
        category_specific_message = self._get_category_specific_message(category)
        if category_specific_message:
            content_parts.extend([
                f"✨ {category} 분야 전문성:",
                category_specific_message,
                ""
            ])
        
        # 마무리
        content_parts.extend([
            "협업에 관심이 있으시다면 언제든 연락 주시기 바랍니다.",
            "궁금한 점이나 추가로 논의하고 싶은 사항이 있으시면 편하게 말씀해 주세요.",
            "",
            "감사합니다.",
            "",
            "---",
            f"{company_name} 마케팅팀",
            "📧 이메일로 회신 부탁드립니다.",
            "📞 빠른 연락을 원하시면 전화 문의도 가능합니다."
        ])
        
        return "\n".join(content_parts)
    
    def _get_category_specific_message(self, category: str) -> Optional[str]:
        """카테고리별 맞춤 메시지"""
        
        category_messages = {
            "뷰티": f"{category} 분야에서의 전문적인 리뷰와 팁이 독자들에게 큰 도움이 될 것 같습니다.",
            "패션": f"{category} 트렌드에 대한 안목과 스타일링 노하우가 돋보입니다.",
            "음식": f"{category} 관련 솔직한 후기와 레시피가 많은 분들께 인기가 높을 것 같습니다.",
            "여행": f"{category} 정보와 생생한 경험담이 여행을 계획하는 분들께 큰 도움이 됩니다.",
            "육아": f"{category} 경험과 노하우가 같은 고민을 하는 부모님들께 큰 공감을 얻을 것 같습니다.",
            "건강": f"{category} 정보에 대한 신뢰성 있는 접근이 독자들에게 도움이 됩니다.",
            "IT": f"{category} 제품에 대한 전문적인 분석과 리뷰가 인상적입니다.",
            "생활": f"일상 {category} 팁과 정보가 실용적이고 유용합니다."
        }
        
        return category_messages.get(category)
    
    def get_template_variations(self, collaboration_type: str) -> List[str]:
        """협업 유형별 템플릿 변형 제공"""
        
        variations = {
            "sponsored_post": [
                "제품 체험 후 솔직한 후기 포스팅",
                "일상 속 자연스러운 제품 사용 후기",
                "제품의 특징과 장점을 중심으로 한 리뷰"
            ],
            "product_review": [
                "상세한 제품 분석 및 평가",
                "다른 제품과의 비교 리뷰",
                "장단점을 균형있게 다룬 객관적 리뷰"
            ],
            "brand_mention": [
                "관련 포스팅에서 자연스러운 브랜드 언급",
                "카테고리 관련 글에서 추천 형태로 소개",
                "일상 공유 글에서 자연스럽게 포함"
            ],
            "event_coverage": [
                "이벤트 참여 후기 및 현장 분위기 전달",
                "이벤트 하이라이트와 개인적 소감",
                "이벤트 정보와 참여 방법 안내"
            ]
        }
        
        return variations.get(collaboration_type, ["기본 협업 내용"])
    
    def validate_proposal_content(self, content: str) -> Dict[str, Any]:
        """제안 내용 유효성 검사"""
        
        validation_result = {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }
        
        # 길이 체크
        if len(content) < 200:
            validation_result["issues"].append("내용이 너무 짧습니다.")
            validation_result["is_valid"] = False
        
        if len(content) > 2000:
            validation_result["issues"].append("내용이 너무 깁니다.")
            validation_result["suggestions"].append("핵심 내용만 간결하게 정리해보세요.")
        
        # 필수 요소 체크
        required_elements = ["협업", "보상", "요구사항"]
        for element in required_elements:
            if element not in content:
                validation_result["suggestions"].append(f"'{element}' 관련 내용을 추가하면 좋겠습니다.")
        
        # 정중한 표현 체크
        polite_expressions = ["안녕하세요", "감사합니다", "부탁드립니다"]
        if not any(expr in content for expr in polite_expressions):
            validation_result["suggestions"].append("더 정중한 표현을 사용해보세요.")
        
        return validation_result