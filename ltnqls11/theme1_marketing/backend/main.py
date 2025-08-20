from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import socket
import sys

app = FastAPI(title="마케팅 플랫폼 API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 모델
class Campaign(BaseModel):
    id: Optional[str] = None
    clientId: str
    title: str
    objective: str
    budget: float
    startAt: datetime
    endAt: datetime
    channels: List[str]
    keywords: List[str]
    referenceUrls: List[str]
    status: str = "draft"
    targetCategory: str = "beauty"
    crawlingKeywords: List[str] = []

class PowerBlogger(BaseModel):
    id: Optional[str] = None
    blogUrl: str
    blogTitle: str
    bloggerName: str
    category: str
    subscriberCount: int
    avgViews: int
    avgLikes: int
    avgComments: int
    engagementRate: float
    contactEmail: Optional[str] = None
    contactPhone: Optional[str] = None
    collaborationRate: Optional[int] = None
    lastActive: datetime
    isVerified: bool = False
    tags: List[str] = []

class ReviewData(BaseModel):
    id: Optional[str] = None
    productName: str
    blogUrl: str
    bloggerName: str
    title: str
    content: str
    rating: float
    pros: List[str] = []
    cons: List[str] = []
    images: List[str] = []
    publishedAt: datetime
    category: str
    sentiment: str = "neutral"
    keywords: List[str] = []

class GeneratedContent(BaseModel):
    id: Optional[str] = None
    campaignId: str
    contentType: str
    title: str
    content: str
    hashtags: List[str] = []
    targetAudience: str
    tone: str
    basedOnReviews: List[str] = []
    generatedAt: datetime
    status: str = "draft"

# 메모리 저장소 (실제로는 데이터베이스 사용)
campaigns_db = []
power_bloggers_db = [
    # 네이버 블로그
    {
        "id": str(uuid.uuid4()),
        "blogUrl": "https://blog.naver.com/beauty_queen",
        "blogTitle": "뷰티퀸의 화장품 리뷰",
        "bloggerName": "뷰티퀸",
        "platform": "naver_blog",
        "category": "beauty",
        "subscriberCount": 45000,
        "avgViews": 8500,
        "avgLikes": 320,
        "avgComments": 85,
        "engagementRate": 0.048,
        "contactEmail": "beautyqueen@naver.com",
        "collaborationRate": 300000,
        "lastActive": datetime.now(),
        "isVerified": True,
        "tags": ["화장품", "스킨케어", "메이크업", "뷰티팁"]
    },
    # 티스토리
    {
        "id": str(uuid.uuid4()),
        "blogUrl": "https://foodlover.tistory.com",
        "blogTitle": "맛집탐방 일기",
        "bloggerName": "푸드러버",
        "platform": "tistory",
        "category": "food",
        "subscriberCount": 32000,
        "avgViews": 6200,
        "avgLikes": 280,
        "avgComments": 65,
        "engagementRate": 0.055,
        "contactEmail": "foodlover@gmail.com",
        "collaborationRate": 250000,
        "lastActive": datetime.now(),
        "isVerified": True,
        "tags": ["맛집", "요리", "레시피", "카페"]
    },
    # 블로그스팟
    {
        "id": str(uuid.uuid4()),
        "blogUrl": "https://lifestylemom.blogspot.com",
        "blogTitle": "워킹맘의 라이프스타일",
        "bloggerName": "라이프맘",
        "platform": "blogspot",
        "category": "lifestyle",
        "subscriberCount": 28000,
        "avgViews": 5800,
        "avgLikes": 240,
        "avgComments": 55,
        "engagementRate": 0.052,
        "contactEmail": "lifemom@gmail.com",
        "collaborationRate": 200000,
        "lastActive": datetime.now(),
        "isVerified": False,
        "tags": ["육아", "살림", "인테리어", "패션"]
    },
    # 카카오채널
    {
        "id": str(uuid.uuid4()),
        "blogUrl": "https://pf.kakao.com/_beauty_tips",
        "blogTitle": "뷰티팁 채널",
        "bloggerName": "뷰티팁",
        "platform": "kakao_channel",
        "category": "beauty",
        "subscriberCount": 15000,
        "avgViews": 3200,
        "avgLikes": 180,
        "avgComments": 25,
        "engagementRate": 0.064,
        "contactEmail": "beautytips@kakao.com",
        "collaborationRate": 150000,
        "lastActive": datetime.now(),
        "isVerified": True,
        "tags": ["뷰티", "팁", "화장품", "리뷰"]
    },
    # 인스타그램
    {
        "id": str(uuid.uuid4()),
        "blogUrl": "https://instagram.com/fashion_daily",
        "blogTitle": "데일리 패션",
        "bloggerName": "패션데일리",
        "platform": "instagram",
        "category": "fashion",
        "subscriberCount": 52000,
        "avgViews": 12000,
        "avgLikes": 850,
        "avgComments": 120,
        "engagementRate": 0.081,
        "contactEmail": "fashiondaily@gmail.com",
        "collaborationRate": 400000,
        "lastActive": datetime.now(),
        "isVerified": True,
        "tags": ["패션", "OOTD", "스타일링", "트렌드"]
    }
]
reviews_db = []
generated_content_db = []
blogger_outreach_db = []

@app.get("/")
async def root():
    return {"message": "마케팅 플랫폼 API 서버가 실행 중입니다"}

# 캠페인 관련 API
@app.get("/api/campaigns")
async def get_campaigns():
    return campaigns_db

@app.post("/api/campaigns")
async def create_campaign(campaign: Campaign):
    campaign.id = str(uuid.uuid4())
    campaign_dict = campaign.model_dump()
    campaigns_db.append(campaign_dict)
    return campaign_dict

@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaign = next((c for c in campaigns_db if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다")
    return campaign

@app.put("/api/campaigns/{campaign_id}")
async def update_campaign(campaign_id: str, campaign_data: dict):
    for i, campaign in enumerate(campaigns_db):
        if campaign["id"] == campaign_id:
            campaigns_db[i].update(campaign_data)
            return campaigns_db[i]
    raise HTTPException(status_code=404, detail="캠페인을 찾을 수 없습니다")

# 지원 플랫폼 목록
SUPPORTED_PLATFORMS = [
    "naver_blog",      # 네이버 블로그
    "blogspot",        # 블로그스팟
    "tistory",         # 티스토리
    "kakao_channel",   # 카카오채널
    "instagram"        # 인스타그램
]

# 문구 생성 관련 API
@app.post("/api/copy/generate")
async def generate_copy(request: dict):
    # 간단한 문구 생성 시뮬레이션
    channel = request.get("channel", "naver_blog")
    product = request.get("productDescription", "제품")
    
    if channel in ["naver_blog", "blogspot", "tistory"]:
        # 블로그 플랫폼용 긴 형태 콘텐츠
        variants = [
            {
                "title": f"{product} 완벽 가이드 - 실제 사용 후기",
                "content": f"안녕하세요! 오늘은 {product}에 대해 자세히 알아보겠습니다. 실제로 사용해본 경험을 바탕으로 솔직한 후기를 공유드리려고 해요...",
                "hashtags": ["#리뷰", "#추천", "#후기"],
                "cta": "지금 바로 확인해보세요!",
                "length": 1850,
                "score": 0.92
            },
            {
                "title": f"{product} 사용법과 꿀팁 대공개",
                "content": f"{product}를 더 효과적으로 사용하는 방법을 알려드릴게요. 많은 분들이 놓치고 있는 숨겨진 기능들도 함께 소개합니다...",
                "hashtags": ["#꿀팁", "#사용법", "#가이드"],
                "cta": "더 많은 정보를 확인하세요!",
                "length": 1650,
                "score": 0.88
            }
        ]
    elif channel == "kakao_channel":
        # 카카오채널용 중간 형태 콘텐츠
        variants = [
            {
                "title": f"{product} 추천해요! 💕",
                "content": f"{product} 사용해보니 정말 만족스러워요! 특히 이런 분들께 추천드려요 ✨\n\n✅ 장점\n- 사용감이 좋아요\n- 효과가 빨라요\n- 가성비 좋아요\n\n지금 특가로 만나보세요! 👇",
                "hashtags": ["#추천", "#좋아요", "#특가"],
                "cta": "자세히 보기",
                "length": 180,
                "score": 0.89
            }
        ]
    elif channel == "instagram":
        # 인스타그램용 짧은 형태 콘텐츠
        variants = [
            {
                "content": f"{product} 정말 좋아요! 👍 사용해보니 기대 이상이네요 ✨",
                "hashtags": ["#추천", "#좋아요", "#만족"],
                "cta": "스토리에서 더 보기 👆",
                "length": 45,
                "score": 0.85
            },
            {
                "content": f"요즘 핫한 {product} 드디어 써봤어요! 💕 진짜 대박이에요 🔥",
                "hashtags": ["#핫템", "#대박", "#추천템"],
                "cta": "링크는 프로필에 👆",
                "length": 42,
                "score": 0.87
            }
        ]
    else:
        # 기본 콘텐츠
        variants = [
            {
                "content": f"{product} 추천드려요!",
                "hashtags": ["#추천"],
                "cta": "자세히 보기",
                "length": 20,
                "score": 0.75
            }
        ]
    
    return {"variants": variants}

@app.get("/api/campaigns/{campaign_id}/copy-variants")
async def get_copy_variants(campaign_id: str):
    variants = [v for v in copy_variants_db if v["campaignId"] == campaign_id]
    return variants

@app.patch("/api/copy-variants/{variant_id}/approve")
async def approve_copy_variant(variant_id: str):
    for variant in copy_variants_db:
        if variant["id"] == variant_id:
            variant["approved"] = True
            return variant
    raise HTTPException(status_code=404, detail="문구를 찾을 수 없습니다")

# 플랫폼 목록 조회 API
@app.get("/api/platforms")
async def get_platforms():
    return {
        "platforms": [
            {"id": "naver_blog", "name": "네이버 블로그", "type": "blog"},
            {"id": "blogspot", "name": "블로그스팟", "type": "blog"},
            {"id": "tistory", "name": "티스토리", "type": "blog"},
            {"id": "kakao_channel", "name": "카카오채널", "type": "channel"},
            {"id": "instagram", "name": "인스타그램", "type": "social"}
        ]
    }

# 파워블로거 관련 API
@app.get("/api/power-bloggers")
async def get_power_bloggers(
    category: Optional[str] = None, 
    platform: Optional[str] = None,
    minSubscribers: Optional[int] = None,
    maxSubscribers: Optional[int] = None,
    minEngagementRate: Optional[float] = None
):
    filtered_bloggers = power_bloggers_db
    
    if category:
        filtered_bloggers = [b for b in filtered_bloggers if b["category"] == category]
    
    if platform:
        filtered_bloggers = [b for b in filtered_bloggers if b["platform"] == platform]
    
    if minSubscribers:
        filtered_bloggers = [b for b in filtered_bloggers if b["subscriberCount"] >= minSubscribers]
        
    if maxSubscribers:
        filtered_bloggers = [b for b in filtered_bloggers if b["subscriberCount"] <= maxSubscribers]
        
    if minEngagementRate:
        filtered_bloggers = [b for b in filtered_bloggers if b["engagementRate"] >= minEngagementRate]
    
    return filtered_bloggers

@app.get("/api/power-bloggers/{blogger_id}")
async def get_power_blogger(blogger_id: str):
    blogger = next((b for b in power_bloggers_db if b["id"] == blogger_id), None)
    if not blogger:
        raise HTTPException(status_code=404, detail="블로거를 찾을 수 없습니다")
    return blogger

@app.post("/api/crawl/blogger")
async def crawl_blogger_data(request: dict):
    blog_url = request.get("blogUrl")
    if not blog_url:
        raise HTTPException(status_code=400, detail="블로그 URL이 필요합니다")
    
    # 플랫폼 자동 감지
    platform = "naver_blog"  # 기본값
    if "tistory.com" in blog_url:
        platform = "tistory"
    elif "blogspot.com" in blog_url:
        platform = "blogspot"
    elif "kakao.com" in blog_url:
        platform = "kakao_channel"
    elif "instagram.com" in blog_url:
        platform = "instagram"
    
    # 실제로는 크롤링 로직 구현
    new_blogger = {
        "id": str(uuid.uuid4()),
        "blogUrl": blog_url,
        "blogTitle": "새로 발견된 블로그",
        "bloggerName": "신규 블로거",
        "platform": platform,
        "category": "lifestyle",
        "subscriberCount": 5000,
        "avgViews": 1200,
        "avgLikes": 45,
        "avgComments": 12,
        "engagementRate": 0.048,
        "contactEmail": "newblogger@example.com",
        "collaborationRate": 150000,
        "lastActive": datetime.now(),
        "isVerified": False,
        "tags": ["신규", "라이프스타일"]
    }
    
    power_bloggers_db.append(new_blogger)
    return new_blogger

# 체험단 후기 크롤링 API
@app.post("/api/crawl/reviews")
async def crawl_reviews(request: dict):
    keywords = request.get("keywords", [])
    category = request.get("category", "beauty")
    
    # 실제로는 네이버 블로그 크롤링 로직 구현
    sample_reviews = [
        {
            "id": str(uuid.uuid4()),
            "productName": "신제품 스킨케어",
            "blogUrl": "https://blog.naver.com/review1",
            "bloggerName": "리뷰어1",
            "title": "신제품 스킨케어 체험 후기",
            "content": "정말 좋은 제품이에요. 사용 후 피부가 촉촉해졌습니다...",
            "rating": 4.5,
            "pros": ["보습력 좋음", "향이 좋음", "흡수 빠름"],
            "cons": ["가격이 비쌈"],
            "images": [],
            "publishedAt": datetime.now(),
            "category": category,
            "sentiment": "positive",
            "keywords": keywords
        },
        {
            "id": str(uuid.uuid4()),
            "productName": "신제품 스킨케어",
            "blogUrl": "https://blog.naver.com/review2",
            "bloggerName": "리뷰어2",
            "title": "스킨케어 솔직 후기",
            "content": "기대했던 것보다는 아쉬웠어요. 그래도 나쁘지 않습니다...",
            "rating": 3.5,
            "pros": ["패키지 예쁨", "용량 적당"],
            "cons": ["효과 미미", "끈적함"],
            "images": [],
            "publishedAt": datetime.now(),
            "category": category,
            "sentiment": "neutral",
            "keywords": keywords
        }
    ]
    
    reviews_db.extend(sample_reviews)
    return sample_reviews

@app.get("/api/campaigns/{campaign_id}/reviews")
async def get_campaign_reviews(campaign_id: str):
    # 실제로는 캠페인별 리뷰 필터링
    return reviews_db

# 콘텐츠 자동 생성 API
@app.post("/api/content/generate")
async def generate_content(request: dict):
    campaign_id = request.get("campaignId")
    content_type = request.get("contentType", "blog_post")
    based_on_reviews = request.get("basedOnReviews", [])
    tone = request.get("tone", "friendly")
    target_audience = request.get("targetAudience", "20-30대 여성")
    
    # 실제로는 AI 기반 콘텐츠 생성
    if content_type == "blog_post":
        generated_content = {
            "id": str(uuid.uuid4()),
            "campaignId": campaign_id,
            "contentType": content_type,
            "title": "신제품 스킨케어 완벽 가이드 - 실제 체험단 후기 모음",
            "content": """안녕하세요! 오늘은 최근 화제가 되고 있는 신제품 스킨케어에 대해 자세히 알아보겠습니다.

실제 체험단분들의 후기를 종합해보니, 이 제품의 가장 큰 장점은 뛰어난 보습력이었습니다. 
많은 분들이 "사용 후 피부가 정말 촉촉해졌다"고 말씀하셨어요.

🌟 주요 장점:
- 뛰어난 보습력으로 건조한 피부에 효과적
- 은은하고 좋은 향으로 사용감이 좋음
- 빠른 흡수력으로 끈적임 없이 산뜻함

💡 사용 팁:
세안 후 토너 사용 후 적당량을 발라주시면 됩니다. 
특히 밤에 사용하시면 다음날 아침 피부 상태가 확연히 달라지는 것을 느끼실 수 있어요!

지금 구매하시면 특별 할인 혜택도 받으실 수 있으니 놓치지 마세요! ✨""",
            "hashtags": ["스킨케어", "뷰티", "보습", "체험후기", "추천"],
            "targetAudience": target_audience,
            "tone": tone,
            "basedOnReviews": based_on_reviews,
            "generatedAt": datetime.now(),
            "status": "draft"
        }
    else:
        generated_content = {
            "id": str(uuid.uuid4()),
            "campaignId": campaign_id,
            "contentType": content_type,
            "title": "",
            "content": "신제품 스킨케어 체험해봤어요! 💕 보습력이 정말 좋네요 ✨ 여러분도 한번 써보세요! #스킨케어 #뷰티 #추천",
            "hashtags": ["스킨케어", "뷰티", "추천", "체험후기"],
            "targetAudience": target_audience,
            "tone": tone,
            "basedOnReviews": based_on_reviews,
            "generatedAt": datetime.now(),
            "status": "draft"
        }
    
    generated_content_db.append(generated_content)
    return generated_content

@app.get("/api/campaigns/{campaign_id}/content")
async def get_generated_content(campaign_id: str):
    return [c for c in generated_content_db if c["campaignId"] == campaign_id]

@app.patch("/api/content/{content_id}/approve")
async def approve_content(content_id: str):
    for content in generated_content_db:
        if content["id"] == content_id:
            content["status"] = "approved"
            return content
    raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다")

# 블로거 컨택 관련 API
@app.post("/api/blogger-outreach")
async def create_blogger_outreach(request: dict):
    outreach_data = {
        "id": str(uuid.uuid4()),
        "sentAt": datetime.now(),
        **request
    }
    blogger_outreach_db.append(outreach_data)
    return outreach_data

@app.get("/api/campaigns/{campaign_id}/blogger-outreach")
async def get_blogger_outreach(campaign_id: str):
    return [o for o in blogger_outreach_db if o["campaignId"] == campaign_id]

@app.post("/api/blogger-outreach/bulk-send")
async def send_bulk_emails(request: dict):
    campaign_id = request.get("campaignId")
    blogger_ids = request.get("bloggerIds", [])
    template = request.get("template")
    
    # 실제로는 이메일 발송 로직 구현
    sent_count = len(blogger_ids)
    failed_count = 0
    
    # 발송 기록 저장
    for blogger_id in blogger_ids:
        outreach_data = {
            "id": str(uuid.uuid4()),
            "campaignId": campaign_id,
            "bloggerId": blogger_id,
            "contactMethod": "email",
            "subject": "협업 제안",
            "message": template,
            "proposedRate": 200000,
            "sentAt": datetime.now(),
            "status": "sent"
        }
        blogger_outreach_db.append(outreach_data)
    
    return {"sent": sent_count, "failed": failed_count}

# 대시보드 통계 API
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    return {
        "activeCampaigns": len([c for c in campaigns_db if c["status"] == "active"]),
        "pendingApprovals": len([v for v in copy_variants_db if not v["approved"]]),
        "sentProposals": 5,
        "awaitingReplies": 2
    }

if __name__ == "__main__":
    import uvicorn
    
    # 포트 5678에서 실행
    port = 5678
    
    print(f"🚀 마케팅 플랫폼 API 서버를 포트 {port}에서 시작합니다...")
    print(f"📖 API 문서: http://localhost:{port}/docs")
    print(f"🌐 API 서버: http://localhost:{port}")
    print("⏹️  종료하려면 Ctrl+C를 누르세요")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except KeyboardInterrupt:
        print("\n✅ 서버가 정상적으로 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)