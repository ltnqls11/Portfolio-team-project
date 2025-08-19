"""
홍보 문구 생성 서비스
"""

from typing import List, Dict, Any
import json
import re
from datetime import datetime

from database.models import Campaign, Platform


class CopyGeneratorService:
    """홍보 문구 생성 서비스"""
    
    def __init__(self):
        self.channel_rules = self._load_channel_rules()
        self.forbidden_words = self._load_forbidden_words()
    
    def _load_channel_rules(self) -> Dict[Platform, Dict[str, Any]]:
        """채널별 문구 생성 규칙"""
        return {
            Platform.NAVER_BLOG: {
                "title_length": {"min": 30, "max": 40},
                "content_length": {"min": 1500, "max": 3000},
                "headings": 3,
                "keyword_frequency": 5,
                "cta_count": 1,
                "tone": "informative"
            },
            Platform.INSTAGRAM: {
                "content_length": {"min": 150, "max": 220},
                "hashtags": {"min": 8, "max": 12},
                "emojis": {"min": 1, "max": 3},
                "cta_count": 1,
                "tone": "casual"
            },
            Platform.TISTORY: {
                "title_length": {"min": 25, "max": 35},
                "content_length": {"min": 1000, "max": 2500},
                "headings": 2,
                "keyword_frequency": 4,
                "cta_count": 1,
                "tone": "friendly"
            },
            Platform.KAKAO_CHANNEL: {
                "content_length": {"min": 100, "max": 300},
                "cta_count": 1,
                "tone": "professional"
            }
        }
    
    def _load_forbidden_words(self) -> List[str]:
        """금칙어 목록"""
        return [
            "100%", "완벽한", "절대", "무조건", "최고", "최상",
            "의학적", "치료", "완치", "부작용 없음",
            "무료", "공짜", "한정", "마지막 기회"
        ]
    
    async def generate_variants(
        self, 
        campaign: Campaign, 
        channel: Platform, 
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """채널별 문구 변형 생성"""
        
        rules = self.channel_rules.get(channel, {})
        variants = []
        
        for i in range(count):
            variant = await self._generate_single_variant(
                campaign, channel, rules, variant_num=i+1
            )
            variants.append(variant)
        
        return variants
    
    async def _generate_single_variant(
        self, 
        campaign: Campaign, 
        channel: Platform, 
        rules: Dict[str, Any],
        variant_num: int
    ) -> Dict[str, Any]:
        """단일 문구 변형 생성"""
        
        # 기본 정보 추출
        keywords = campaign.keywords_list
        objective = campaign.objective
        tone = rules.get("tone", "professional")
        
        # 채널별 문구 생성
        if channel == Platform.NAVER_BLOG:
            content = self._generate_naver_blog_content(
                objective, keywords, rules, variant_num
            )
        elif channel == Platform.INSTAGRAM:
            content = self._generate_instagram_content(
                objective, keywords, rules, variant_num
            )
        elif channel == Platform.TISTORY:
            content = self._generate_tistory_content(
                objective, keywords, rules, variant_num
            )
        elif channel == Platform.KAKAO_CHANNEL:
            content = self._generate_kakao_content(
                objective, keywords, rules, variant_num
            )
        else:
            content = self._generate_default_content(objective, keywords)
        
        # 금칙어 체크 및 제거
        content = self._remove_forbidden_words(content)
        
        # 품질 점수 계산
        score = self._calculate_quality_score(content, rules)
        
        return {
            "text": content,
            "tone": tone,
            "score": score,
            "channel": channel.value
        }
    
    def _generate_naver_blog_content(
        self, 
        objective: str, 
        keywords: List[str], 
        rules: Dict[str, Any],
        variant_num: int
    ) -> str:
        """네이버 블로그용 문구 생성"""
        
        # 제목 생성
        title_templates = [
            f"{keywords[0] if keywords else '제품'} 후기 - 실제 사용해본 솔직한 경험담",
            f"요즘 핫한 {keywords[0] if keywords else '아이템'}, 정말 효과가 있을까?",
            f"{keywords[0] if keywords else '제품'} 완벽 가이드 | 구매 전 꼭 읽어보세요"
        ]
        
        title = title_templates[variant_num - 1] if variant_num <= len(title_templates) else title_templates[0]
        
        # 본문 생성
        content_parts = [
            f"안녕하세요! 오늘은 {objective}에 대해 자세히 알아보려고 해요.",
            "",
            "## 왜 이 제품을 선택했을까요?",
            f"최근 {keywords[0] if keywords else '이 분야'}에 관심이 많아지면서 여러 제품을 비교해봤는데요,",
            "실제 사용자들의 후기와 전문가 의견을 종합해본 결과 이 제품이 가장 적합하다고 판단했습니다.",
            "",
            "## 주요 특징과 장점",
            f"• {keywords[0] if keywords else '핵심 기능'}: 뛰어난 성능과 안정성",
            f"• {keywords[1] if len(keywords) > 1 else '사용 편의성'}: 직관적이고 간편한 사용법",
            f"• {keywords[2] if len(keywords) > 2 else '가성비'}: 합리적인 가격대",
            "",
            "## 실제 사용 후기",
            "처음 사용했을 때부터 확실히 다른 점을 느낄 수 있었어요.",
            "특히 기대했던 부분에서 만족스러운 결과를 얻을 수 있었습니다.",
            "",
            "## 마무리",
            f"{objective}를 고민하고 계신다면 한 번 체험해보시는 것을 추천드려요!",
            "",
            "👉 자세한 정보는 아래 링크에서 확인하세요!"
        ]
        
        return title + "\n\n" + "\n".join(content_parts)
    
    def _generate_instagram_content(
        self, 
        objective: str, 
        keywords: List[str], 
        rules: Dict[str, Any],
        variant_num: int
    ) -> str:
        """인스타그램용 문구 생성"""
        
        content_templates = [
            f"✨ {objective} ✨\n\n요즘 정말 만족하고 있는 아이템 소개해드릴게요!\n\n실제로 써보니 기대 이상이었어요 😍\n\n",
            f"🌟 {objective} 🌟\n\n이거 진짜 추천해요!\n\n사용해보고 완전 만족 중 💕\n\n",
            f"💫 {objective} 💫\n\n요즘 핫한 이유가 있더라구요!\n\n직접 체험해보니 정말 좋아요 ✨\n\n"
        ]
        
        base_content = content_templates[variant_num - 1] if variant_num <= len(content_templates) else content_templates[0]
        
        # 해시태그 생성
        hashtags = []
        for keyword in keywords[:5]:  # 최대 5개 키워드 사용
            hashtags.append(f"#{keyword.replace(' ', '')}")
        
        # 기본 해시태그 추가
        default_hashtags = ["#추천", "#후기", "#일상", "#좋아요", "#팔로우"]
        hashtags.extend(default_hashtags[:12-len(hashtags)])  # 최대 12개까지
        
        hashtag_text = " ".join(hashtags)
        
        return base_content + hashtag_text
    
    def _generate_tistory_content(
        self, 
        objective: str, 
        keywords: List[str], 
        rules: Dict[str, Any],
        variant_num: int
    ) -> str:
        """티스토리용 문구 생성"""
        
        title_templates = [
            f"{keywords[0] if keywords else '제품'} 리뷰 | 한 달 사용 후기",
            f"{keywords[0] if keywords else '제품'} 솔직 후기 및 구매 가이드",
            f"{keywords[0] if keywords else '제품'} 체험기 - 장단점 총정리"
        ]
        
        title = title_templates[variant_num - 1] if variant_num <= len(title_templates) else title_templates[0]
        
        content_parts = [
            f"안녕하세요! {objective}에 대한 솔직한 후기를 공유해드리려고 합니다.",
            "",
            "# 선택 이유",
            f"{keywords[0] if keywords else '이 제품'}을 선택한 이유는 다양한 리뷰를 비교해본 결과 가장 적합하다고 판단했기 때문입니다.",
            "",
            "# 사용 경험",
            "실제로 사용해보니 기대했던 것보다 훨씬 만족스러웠습니다.",
            f"특히 {keywords[1] if len(keywords) > 1 else '핵심 기능'} 부분에서 뛰어난 성능을 보여주었어요.",
            "",
            "관심 있으시다면 한번 체험해보시길 추천드립니다!"
        ]
        
        return title + "\n\n" + "\n".join(content_parts)
    
    def _generate_kakao_content(
        self, 
        objective: str, 
        keywords: List[str], 
        rules: Dict[str, Any],
        variant_num: int
    ) -> str:
        """카카오 채널용 문구 생성"""
        
        content_templates = [
            f"📢 {objective}\n\n✅ 검증된 품질\n✅ 합리적인 가격\n✅ 빠른 배송\n\n지금 바로 확인해보세요!",
            f"🎯 {objective}\n\n많은 분들이 선택하는 이유가 있습니다.\n\n실제 후기와 함께 자세한 정보를 확인해보세요.",
            f"⭐ {objective}\n\n신뢰할 수 있는 품질과 서비스로\n고객 만족도 1위를 달성했습니다.\n\n더 자세한 내용은 아래에서 확인하세요."
        ]
        
        return content_templates[variant_num - 1] if variant_num <= len(content_templates) else content_templates[0]
    
    def _generate_default_content(self, objective: str, keywords: List[str]) -> str:
        """기본 문구 생성"""
        return f"{objective}\n\n주요 키워드: {', '.join(keywords[:3])}\n\n자세한 정보는 문의해주세요."
    
    def _remove_forbidden_words(self, content: str) -> str:
        """금칙어 제거"""
        for word in self.forbidden_words:
            content = content.replace(word, "")
        return content
    
    def _calculate_quality_score(self, content: str, rules: Dict[str, Any]) -> float:
        """문구 품질 점수 계산"""
        score = 0.8  # 기본 점수
        
        # 길이 체크
        content_length = len(content)
        if "content_length" in rules:
            min_len = rules["content_length"]["min"]
            max_len = rules["content_length"]["max"]
            
            if min_len <= content_length <= max_len:
                score += 0.1
            elif content_length < min_len * 0.8 or content_length > max_len * 1.2:
                score -= 0.2
        
        # 금칙어 체크
        forbidden_count = sum(1 for word in self.forbidden_words if word in content)
        score -= forbidden_count * 0.1
        
        # 이모지 체크 (인스타그램)
        emoji_count = len(re.findall(r'[😀-🙏]', content))
        if "emojis" in rules:
            min_emoji = rules["emojis"]["min"]
            max_emoji = rules["emojis"]["max"]
            if min_emoji <= emoji_count <= max_emoji:
                score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def get_channel_templates(self, channel: Platform) -> Dict[str, Any]:
        """채널별 템플릿 정보 반환"""
        rules = self.channel_rules.get(channel, {})
        
        return {
            "rules": rules,
            "examples": self._get_channel_examples(channel),
            "tips": self._get_channel_tips(channel)
        }
    
    def _get_channel_examples(self, channel: Platform) -> List[str]:
        """채널별 예시 문구"""
        examples = {
            Platform.NAVER_BLOG: [
                "제품명 후기 - 실제 사용해본 솔직한 경험담",
                "요즘 핫한 아이템, 정말 효과가 있을까?",
                "완벽 가이드 | 구매 전 꼭 읽어보세요"
            ],
            Platform.INSTAGRAM: [
                "✨ 요즘 정말 만족하고 있는 아이템! #추천 #후기",
                "🌟 이거 진짜 추천해요! 완전 만족 중 💕",
                "💫 요즘 핫한 이유가 있더라구요! ✨"
            ],
            Platform.TISTORY: [
                "제품 리뷰 | 한 달 사용 후기",
                "솔직 후기 및 구매 가이드",
                "체험기 - 장단점 총정리"
            ],
            Platform.KAKAO_CHANNEL: [
                "📢 검증된 품질, 합리적인 가격!",
                "🎯 많은 분들이 선택하는 이유가 있습니다.",
                "⭐ 고객 만족도 1위 달성!"
            ]
        }
        
        return examples.get(channel, ["기본 예시 문구"])
    
    def _get_channel_tips(self, channel: Platform) -> List[str]:
        """채널별 작성 팁"""
        tips = {
            Platform.NAVER_BLOG: [
                "제목은 30-40자로 작성하세요",
                "소제목(H2)을 3개 정도 사용하세요",
                "키워드를 5회 이내로 자연스럽게 포함하세요",
                "CTA(행동 유도)를 1개 포함하세요"
            ],
            Platform.INSTAGRAM: [
                "150-220자 내외로 작성하세요",
                "해시태그 8-12개를 사용하세요",
                "이모지 1-3개를 적절히 활용하세요",
                "스토리텔링을 활용하세요"
            ],
            Platform.TISTORY: [
                "제목은 25-35자로 작성하세요",
                "소제목을 2개 정도 사용하세요",
                "개인적인 경험을 포함하세요",
                "독자와의 소통을 유도하세요"
            ],
            Platform.KAKAO_CHANNEL: [
                "100-300자 내외로 간결하게 작성하세요",
                "핵심 메시지를 명확히 전달하세요",
                "전문적인 톤을 유지하세요",
                "명확한 행동 유도를 포함하세요"
            ]
        }
        
        return tips.get(channel, ["기본 작성 팁"])