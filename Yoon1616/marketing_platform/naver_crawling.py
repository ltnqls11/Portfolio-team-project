"""
네이버 블로그 검색 API 기반 후보 수집 유틸
- 함수형으로 리팩터링하여 외부에서 재사용 가능
- 기본적으로 환경변수 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 사용
"""

import os
import time
from typing import Dict, List

import requests
import pandas as pd
from bs4 import BeautifulSoup


NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID", "")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "")
NAVER_BLOG_SEARCH_URL = "https://openapi.naver.com/v1/search/blog.json"


def _naver_headers() -> Dict[str, str]:
    return {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }


def search_naver_blogs(query: str, total: int = 50, delay_sec: float = 0.5) -> List[Dict]:
    """
    네이버 블로그 검색 API로 게시글 메타 수집
    - total: 수집할 게시글 수(최대 1000, 10단위 페이지네이션)
    반환: [{title, link, blogger, postdate}]
    """
    items: List[Dict] = []
    fetched = 0
    start = 1
    while fetched < total and start <= 1000:
        display = min(10, total - fetched)
        params = {"query": query, "display": display, "start": start, "sort": "date"}
        res = requests.get(NAVER_BLOG_SEARCH_URL, headers=_naver_headers(), params=params, timeout=15)
        data = res.json() if res.ok else {"items": []}
        for it in data.get("items", []):
            items.append({
                "title": it.get("title", ""),
                "link": it.get("link", ""),
                "blogger": it.get("bloggername", ""),
                "postdate": it.get("postdate", "")
            })
            fetched += 1
            if fetched >= total:
                break
        start += 10
        time.sleep(delay_sec)
    return items


def get_blog_metrics(link: str) -> Dict[str, int]:
    """개별 블로그 글에서 공감/댓글 수를 추정"""
    try:
        res = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")
        likes_el = soup.select_one(".u_likeit_list_count._count")
        comments_el = soup.select_one(".area_comment .num")
        likes = int(likes_el.text.strip()) if likes_el and likes_el.text.strip().isdigit() else 0
        # 댓글 수 표기가 숫자가 아닐 수 있어 숫자만 추출
        ctext = (comments_el.text if comments_el else "").strip()
        cnum = "".join([ch for ch in ctext if ch.isdigit()])
        comments = int(cnum) if cnum else 0
        return {"likes": likes, "comments": comments}
    except Exception:
        return {"likes": 0, "comments": 0}


def collect_blogger_candidates(query: str, total: int = 50, delay_sec: float = 0.5) -> List[Dict]:
    """
    검색 → 메트릭 보강 → 후보 리스트 반환
    반환: [{title, link, blogger, postdate, likes, comments, engagement}]
    """
    base = search_naver_blogs(query=query, total=total, delay_sec=delay_sec)
    enriched: List[Dict] = []
    for it in base:
        metrics = get_blog_metrics(it.get("link", ""))
        row = {
            **it,
            **metrics,
        }
        row["engagement"] = (row.get("likes", 0) or 0) + (row.get("comments", 0) or 0)
        enriched.append(row)
        time.sleep(delay_sec)
    return enriched


if __name__ == "__main__":
    # 예시 실행: 쿼리와 결과 저장
    q = os.environ.get("NAVER_QUERY", "립스틱 후기")
    blogs = collect_blogger_candidates(q, total=50)
    df = pd.DataFrame(blogs)
    out = f"{q}_blogs.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"✅ 완료! {out} 파일로 저장되었습니다.")
