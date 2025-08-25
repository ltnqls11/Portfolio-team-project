import streamlit as st

# ============================================================================
# 광고 모듈 (실제 웹사이트용)
# ============================================================================
# 이 모듈은 VDT 증후군 관리 시스템의 광고 표시를 담당합니다.
# 실제 배포 시에는 Google AdSense 코드로 교체하세요.

# ============================================================================
# 설정 상수
# ============================================================================
ADSENSE_PUBLISHER_ID = "YOUR_ADSENSE_PUBLISHER_ID"   # Google AdSense 퍼블리셔 ID
COUPANG_PARTNER_ID = "AF6363203"                     # 쿠팡 파트너스 아이디

# ============================================================================
# 광고 표시 함수
# ============================================================================
def show_adsense_banner():
    """Google AdSense 광고 배너를 표시합니다."""
    st.markdown("""
    <div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin: 10px 0;">
        <small>📢 광고</small>
        <br>
        <small style="color: #666;">Google AdSense 광고 영역</small>
    </div>
    """, unsafe_allow_html=True)
    
    # 실제 AdSense 코드 (주석 처리)
    st.markdown("""
    <!-- 
    실제 배포 시 아래 코드를 활성화하세요:
    
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=YOUR_PUBLISHER_ID"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="YOUR_PUBLISHER_ID"
         data-ad-slot="YOUR_AD_SLOT_ID"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
    -->""", unsafe_allow_html=True)

def show_coupang_affiliate_link(product_url, product_name):
    """쿠팡 제휴 링크를 생성합니다."""
    if "?" in product_url:
        affiliate_link = f"{product_url}&partnerId={COUPANG_PARTNER_ID}"
    else:
        affiliate_link = f"{product_url}?partnerId={COUPANG_PARTNER_ID}"
    
    return affiliate_link

def get_healthcare_products(condition):
    """증상별 헬스케어 제품 추천"""
    products_db = {
        "거북목": [
            {
                "name": "목 스트레칭 도구 세트",
                "description": "개발자들이 많이 겪는 거북목 증상을 개선하는 전문 스트레칭 도구입니다",
                "price": "45,000원",
                "url": "https://www.coupang.com/vp/products/123456789",
                "image": "📦",
                "benefit": "경직된 목 근육을 이완시키고 자세를 교정합니다"
            },
            {
                "name": "인체공학적 목받침대",
                "description": "장시간 코딩 시 목 부담을 줄여주는 목받침대입니다",
                "price": "89,000원",
                "url": "https://www.coupang.com/vp/products/987654321",
                "image": "🪑",
                "benefit": "목이 앞으로 나오는 것을 방지하고 올바른 자세를 유지합니다"
            }
        ],
        "라운드숄더": [
            {
                "name": "어깨 교정 밴드",
                "description": "어깨가 앞으로 말리는 라운드숄더 증상을 교정하는 전문 밴드입니다",
                "price": "32,000원",
                "url": "https://www.coupang.com/vp/products/456789123",
                "image": "🎽",
                "benefit": "어깨를 뒤로 당기고 등 근육을 강화합니다"
            },
            {
                "name": "등 스트레칭 도구",
                "description": "굽은 등과 어깨 통증을 완화하는 스트레칭 도구입니다",
                "price": "67,000원",
                "url": "https://www.coupang.com/vp/products/789123456",
                "image": "🧘‍♀️",
                "benefit": "등 근육의 긴장을 이완시키고 자세를 교정합니다"
            }
        ],
        "허리디스크": [
            {
                "name": "허리 디스크 예방 인체공학 의자",
                "description": "허리 디스크를 예방하고 허리 건강을 지키는 전문 의자입니다",
                "price": "299,000원",
                "url": "https://www.coupang.com/vp/products/321654987",
                "image": "🪑",
                "benefit": "허리 부담을 줄이고 올바른 자세를 유지합니다"
            },
            {
                "name": "허리 보조대",
                "description": "허리 통증 시 착용하여 통증을 완화하는 의료용 보조대입니다",
                "price": "78,000원",
                "url": "https://www.coupang.com/vp/products/654987321",
                "image": "🩹",
                "benefit": "허리를 지지하고 통증을 감소시킵니다"
            }
        ],
        "손목터널증후군": [
            {
                "name": "인체공학적 마우스",
                "description": "손목터널 증후군을 예방하는 인체공학적으로 설계된 마우스입니다",
                "price": "89,000원",
                "url": "https://www.coupang.com/vp/products/147258369",
                "image": "🖱️",
                "benefit": "손목 부담을 줄이고 자연스러운 그립감을 제공합니다"
            },
            {
                "name": "손목 보조대",
                "description": "손목 통증 시 착용하여 통증을 완화하는 의료용 보조대입니다",
                "price": "25,000원",
                "url": "https://www.coupang.com/vp/products/258369147",
                "image": "🩹",
                "benefit": "손목을 지지하고 통증을 감소시킵니다"
            },
            {
                "name": "키보드 손목받침",
                "description": "타이핑 시 손목을 편안하게 받쳐주는 쿠션입니다",
                "price": "35,000원",
                "url": "https://www.coupang.com/vp/products/365478912",
                "image": "⌨️",
                "benefit": "장시간 타이핑 시 손목 부담을 줄여줍니다"
            }
        ]
    }
    # 손목터널증후군 조건명 정규화
    if "손목터널증후군" in condition:
        condition = "손목터널증후군"
    
    return products_db.get(condition, [])

def show_healthcare_product_recommendation(condition):
    """헬스케어 제품 추천 UI"""
    products = get_healthcare_products(condition)
    
    if products:
        st.subheader("📦 추천 헬스케어 제품")
        st.info("💡 운동과 함께 사용하면 더욱 효과적인 제품들을 추천해드려요!")
        
        for product in products:
            with st.container():
                st.markdown("---")
                
                # 제품명을 크게 표시
                st.markdown(f"### {product['name']}")
                
                # 전문적인 제품 설명
                st.markdown(f"**제품 개요:** {product['description']}")
                
                # 주요 효과 - 더 전문적으로
                st.markdown(f"**임상적 효과:** {product['benefit']}")
                
                # 제휴 링크 생성
                affiliate_link = show_coupang_affiliate_link(product['url'], product['name'])
                
                # 바로 쿠팡 링크로 연결 (한 번 클릭)
                st.markdown(f"[🛒 쿠팡에서 구매하기]({affiliate_link})")

def show_general_healthcare_products():
    """일반적인 헬스케어 제품 추천 (홈페이지용)"""
    general_products = [
        {
            "name": "블루라이트 차단 안경",
            "description": "장시간 모니터 작업 시 눈 피로도 감소",
            "price": "35,000원",
            "url": "https://www.coupang.com/vp/products/111222333",
            "image": "👓",
            "benefit": "블루라이트 차단으로 눈 건강 보호"
        },
        {
            "name": "스탠딩 데스크",
            "description": "앉아서 일하는 시간을 줄여주는 스탠딩 데스크",
            "price": "189,000원",
            "url": "https://www.coupang.com/vp/products/444555666",
            "image": "🪑",
            "benefit": "허리 건강 개선 및 혈액순환 증진"
        },
        {
            "name": "눈 건강 보조제",
            "description": "루테인, 지아잔틴이 함유된 눈 건강 보조제",
            "price": "45,000원",
            "url": "https://www.coupang.com/vp/products/777888999",
            "image": "💊",
            "benefit": "눈 피로 완화 및 시력 보호"
        }
    ]
    
    st.subheader("📦 추천 헬스케어 제품")
    st.info("💡 개발자 건강을 위한 필수 아이템들을 추천해드려요!")
    
    for product in general_products:
        with st.container():
            st.markdown("---")
            
            # 제품명을 크게 표시
            st.markdown(f"### {product['name']}")
            
            # 전문적인 제품 설명
            st.markdown(f"**제품 개요:** {product['description']}")
            
            # 주요 효과 - 더 전문적으로
            st.markdown(f"**임상적 효과:** {product['benefit']}")
            
            # 제휴 링크 생성
            affiliate_link = show_coupang_affiliate_link(product['url'], product['name'])
            
            # 바로 쿠팡 링크로 연결 (한 번 클릭)
            st.markdown(f"[🛒 쿠팡에서 구매하기]({affiliate_link})")

# ============================================================================
# 개발자용 관리 기능 (개발 중에만 사용)
# ============================================================================
def show_developer_dashboard():
    """개발자용 광고 관리 대시보드 (개발 중에만 사용)"""
    st.header("🔧 개발자용 광고 관리")
    st.warning("⚠️ 이 기능은 개발 중에만 사용하세요. 실제 배포 시에는 제거하세요.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 설정 정보")
        st.write(f"**AdSense 퍼블리셔 ID**: {ADSENSE_PUBLISHER_ID}")
        st.write(f"**쿠팡 파트너스 ID**: {COUPANG_PARTNER_ID}")
    
    with col2:
        st.subheader("🔗 제휴 링크 테스트")
        test_url = st.text_input("테스트 URL", "https://www.coupang.com/vp/products/123456")
        if st.button("제휴 링크 생성"):
            affiliate_link = show_coupang_affiliate_link(test_url, "테스트 상품")
            st.code(affiliate_link)
    
    st.subheader("📋 배포 시 체크리스트")
    st.markdown("""
    1. ✅ AdSense 퍼블리셔 ID 설정
    2. ✅ AdSense 광고 코드 활성화
    3. ✅ 개발자용 대시보드 제거
    4. ✅ 쿠팡 제휴 링크 적용
    5. ✅ 광고 위치 최적화
    """)

# ============================================================================
# TODO: 실제 배포 시 구현할 기능들
# ============================================================================
"""
TODO: 실제 배포 시 구현할 기능들

1. Google AdSense 실제 코드 삽입
   - 퍼블리셔 ID 설정
   - 광고 슬롯 ID 설정
   - 반응형 광고 설정

2. 쿠팡 제휴 링크 자동 생성
   - 제품 추천 시 자동으로 제휴 링크 적용
   - 클릭 추적 기능

3. 광고 성과 분석
   - Google Analytics 연동
   - 클릭률 분석
   - 수익 최적화

4. 광고 위치 최적화
   - A/B 테스트
   - 사용자 경험 고려
   - 로딩 속도 최적화
"""

def get_personalized_products(user_data, conditions, pain_scores):
    """개인화된 제품 추천 - 분석 완료 후 호출"""
    
    # 통증 심각도 분석
    total_pain = sum(pain_scores.values()) if pain_scores else 0
    avg_pain = total_pain / len(pain_scores) if pain_scores else 0
    
    # 사용자 정보
    age = user_data.get('age', 30)
    work_intensity = user_data.get('work_intensity', '보통')
    env_score = user_data.get('env_score', 50)
    exercise_habit = user_data.get('exercise_habit', '전혀 안함')
    
    # 개인화된 제품 데이터베이스
    personalized_products = []
    
    # 1. 통증 심각도에 따른 우선순위 제품
    if avg_pain >= 7:  # 심각한 통증
        personalized_products.extend([
            {
                "name": "의료용 목보조기 (심한 통증용)",
                "description": "심한 거북목 통증이 있을 때 착용하면 통증을 완화시켜주는 의료용 목보조기예요",
                "price": "89,000원",
                "url": "https://www.coupang.com/np/search?component=&q=의료용+목보조기&channel=user",
                "image": "🩹",
                "benefit": "심한 통증을 완화시켜주고 목을 안정적으로 지지해줘요",
                "note": "통증이 심할 때 착용하시면 효과를 바로 느끼실 수 있어요"
            },
            {
                "name": "전문가용 허리보조대",
                "description": "허리디스크 통증이 있을 때 착용하면 통증을 완화시켜주는 전문가용 보조대예요",
                "price": "156,000원",
                "url": "https://www.coupang.com/np/search?component=&q=전문가용+허리보조대&channel=user",
                "image": "🩹",
                "benefit": "허리 통증을 줄여주고 척추를 보호해줘요",
                "note": "심각한 통증 상태에서 착용하시면 도움이 될 거예요"
            }
        ])
    
    elif avg_pain >= 4:  # 중간 통증
        personalized_products.extend([
            {
                "name": "목 스트레칭 도구 세트",
                "description": "개발자분들이 많이 겪는 거북목 증상을 개선해주는 전문 스트레칭 도구예요",
                "price": "45,000원",
                "url": "https://www.coupang.com/np/search?component=&q=목+스트레칭+도구+세트&channel=user",
                "image": "🦒",
                "benefit": "경직된 목 근육을 풀어주고 자세를 바로잡아줘요",
                "note": "통증이 중간 정도일 때 예방 차원에서 사용하시면 좋아요"
            },
            {
                "name": "어깨 교정 밴드",
                "description": "어깨가 앞으로 말리는 라운드숄더 증상을 교정해주는 전문 밴드예요",
                "price": "32,000원",
                "url": "https://www.coupang.com/np/search?component=&q=어깨+교정+밴드&channel=user",
                "image": "🎽",
                "benefit": "어깨를 뒤로 당겨주고 등 근육을 강화시켜줘요",
                "note": "어깨 자세 교정으로 통증 예방에 도움이 될 거예요"
            }
        ])
    
    # 2. 작업환경 점수에 따른 제품
    if env_score < 60:  # 작업환경이 나쁨
        personalized_products.extend([
            {
                "name": "인체공학적 사무용 의자",
                "description": "허리 디스크를 예방하고 허리 건강을 지켜주는 전문 의자예요",
                "price": "299,000원",
                "url": "https://www.coupang.com/np/search?component=&q=인체공학적+사무용+의자&channel=user",
                "image": "🪑",
                "benefit": "허리에 가는 부담을 줄여주고 올바른 자세를 유지하게 도와줘요",
                "note": "작업환경을 개선해서 증상 예방에 도움이 될 거예요"
            }
        ])
    
    # 3. 증상별 필수 제품
    for condition in conditions:
        if condition == "손목터널증후군":
            personalized_products.extend([
                {
                    "name": "인체공학적 마우스",
                    "description": "손목터널 증후군을 예방해주는 인체공학적으로 설계된 마우스예요",
                    "price": "89,000원",
                    "url": "https://www.coupang.com/np/search?component=&q=인체공학적+마우스&channel=user",
                    "image": "🖱️",
                    "benefit": "손목에 가는 부담을 줄여주고 자연스러운 그립감을 제공해줘요",
                    "note": "손목터널증후군 증상에 효과적이에요"
                }
            ])
    
    # 중복 제거
    seen_names = set()
    unique_products = []
    for product in personalized_products:
        if product['name'] not in seen_names:
            seen_names.add(product['name'])
            unique_products.append(product)
    
    return unique_products[:4]  # 최대 4개 제품

def show_personalized_product_recommendation(user_data, conditions, pain_scores):
    """개인화된 제품 추천 UI - 분석 완료 후 호출"""
    
    if not conditions:
        st.warning("⚠️ 먼저 증상을 선택해주세요.")
        return

    # 개인화된 제품 가져오기
    products = get_personalized_products(user_data, conditions, pain_scores)
    
    if not products:
        st.info("ℹ️ 현재 상태에 맞는 특별한 제품 추천이 없습니다.")
        return
    
    # 제품 추천 - 전문적인 UI/UX
    for i, product in enumerate(products, 1):
        with st.container():
            st.markdown("---")
            
            # 제품명을 크게 표시
            st.markdown(f"### {product['name']}")
            
            # 전문적인 제품 설명
            st.markdown(f"**제품 개요:** {product['description']}")
            
            # 임상적 효과
            st.markdown(f"**임상적 효과:** {product['benefit']}")
            
            # 사용 가이드라인
            st.info(f"**사용 가이드라인:** {product['note']}")
            
            # 제휴 링크 생성
            affiliate_link = show_coupang_affiliate_link(product['url'], product['name'])
            
            # 바로 쿠팡 링크로 연결 (한 번 클릭)
            st.markdown(f"[🛒 쿠팡에서 구매하기]({affiliate_link})")
    

def show_adsense_ads():
    """Google AdSense 광고 표시"""
    st.markdown("""
    <div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin: 10px 0;">
        <small>📢 광고</small>
        <br>
        <small style="color: #666;">Google AdSense 광고 영역</small>
    </div>
    """, unsafe_allow_html=True)

def show_hospital_recommendation(condition, pain_level):
    """병원 추천 기능 - AdSense 광고로 표시"""
    if pain_level >= 7:
        st.info("현재 통증이 심한 편입니다. 주변 병원을 방문해 정확한 원인을 확인해 보시는 것이 좋습니다.")
        
        # Google AdSense 광고 영역
        st.markdown("""
        <div style="text-align: center; padding: 20px; background-color: #f8f9fa; border: 2px solid #e9ecef; border-radius: 10px; margin: 15px 0;">
            <div style="background-color: #e9ecef; color: #6c757d; padding: 8px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; margin-bottom: 15px; display: inline-block;">
                Google AdSense 영역
            </div>
            <div style="background-color: white; border-radius: 8px; padding: 20px; margin: 10px 0; border: 1px solid #dee2e6; min-height: 120px; display: flex; align-items: center; justify-content: center;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; color: #2c5aa0; font-weight: bold; margin-bottom: 8px;">OO정형외과</div>
                    <div style="font-size: 14px; color: #666; margin-bottom: 8px;">목디스크 • 허리디스크 • 어깨통증 전문</div>
                    <div style="font-size: 12px; color: #888; margin-bottom: 12px;">✓ 무료 상담 ✓ 당일 진료 ✓ 전문의 진료</div>
                    <div style="background-color: #2c5aa0; color: white; padding: 8px 16px; border-radius: 4px; font-size: 12px; font-weight: bold; display: inline-block;">
                        예약 문의: 02-1234-5678
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 실제 AdSense 코드 (주석 처리)
        st.markdown("""
        <!-- 
        실제 배포 시 아래 AdSense 병원 광고 코드를 활성화하세요:
        
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=YOUR_PUBLISHER_ID"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="YOUR_PUBLISHER_ID"
             data-ad-slot="HOSPITAL_AD_SLOT_ID"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({});
        </script>
        -->""", unsafe_allow_html=True)
