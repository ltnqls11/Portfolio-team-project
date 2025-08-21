import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from config import (
    NAVER_SEARCH_BASE_URL, 
    BLOG_TAB_SELECTOR, 
    EMAIL_PATTERN, 
    BROWSER_TIMEOUT, 
    PAGE_LOAD_DELAY
)


class NaverBlogScraper:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, BROWSER_TIMEOUT)
    
    def search_blogs(self, keyword):
        """네이버 블로그 검색"""
        try:
            # 네이버 검색 페이지로 이동 (요구사항: where=view와 query 파라미터 사용)
            search_url = f"{NAVER_SEARCH_BASE_URL}?where=view&query={keyword}"
            print(f"검색 URL: {search_url}")
            self.driver.get(search_url)
            time.sleep(PAGE_LOAD_DELAY)
            
            # 블로그 탭 클릭
            try:
                blog_tab = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, BLOG_TAB_SELECTOR))
                )
                blog_tab.click()
                time.sleep(PAGE_LOAD_DELAY)
                print("블로그 탭 클릭 완료")
            except TimeoutException:
                print("블로그 탭을 찾을 수 없습니다. 다른 선택자를 시도합니다.")
                # 대안 선택자들
                alternative_selectors = [
                    "a[href*='blog']",
                    ".tab_menu a:contains('블로그')",
                    "#lnb a[data-area='blog']"
                ]
                
                for selector in alternative_selectors:
                    try:
                        blog_tab = self.driver.find_element(By.CSS_SELECTOR, selector)
                        blog_tab.click()
                        time.sleep(PAGE_LOAD_DELAY)
                        print(f"대안 선택자로 블로그 탭 클릭: {selector}")
                        break
                    except NoSuchElementException:
                        continue
            
            return True
            
        except Exception as e:
            print(f"블로그 검색 중 오류 발생: {e}")
            return False
    
    def extract_blog_posts(self):
        """블로그 게시물 정보 추출"""
        blog_posts = []
        
        try:
            # 블로그 게시물 목록 찾기
            post_selectors = [
                ".lst_total .bx",
                ".api_subject_bx",
                ".total_wrap .bx",
                ".blog_lst .bx"
            ]
            
            posts = []
            for selector in post_selectors:
                try:
                    posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if posts:
                        print(f"게시물 {len(posts)}개 발견 (선택자: {selector})")
                        break
                except:
                    continue
            
            if not posts:
                print("블로그 게시물을 찾을 수 없습니다.")
                return blog_posts
            
            # 요구사항: 검색 결과 첫 페이지에 나타나는 모든 블로그 게시물 목록을 순회
            print(f"첫 페이지에서 총 {len(posts)}개의 게시물을 발견했습니다.")
            
            for i, post in enumerate(posts):  # 첫 페이지의 모든 게시물 처리
                try:
                    blog_info = self.extract_post_info(post)
                    if blog_info:
                        blog_posts.append(blog_info)
                        print(f"게시물 {i+1}/{len(posts)} 정보 추출 완료: {blog_info['blog_name']}")
                    else:
                        # 요구사항: 순회 중인 항목이 블로그 게시물이 아닌 경우(예: 광고), 오류를 발생시키지 않고 건너뛴다
                        print(f"게시물 {i+1}/{len(posts)} 건너뜀 (블로그 게시물이 아니거나 광고)")
                    
                except Exception as e:
                    # 요구사항: 예외 처리 - 오류를 발생시키지 않고 건너뛴다
                    print(f"게시물 {i+1}/{len(posts)} 처리 중 오류 발생, 건너뜀: {e}")
                    continue
            
        except Exception as e:
            print(f"게시물 목록 추출 중 오류: {e}")
        
        return blog_posts
    
    def extract_post_info(self, post_element):
        """개별 게시물 정보 추출"""
        try:
            # 포스트 URL 추출
            post_url = ""
            title_selectors = ["a.title_link", ".title a", "a[href*='blog']"]
            
            for selector in title_selectors:
                try:
                    title_link = post_element.find_element(By.CSS_SELECTOR, selector)
                    post_url = title_link.get_attribute('href')
                    if post_url:
                        break
                except:
                    continue
            
            # 블로그명과 블로그 URL 추출
            blog_name = ""
            blog_url = ""
            blog_selectors = [".sub_txt a", ".blog_name a", ".source a"]
            
            for selector in blog_selectors:
                try:
                    blog_link = post_element.find_element(By.CSS_SELECTOR, selector)
                    blog_name = blog_link.text.strip()
                    blog_url = blog_link.get_attribute('href')
                    if blog_name and blog_url:
                        break
                except:
                    continue
            
            if not all([post_url, blog_name, blog_url]):
                return None
            
            return {
                'blog_name': blog_name,
                'post_url': post_url,
                'blog_url': blog_url,
                'email': ''  # 이메일은 별도로 추출
            }
            
        except Exception as e:
            print(f"게시물 정보 추출 중 오류: {e}")
            return None
    
    def extract_email_from_blog(self, blog_url):
        """
        요구사항: 위 단계에서 추출한 '블로그 URL'로 직접 이동한다.
        해당 블로그의 메인 페이지 또는 프로필 영역(위젯 등)에서 이메일 주소를 탐색한다.
        """
        try:
            print(f"블로그 URL로 직접 이동하여 이메일 탐색 중: {blog_url}")
            self.driver.get(blog_url)
            time.sleep(PAGE_LOAD_DELAY)
            
            # 요구사항: 페이지 전체 HTML 소스에서 이메일 정규식과 일치하는 패턴을 찾는다
            page_source = self.driver.page_source
            emails = re.findall(EMAIL_PATTERN, page_source)
            
            if emails:
                print(f"발견된 이메일 패턴들: {emails}")
                
                # 중복 제거 및 일반적이지 않은 이메일 필터링
                unique_emails = list(set(emails))
                filtered_emails = [
                    email for email in unique_emails 
                    if not any(domain in email.lower() for domain in [
                        'naver.com', 'example.com', 'test.com', 'sample.com',
                        'domain.com', 'email.com', 'mail.com'
                    ])
                ]
                
                if filtered_emails:
                    selected_email = filtered_emails[0]
                    print(f"✅ 이메일 발견: {selected_email}")
                    return selected_email
                else:
                    print("⚠️ 유효한 이메일을 찾을 수 없음 (필터링됨)")
            
            print("❌ 이메일을 찾을 수 없습니다.")
            return ""
            
        except Exception as e:
            print(f"❌ 이메일 추출 중 오류: {e}")
            return ""
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()