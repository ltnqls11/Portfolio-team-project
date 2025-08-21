#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
완전한 블로거 마케팅 자동화 시스템
①블로거 정보 수집 → ②이메일 자동 발송 → ③네이버 카페 자동 포스팅
n8n 없이 독립적으로 동작하는 완전한 자동화 스크립트
"""

import sys
import argparse
import time
from datetime import datetime
from google_sheets_client import GoogleSheetsClient
from naver_blog_scraper import NaverBlogScraper
from gmail_client import GmailClient
from naver_cafe_client import NaverCafeClient


class CompleteAutomationSystem:
    def __init__(self):
        self.sheets_client = None
        self.scraper = None
        self.gmail_client = None
        self.cafe_client = None
        
    def initialize_clients(self):
        """모든 클라이언트 초기화"""
        try:
            print("🔧 시스템 초기화 중...")
            
            # Google Sheets 클라이언트
            print("📊 Google Sheets API 연결 중...")
            self.sheets_client = GoogleSheetsClient()
            
            # 네이버 블로그 스크래퍼
            print("🕷️ 네이버 블로그 스크래퍼 초기화 중...")
            self.scraper = NaverBlogScraper()
            
            # Gmail 클라이언트
            print("📧 Gmail API 연결 중...")
            self.gmail_client = GmailClient()
            
            # 네이버 카페 클라이언트
            print("📝 네이버 카페 API 연결 중...")
            self.cafe_client = NaverCafeClient()
            
            print("✅ 모든 클라이언트 초기화 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 클라이언트 초기화 실패: {e}")
            return False
    
    def step1_collect_blogger_info(self, keyword, sheet_id, sheet_name):
        """1단계: 블로거 정보 수집"""
        print("\n" + "="*60)
        print("1️⃣ 단계: 블로거 정보 수집")
        print("="*60)
        
        try:
            # 시트 헤더 초기화
            self.sheets_client.initialize_sheet_headers(sheet_id, sheet_name)
            
            # 네이버 블로그 검색
            print(f"🔍 키워드 '{keyword}'로 네이버 블로그 검색 중...")
            if not self.scraper.search_blogs(keyword):
                print("❌ 블로그 검색 실패")
                return []
            
            # 블로그 게시물 정보 추출
            print("📋 블로그 게시물 정보 추출 중...")
            blog_posts = self.scraper.extract_blog_posts()
            
            if not blog_posts:
                print("❌ 추출할 블로그 게시물이 없습니다.")
                return []
            
            print(f"✅ {len(blog_posts)}개 블로그 게시물 발견!")
            
            # 각 블로그에서 이메일 추출 및 데이터 저장
            print("📧 각 블로그에서 이메일 주소 추출 중...")
            successful_saves = 0
            blogger_list = []
            
            for i, blog_info in enumerate(blog_posts, 1):
                try:
                    print(f"[{i}/{len(blog_posts)}] {blog_info['blog_name']} 처리 중...")
                    
                    # 이메일 추출
                    try:
                        email = self.scraper.extract_email_from_blog(blog_info['blog_url'])
                        blog_info['email'] = email
                    except Exception as email_error:
                        print(f"⚠️ {blog_info['blog_name']} 이메일 탐색 실패: {email_error}")
                        blog_info['email'] = ""
                    
                    # Google Sheets에 데이터 저장
                    row_data = [
                        blog_info['blog_name'],
                        blog_info['post_url'],
                        blog_info['blog_url'],
                        blog_info['email']
                    ]
                    
                    self.sheets_client.append_row(sheet_id, sheet_name, row_data)
                    successful_saves += 1
                    
                    # 이메일이 있는 블로거만 리스트에 추가
                    if blog_info['email']:
                        blogger_list.append(blog_info)
                    
                    print(f"✅ 저장 완료: {blog_info['blog_name']} (이메일: {blog_info['email'] or '없음'})")
                    
                except Exception as e:
                    print(f"❌ {blog_info['blog_name']} 처리 중 오류: {e}")
                    continue
            
            print(f"\n📊 1단계 완료!")
            print(f"✅ 총 처리된 블로그: {len(blog_posts)}개")
            print(f"✅ 성공적으로 저장된 데이터: {successful_saves}개")
            print(f"📧 이메일이 있는 블로거: {len(blogger_list)}명")
            
            return blogger_list
            
        except Exception as e:
            print(f"❌ 1단계 실행 중 오류: {e}")
            return []
    
    def step2_send_emails(self, blogger_list, product_name, sender_name="마케팅팀"):
        """2단계: 이메일 자동 발송"""
        print("\n" + "="*60)
        print("2️⃣ 단계: 이메일 자동 발송")
        print("="*60)
        
        if not blogger_list:
            print("❌ 이메일을 발송할 블로거가 없습니다.")
            return False
        
        try:
            success_count, failed_count = self.gmail_client.send_bulk_emails(
                blogger_list, product_name, sender_name
            )
            
            print(f"\n📊 2단계 완료!")
            print(f"✅ 이메일 발송 성공: {success_count}건")
            print(f"❌ 이메일 발송 실패: {failed_count}건")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 2단계 실행 중 오류: {e}")
            return False
    
    def step3_post_to_cafe(self, product_name, event_info="특별 할인 이벤트"):
        """3단계: 네이버 카페 자동 포스팅"""
        print("\n" + "="*60)
        print("3️⃣ 단계: 네이버 카페 자동 포스팅")
        print("="*60)
        
        try:
            # 단일 카페에 포스팅
            success = self.cafe_client.post_to_cafe(product_name, event_info)
            
            print(f"\n📊 3단계 완료!")
            if success:
                print(f"✅ 카페 포스팅 성공!")
            else:
                print(f"❌ 카페 포스팅 실패!")
            
            return success
            
        except Exception as e:
            print(f"❌ 3단계 실행 중 오류: {e}")
            return False
    
    def run_complete_automation(self, keyword, sheet_id, sheet_name, product_name, 
                              event_info="특별 할인 이벤트", sender_name="마케팅팀"):
        """완전한 자동화 프로세스 실행"""
        start_time = datetime.now()
        
        print("🤖 완전한 블로거 마케팅 자동화 시스템 시작")
        print("="*80)
        print(f"🕐 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 검색 키워드: {keyword}")
        print(f"📊 Google Sheets: {sheet_id} / {sheet_name}")
        print(f"🎁 제품명: {product_name}")
        print(f"🎉 이벤트 정보: {event_info}")
        print("="*80)
        
        # 시스템 초기화
        if not self.initialize_clients():
            print("❌ 시스템 초기화 실패. 프로그램을 종료합니다.")
            return False
        
        try:
            # 1단계: 블로거 정보 수집
            blogger_list = self.step1_collect_blogger_info(keyword, sheet_id, sheet_name)
            
            if not blogger_list:
                print("❌ 이메일이 있는 블로거를 찾을 수 없어 2, 3단계를 건너뜁니다.")
                return False
            
            # 잠시 대기 (API 호출 제한 고려)
            print("\n⏳ 다음 단계 준비 중... (3초 대기)")
            time.sleep(3)
            
            # 2단계: 이메일 자동 발송
            email_success = self.step2_send_emails(blogger_list, product_name, sender_name)
            
            # 잠시 대기
            print("\n⏳ 다음 단계 준비 중... (3초 대기)")
            time.sleep(3)
            
            # 3단계: 네이버 카페 자동 포스팅
            cafe_success = self.step3_post_to_cafe(product_name, event_info)
            
            # 최종 결과 출력
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("\n" + "="*80)
            print("🎉 완전한 자동화 프로세스 완료!")
            print("="*80)
            print(f"🕐 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️ 총 소요 시간: {duration}")
            print(f"📊 수집된 블로거: {len(blogger_list)}명")
            print(f"📧 이메일 발송: {'성공' if email_success else '실패'}")
            print(f"📝 카페 포스팅: {'성공' if cafe_success else '실패'}")
            print("="*80)
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
            return False
        except Exception as e:
            print(f"\n❌ 자동화 프로세스 실행 중 오류: {e}")
            return False
        finally:
            # 리소스 정리
            if self.scraper:
                self.scraper.close()
            print("🧹 리소스 정리 완료")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='완전한 블로거 마케팅 자동화 시스템')
    parser.add_argument('--keyword', required=True, help='검색 키워드 (예: "내돈내산 영양제")')
    parser.add_argument('--sheet-id', required=True, help='Google Sheets 문서 ID')
    parser.add_argument('--sheet-name', required=True, help='시트 이름')
    parser.add_argument('--product-name', required=True, help='마케팅할 제품명')
    parser.add_argument('--event-info', default='특별 할인 이벤트', help='이벤트 정보')
    parser.add_argument('--sender-name', default='마케팅팀', help='이메일 발신자명')
    
    args = parser.parse_args()
    
    # 자동화 시스템 실행
    automation = CompleteAutomationSystem()
    success = automation.run_complete_automation(
        keyword=args.keyword,
        sheet_id=args.sheet_id,
        sheet_name=args.sheet_name,
        product_name=args.product_name,
        event_info=args.event_info,
        sender_name=args.sender_name
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())