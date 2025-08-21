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
                "description": "거북목 교정에 도움되는 목 스트레칭 도구",
                "price": "45,000원",
                "url": "https://www.coupang.com/vp/products/123456789",
                "image": "🦒",
                "benefit": "목 근육 이완 및 자세 교정에 효과적"
            },
            {
                "name": "인체공학적 목받침대",
                "description": "장시간 작업 시 목 부담을 줄여주는 목받침대",
                "price": "89,000원",
                "url": "https://www.coupang.com/vp/products/987654321",
                "image": "🪑",
                "benefit": "올바른 목 자세 유지 도움"
            }
        ],
        "라운드숄더": [
            {
                "name": "어깨 교정 밴드",
                "description": "라운드숄더 교정을 위한 어깨 스트레칭 밴드",
                "price": "32,000원",
                "url": "https://www.coupang.com/vp/products/456789123",
                "image": "🎽",
                "benefit": "어깨 자세 교정 및 근육 강화"
            },
            {
                "name": "등 스트레칭 도구",
                "description": "등 근육 이완과 자세 교정을 위한 도구",
                "price": "67,000원",
                "url": "https://www.coupang.com/vp/products/789123456",
                "image": "🧘‍♀️",
                "benefit": "등 근육 긴장 완화 효과"
            }
        ],
        "허리디스크": [
            {
                "name": "허리 디스크 예방 인체공학 의자",
                "description": "허리 건강을 위한 인체공학적 사무용 의자",
                "price": "299,000원",
                "url": "https://www.coupang.com/vp/products/321654987",
                "image": "🪑",
                "benefit": "허리 부담 최소화 및 올바른 자세 유지"
            },
            {
                "name": "허리 보조대",
                "description": "허리 통증 완화를 위한 의료용 보조대",
                "price": "78,000원",
                "url": "https://www.coupang.com/vp/products/654987321",
                "image": "🩹",
                "benefit": "허리 지지 및 통증 완화"
            }
        ],
        "손목터널증후군_왼쪽": [
            {
                "name": "인체공학적 마우스",
                "description": "손목터널 증후군 예방을 위한 인체공학적 마우스",
                "price": "89,000원",
                "url": "https://www.coupang.com/vp/products/147258369",
                "image": "🖱️",
                "benefit": "손목 부담 최소화 및 자연스러운 그립"
            },
            {
                "name": "손목 보조대",
                "description": "손목 통증 완화를 위한 의료용 보조대",
                "price": "25,000원",
                "url": "https://www.coupang.com/vp/products/258369147",
                "image": "🩹",
                "benefit": "손목 지지 및 통증 완화"
            }
        ],
        "손목터널증후군_오른쪽": [
            {
                "name": "인체공학적 마우스",
                "description": "손목터널 증후군 예방을 위한 인체공학적 마우스",
                "price": "89,000원",
                "url": "https://www.coupang.com/vp/products/147258369",
                "image": "🖱️",
                "benefit": "손목 부담 최소화 및 자연스러운 그립"
            },
            {
                "name": "손목 보조대",
                "description": "손목 통증 완화를 위한 의료용 보조대",
                "price": "25,000원",
                "url": "https://www.coupang.com/vp/products/258369147",
                "image": "🩹",
                "benefit": "손목 지지 및 통증 완화"
            }
        ]
    }
    return products_db.get(condition, [])

def show_healthcare_product_recommendation(condition):
    """헬스케어 제품 추천 UI"""
    products = get_healthcare_products(condition)
    
    if products:
        st.subheader("🛒 추천 헬스케어 제품")
        st.info("💡 운동과 함께 사용하면 더욱 효과적인 제품들을 추천해드려요!")
        
        for product in products:
            with st.container():
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"<h2 style='text-align: center;'>{product['image']}</h2>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{product['name']}**")
                    st.markdown(f"*{product['description']}*")
                    st.markdown(f"💪 **효과**: {product['benefit']}")
                    st.markdown(f"💰 **가격**: {product['price']}")
                    
                    # 제휴 링크 생성
                    affiliate_link = show_coupang_affiliate_link(product['url'], product['name'])
                    
                    if st.button(f"🛒 쿠팡에서 구매하기", key=f"buy_{product['name']}"):
                        st.markdown(f"[🛒 쿠팡에서 구매하기]({affiliate_link})")
                        st.success("✅ 쿠팡 페이지로 이동합니다!")
                
                st.markdown("---")

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
    
    st.subheader("🛒 추천 헬스케어 제품")
    st.info("💡 개발자 건강을 위한 필수 아이템들을 추천해드려요!")
    
    for product in general_products:
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"<h2 style='text-align: center;'>{product['image']}</h2>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{product['name']}**")
                st.markdown(f"*{product['description']}*")
                st.markdown(f"💪 **효과**: {product['benefit']}")
                st.markdown(f"💰 **가격**: {product['price']}")
                
                # 제휴 링크 생성
                affiliate_link = show_coupang_affiliate_link(product['url'], product['name'])
                
                if st.button(f"🛒 쿠팡에서 구매하기", key=f"buy_general_{product['name']}"):
                    st.markdown(f"[🛒 쿠팡에서 구매하기]({affiliate_link})")
                    st.success("✅ 쿠팡 페이지로 이동합니다!")
            
            st.markdown("---")

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
