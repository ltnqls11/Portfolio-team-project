#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네이버 카페 API를 사용한 자동 포스팅 클라이언트
"""

import requests
import json
import time
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NAVER_CAFE_ID, NAVER_MENU_ID


class NaverCafeClient:
    def __init__(self):
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.cafe_id = NAVER_CAFE_ID
        self.menu_id = NAVER_MENU_ID
        self.access_token = None
        
        if not all([self.client_id, self.client_secret, self.cafe_id, self.menu_id]):
            print("⚠️ 네이버 카페 API 설정이 완료되지 않았습니다.")
            print("💡 .env 파일에서 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, NAVER_CAFE_ID, NAVER_MENU_ID를 설정하세요.")
        else:
            print("✓ 네이버 카페 API 설정 확인됨")
    
    def get_access_token(self):
        """네이버 API 액세스 토큰 발급"""
        try:
            # 실제 환경에서는 OAuth 2.0 플로우를 통해 토큰을 발급받아야 합니다.
            # 여기서는 시뮬레이션을 위한 코드입니다.
            print("📡 네이버 API 액세스 토큰 발급 중...")
            
            # 실제로는 사용자 인증을 통해 토큰을 받아야 하지만,
            # 데모 목적으로 클라이언트 자격증명 방식 시뮬레이션
            token_url = "https://nid.naver.com/oauth2.0/token"
            
            # 실제 구현에서는 적절한 OAuth 플로우를 사용해야 합니다
            print("⚠️ 실제 환경에서는 OAuth 2.0 인증이 필요합니다.")
            print("💡 네이버 개발자 센터에서 카페 API 권한을 신청하고 인증 토큰을 발급받으세요.")
            
            # 시뮬레이션용 가짜 토큰
            self.access_token = "DEMO_ACCESS_TOKEN"
            return True
            
        except Exception as e:
            print(f"✗ 액세스 토큰 발급 실패: {e}")
            return False
    
    def create_post_content(self, product_name, event_info):
        """카페 게시물 내용 생성"""
        subject = f"[신제품 출시] {product_name}를 소개합니다!"
        
        content = f"""
안녕하세요, 회원 여러분! 👋

드디어 저희의 야심작, **{product_name}**가 출시되었습니다! 🎉

## 🌟 제품 특징
- 엄선된 고품질 원료 사용
- 과학적으로 검증된 효과
- 안전하고 신뢰할 수 있는 품질

## 🎁 특별 이벤트
{event_info}와 같은 특별 이벤트도 진행 중이니 많은 관심 부탁드립니다!

## 📞 문의사항
궁금한 점이 있으시면 언제든지 댓글로 문의해 주세요.

감사합니다! 😊

---
*이 게시물은 자동화 시스템을 통해 작성되었습니다.*
        """
        
        return subject, content
    
    def post_to_cafe(self, product_name, event_info="특별 할인 이벤트"):
        """네이버 카페에 게시물 작성"""
        try:
            if not self.access_token:
                if not self.get_access_token():
                    return False
            
            print(f"📝 네이버 카페에 '{product_name}' 관련 게시물 작성 중...")
            
            # 게시물 내용 생성
            subject, content = self.create_post_content(product_name, event_info)
            
            # 실제 API 호출 (시뮬레이션)
            api_url = f"https://openapi.naver.com/v1/cafe/{self.cafe_id}/menu/{self.menu_id}/articles"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'subject': subject,
                'content': content
            }
            
            print(f"📤 카페 ID: {self.cafe_id}")
            print(f"📤 메뉴 ID: {self.menu_id}")
            print(f"📤 제목: {subject}")
            print(f"📤 내용 길이: {len(content)}자")
            
            # 실제 환경에서는 아래 주석을 해제하고 실제 API 호출
            # response = requests.post(api_url, headers=headers, data=data)
            
            # 시뮬레이션을 위한 가짜 응답
            print("⚠️ 데모 모드: 실제 카페 포스팅은 수행되지 않습니다.")
            print("💡 실제 환경에서는 네이버 카페 API 인증 후 포스팅이 가능합니다.")
            
            # 시뮬레이션 성공
            fake_article_id = f"demo_{int(time.time())}"
            
            print(f"✓ 카페 포스팅 완료 (시뮬레이션)")
            print(f"📄 게시물 ID: {fake_article_id}")
            print(f"🔗 예상 URL: https://cafe.naver.com/{self.cafe_id}/{fake_article_id}")
            
            return True
            
        except Exception as e:
            print(f"✗ 카페 포스팅 실패: {e}")
            return False
    
    def post_multiple_cafes(self, cafe_list, product_name, event_info="특별 할인 이벤트"):
        """여러 카페에 동시 포스팅"""
        print(f"\n📝 {len(cafe_list)}개 카페에 동시 포스팅 시작...")
        
        success_count = 0
        failed_count = 0
        
        for i, cafe_info in enumerate(cafe_list, 1):
            try:
                cafe_name = cafe_info.get('name', f'카페{i}')
                print(f"[{i}/{len(cafe_list)}] {cafe_name}에 포스팅 중...")
                
                # 각 카페별로 설정 업데이트
                original_cafe_id = self.cafe_id
                original_menu_id = self.menu_id
                
                self.cafe_id = cafe_info.get('cafe_id', self.cafe_id)
                self.menu_id = cafe_info.get('menu_id', self.menu_id)
                
                if self.post_to_cafe(product_name, event_info):
                    success_count += 1
                else:
                    failed_count += 1
                
                # 원래 설정 복원
                self.cafe_id = original_cafe_id
                self.menu_id = original_menu_id
                
                # API 호출 제한을 위한 대기
                time.sleep(2)
                
            except Exception as e:
                print(f"[{i}/{len(cafe_list)}] {cafe_info.get('name', '알 수 없음')} 처리 중 오류: {e}")
                failed_count += 1
                continue
        
        print(f"\n📊 카페 포스팅 완료!")
        print(f"✓ 성공: {success_count}건")
        print(f"✗ 실패: {failed_count}건")
        print(f"📈 성공률: {(success_count/(success_count+failed_count)*100):.1f}%" if (success_count+failed_count) > 0 else "0%")
        
        return success_count, failed_count