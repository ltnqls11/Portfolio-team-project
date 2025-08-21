#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from google_sheets_client import GoogleSheetsClient
from naver_blog_scraper import NaverBlogScraper


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='네이버 블로그 인플루언서 정보 수집 RPA')
    parser.add_argument('--keyword', required=True, help='검색 키워드 (예: "내돈내산 영양제")')
    parser.add_argument('--sheet-id', required=True, help='Google Sheets 문서 ID')
    parser.add_argument('--sheet-name', required=True, help='시트 이름')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("네이버 블로그 인플루언서 정보 수집 RPA 시작")
    print("=" * 60)
    print(f"검색 키워드: {args.keyword}")
    print(f"Google Sheets ID: {args.sheet_id}")
    print(f"시트 이름: {args.sheet_name}")
    print()
    
    # Google Sheets 클라이언트 초기화
    try:
        print("1. Google Sheets API 연결 중...")
        sheets_client = GoogleSheetsClient()
        sheets_client.initialize_sheet_headers(args.sheet_id, args.sheet_name)
        print("✓ Google Sheets 연결 완료")
        print()
    except Exception as e:
        print(f"✗ Google Sheets 연결 실패: {e}")
        return 1
    
    # 네이버 블로그 스크래퍼 초기화
    scraper = None
    try:
        print("2. 웹 브라우저 실행 중...")
        scraper = NaverBlogScraper()
        print("✓ 브라우저 실행 완료")
        print()
        
        # 블로그 검색
        print("3. 네이버 블로그 검색 중...")
        if not scraper.search_blogs(args.keyword):
            print("✗ 블로그 검색 실패")
            return 1
        print("✓ 블로그 검색 완료")
        print()
        
        # 블로그 게시물 정보 추출
        print("4. 블로그 게시물 정보 추출 중...")
        blog_posts = scraper.extract_blog_posts()
        
        if not blog_posts:
            print("✗ 추출할 블로그 게시물이 없습니다.")
            return 1
        
        print(f"✓ {len(blog_posts)}개 블로그 게시물 정보 추출 완료")
        print()
        
        # 각 블로그에서 이메일 추출 및 데이터 저장
        print("5. 이메일 추출 및 데이터 저장 중...")
        successful_saves = 0
        
        for i, blog_info in enumerate(blog_posts, 1):
            try:
                print(f"[{i}/{len(blog_posts)}] {blog_info['blog_name']} 처리 중...")
                
                # 요구사항: 이메일 주소 탐색 (심층 추출)
                try:
                    email = scraper.extract_email_from_blog(blog_info['blog_url'])
                    blog_info['email'] = email
                except Exception as email_error:
                    # 요구사항: 특정 블로그에서 이메일 탐색에 실패하더라도 프로세스를 중단하지 않고 다음 블로그로 넘어간다
                    print(f"⚠️ {blog_info['blog_name']} 이메일 탐색 실패, 빈 값으로 저장: {email_error}")
                    blog_info['email'] = ""
                
                # 요구사항: 추출된 한 줄의 데이터(블로그명, 포스트URL, 블로그URL, 이메일)를 Google Sheets의 새로운 행에 추가한다
                row_data = [
                    blog_info['blog_name'],
                    blog_info['post_url'],
                    blog_info['blog_url'],
                    blog_info['email']
                ]
                
                sheets_client.append_row(args.sheet_id, args.sheet_name, row_data)
                successful_saves += 1
                
                print(f"✓ 저장 완료: {blog_info['blog_name']} (이메일: {blog_info['email'] or '없음'})")
                
            except Exception as e:
                # 요구사항: 예외 처리 - 프로세스를 중단하지 않고 다음으로 넘어간다
                print(f"✗ {blog_info['blog_name']} 전체 처리 중 오류, 건너뜀: {e}")
                continue
        
        print()
        print("=" * 60)
        print("작업 완료!")
        print(f"총 처리된 블로그: {len(blog_posts)}개")
        print(f"성공적으로 저장된 데이터: {successful_saves}개")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        return 1
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    sys.exit(main())