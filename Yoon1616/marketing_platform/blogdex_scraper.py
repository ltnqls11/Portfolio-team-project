import requests
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class BloggerCandidate(dict):
    @property
    def name(self) -> str:
        return self.get("name", "")

    @property
    def url(self) -> str:
        return self.get("url", "")

    @property
    def category(self) -> str:
        return self.get("category", "")

    @property
    def reach(self) -> Optional[float]:
        return self.get("reach")

    @property
    def engagement(self) -> Optional[float]:
        return self.get("engagement")

    @property
    def last_posted_at(self) -> Optional[str]:
        return self.get("last_posted_at")


def _safe_float(text: str) -> Optional[float]:
    try:
        return float(text.replace(",", "").replace("%", "").strip())
    except Exception:
        return None


def scrape_blogdex(category_keyword: str, max_pages: int = 3, delay_sec: float = 1.0) -> List[BloggerCandidate]:
    """
    비공식 스크래핑: blogdex.space의 카테고리 검색 결과에서 후보 추정치 추출
    동적 로딩/차단 가능성으로 실패할 수 있음 → 실패 시 빈 리스트 반환
    """
    base = "https://blogdex.space/search"
    results: List[BloggerCandidate] = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    }

    for page in range(1, max_pages + 1):
        try:
            params = {"q": category_keyword, "page": page}
            resp = requests.get(base, params=params, headers=headers, timeout=15)
            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.select(".blog-card, .result-card, .card")
            if not cards:
                # 구조 변경 가능성. 최소한의 셀렉터로도 안 잡히면 중단
                break

            for el in cards:
                name = (el.select_one(".title, .name, h3") or {}).get_text(strip=True) if hasattr(el.select_one(".title, .name, h3"), 'get_text') else ""
                url_el = el.select_one("a[href]")
                url = url_el["href"].strip() if url_el else ""
                meta_text = " ".join([t.get_text(" ", strip=True) for t in el.select(".meta, .stats, .desc, p")])

                reach = _safe_float(meta_text) if "%" not in meta_text else None
                engagement = _safe_float(meta_text.split("%")[0] + "%") if "%" in meta_text else None

                candidate = BloggerCandidate(
                    name=name,
                    url=url,
                    category=category_keyword,
                    reach=reach,
                    engagement=engagement,
                )
                results.append(candidate)
        except Exception:
            break
        finally:
            time.sleep(delay_sec)

    # 중복 제거(이름+URL 기준)
    uniq: Dict[str, BloggerCandidate] = {}
    for c in results:
        key = f"{c.get('name','')}|{c.get('url','')}"
        if key not in uniq:
            uniq[key] = c

    return list(uniq.values())


def score_candidates(candidates: List[BloggerCandidate], weight_reach: float = 0.5, weight_engagement: float = 0.5) -> List[BloggerCandidate]:
    """
    간단 가중치 스코어 = 표준화 없는 가중 평균(데모 목적) 
    """
    scored = []
    for c in candidates:
        reach = c.get("reach") or 0
        eng = c.get("engagement") or 0
        score = weight_reach * reach + weight_engagement * eng
        x = BloggerCandidate(**c)
        x["score"] = score
        scored.append(x)
    scored.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored

