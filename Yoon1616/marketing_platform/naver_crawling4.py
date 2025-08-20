import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import re, time, random

# ==============================
# 설정
# ==============================
CLIENT_ID = ""      # ← 교체 필수
CLIENT_SECRET = ""  # ← 교체 필수
QUERIES = [
    "립스틱 후기", "립스틱 리뷰", "매트 립 후기",
    "틴트 후기", "립 메이크업"
]
RESULTS_PER_QUERY = 50   # 쿼리당 최대 100까지 추천 (10단위)
SORT = "sim"             # 유사도순(sim) 권장
HEADERS_API = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
HEADERS_WEB = {"User-Agent": "Mozilla/5.0"}

# 랭킹/필터 파라미터
RECENT_DAYS_WINDOW = 90     # 최근 90일 가중치·빈도 계산
RECENT_DAYS_FILTER = 60     # 최종 추천 시 "최근 글 있음" 기준
TOP_K_BLOGGERS = 10         # 최종 추천 블로거 수
SLEEP_API = (0.2, 0.5)      # API 호출 간 랜덤 지연
SLEEP_WEB = (0.2, 0.6)      # 웹 크롤링 간 랜덤 지연

# ==============================
# 유틸
# ==============================
def jitter_sleep(a, b):
    time.sleep(random.uniform(a, b))

def only_digits(s: str) -> int:
    if not s:
        return 0
    digs = re.sub(r"[^\d]", "", s)
    return int(digs) if digs else 0

def to_mobile_url(link: str) -> str:
    """
    네이버 블로그는 모바일 페이지가 정적 HTML로 더 많은 정보를 노출하는 경우가 많음.
    가능한 경우 m.blog.naver.com 형식으로 변환.
    """
    if "m.blog.naver.com" in link:
        return link
    # 패턴 1: ...PostView.naver?blogId=xxx&logNo=yyy
    m = re.search(r"blogId=([^&]+).*?logNo=([^&]+)", link)
    if m:
        blogId, logNo = m.group(1), m.group(2)
        return f"https://m.blog.naver.com/{blogId}/{logNo}"
    # 패턴 2: blog.naver.com/{blogId}/{logNo}
    m2 = re.search(r"blog\.naver\.com/([^/?]+)/(\d+)", link)
    if m2:
        blogId, logNo = m2.group(1), m2.group(2)
        return f"https://m.blog.naver.com/{blogId}/{logNo}"
    # 그 외는 그대로 사용
    return link

def extract_blog_id(bloggerlink: str, link: str) -> str:
    # bloggerlink 우선
    m = re.search(r"blog\.naver\.com/([^/?#]+)", str(bloggerlink))
    if m:
        return m.group(1)
    # 링크에서 추출
    m2 = re.search(r"blogId=([^&]+)", link)
    if m2:
        return m2.group(1)
    m3 = re.search(r"blog\.naver\.com/([^/?#]+)", link)
    if m3:
        return m3.group(1)
    return ""  # 식별 불가 시 공백

def parse_like_comment_from_soup(soup: BeautifulSoup):
    """
    네이버 블로그 DOM이 케이스마다 달라서 다중 후보 셀렉터 사용.
    없으면 0으로.
    """
    # 좋아요(공감)
    like_candidates = [
        ".u_likeit_list_count._count",
        "span.u_likeit_list_count._count",
        "em.u_cnt._count",
        "span._count",  # 모바일 변형
    ]
    likes = 0
    for sel in like_candidates:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            likes = only_digits(el.get_text())
            if likes:
                break

    # 댓글
    comment_candidates = [
        "#commentCount", "em#commentCount", "span#commentCount",
        "span.u_cbox_count", "em.u_cbox_count",
        "a#floatingBottomCmtCount", "em#floatingBottomCmtCount",
        "span._count"  # 일부 케이스
    ]
    comments = 0
    for sel in comment_candidates:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            comments = only_digits(el.get_text())
            if comments:
                break

    # 텍스트에서 '댓글 123' 패턴 보정
    if comments == 0:
        txt = soup.get_text(" ", strip=True)
        m = re.search(r"댓글\s*([0-9,]+)", txt)
        if m:
            comments = only_digits(m.group(1))

    return likes, comments

# ==============================
# 1) 검색 API로 포스트 수집
# ==============================
def fetch_posts():
    posts = []
    seen_links = set()
    for q in QUERIES:
        # start: 1,11,21,... ; display=10 고정
        pages = max(1, RESULTS_PER_QUERY // 10)
        for i in range(pages):
            start = 1 + i*10
            params = {"query": q, "display": 10, "start": start, "sort": SORT}
            r = requests.get("https://openapi.naver.com/v1/search/blog.json",
                             headers=HEADERS_API, params=params, timeout=8)
            if r.status_code != 200:
                print(f"[API 실패] {q} / start={start} status={r.status_code}")
                jitter_sleep(*SLEEP_API); continue
            data = r.json()
            for it in data.get("items", []):
                link = it.get("link", "")
                if not link or link in seen_links:
                    continue
                seen_links.add(link)
                posts.append({
                    "query": q,
                    "title": re.sub(r"<.*?>", "", it.get("title", "")),
                    "link": link,
                    "blogger": it.get("bloggername", ""),
                    "bloggerlink": it.get("bloggerlink", ""),
                    "postdate": it.get("postdate", ""),
                    "description": re.sub(r"<.*?>", "", it.get("description", "")),
                })
            jitter_sleep(*SLEEP_API)
    return posts

# ==============================
# 2) 각 포스트 크롤링하여 공감/댓글 수 수집
# ==============================
def enrich_with_engagement(rows):
    out = []
    for row in rows:
        link = row["link"]
        mlink = to_mobile_url(link)
        likes, comments = 0, 0
        try:
            resp = requests.get(mlink, headers=HEADERS_WEB, timeout=8)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                likes, comments = parse_like_comment_from_soup(soup)
        except Exception:
            pass
        row2 = dict(row)
        row2["likes"] = int(likes)
        row2["comments"] = int(comments)
        row2["engagement"] = row2["likes"] + row2["comments"]
        out.append(row2)
        jitter_sleep(*SLEEP_WEB)
    return out

# ==============================
# 3) 블로거 레벨 집계 → 고참여 블로거 선별
# ==============================
def rank_bloggers(df_posts):
    # 날짜 처리
    today = datetime.today()
    df_posts["date"] = pd.to_datetime(df_posts["postdate"], format="%Y%m%d", errors="coerce")
    df_posts["days_since"] = (today - df_posts["date"]).dt.days

    # 블로그 ID 추출(중복 닉네임 방지)
    df_posts["blog_id"] = df_posts.apply(
        lambda r: extract_blog_id(r.get("bloggerlink",""), r.get("link","")), axis=1
    )
    df_posts["blog_id"] = df_posts["blog_id"].fillna("")

    # 최근 창 (RECENT_DAYS_WINDOW) 내 글 수
    recent_mask = df_posts["days_since"] <= RECENT_DAYS_WINDOW
    grp = df_posts.groupby("blog_id", as_index=False).agg(
        blogger=("blogger", "first"),
        bloggerlink=("bloggerlink", "first"),
        posts_total=("link", "count"),
        median_engagement=("engagement", "median"),
        mean_engagement=("engagement", "mean"),
        latest_date=("date", "max"),
        min_days_since=("days_since", "min"),
        posts_last_window=("days_since", lambda s: (s <= RECENT_DAYS_WINDOW).sum())
    )

    # 점수화 (블로거 레벨)
    def safe_scale(series):
        if series.nunique() <= 1:
            return pd.Series([1.0]*len(series), index=series.index)
        return pd.Series(MinMaxScaler().fit_transform(series.to_frame()).ravel(), index=series.index)

    s_eng = safe_scale(grp["median_engagement"])   # 참여 중심: 중앙값이 튀는 값에 강함
    s_freq = safe_scale(grp["posts_last_window"])  # 최근 글 빈도
    # 최신성: days_since 작을수록 좋음 → 역스케일
    s_rec_raw = safe_scale(-grp["min_days_since"].fillna(9999))

    grp["score"] = 0.6*s_eng + 0.25*s_freq + 0.15*s_rec_raw

    # 최근 글 보유 필터(RECENT_DAYS_FILTER 이내에 최소 1건)
    has_recent = grp["min_days_since"] <= RECENT_DAYS_FILTER
    grp_ranked = grp[has_recent].sort_values("score", ascending=False).head(TOP_K_BLOGGERS).reset_index(drop=True)

    return grp_ranked, df_posts

# ==============================
# 4) 최종: 상위 블로거의 "최신 포스트" 추천 목록 생성
# ==============================
def pick_latest_posts_for_top_bloggers(grp_ranked, df_posts):
    results = []
    for _, r in grp_ranked.iterrows():
        bid = r["blog_id"]
        # 해당 블로거의 포스트 중 가장 최근(RECENT_DAYS_FILTER 이내 우선)
        cand = df_posts[df_posts["blog_id"] == bid].copy()
        cand = cand.sort_values(["date", "engagement"], ascending=[False, False])

        # RECENT_DAYS_FILTER 이내가 있으면 그 중 최상위, 없으면 전체 중 최상위
        in_filter = cand[cand["days_since"] <= RECENT_DAYS_FILTER]
        pick = in_filter.iloc[0] if not in_filter.empty else cand.iloc[0]

        results.append({
            "blog_id": bid,
            "blogger": r["blogger"],
            "bloggerlink": r["bloggerlink"],
            "latest_post_title": pick["title"],
            "latest_post_link": pick["link"],
            "latest_post_date": pick["date"].strftime("%Y-%m-%d") if pd.notnull(pick["date"]) else "",
            "latest_post_engagement": int(pick["engagement"]),
            "median_engagement": int(r["median_engagement"]) if pd.notnull(r["median_engagement"]) else 0,
            "posts_last_90d": int(r["posts_last_window"]),
            "score": round(float(r["score"]), 4),
        })
    return pd.DataFrame(results)

# ==============================
# 메인 실행
# ==============================
if __name__ == "__main__":
    print("1) 검색 API로 포스트 수집 중...")
    posts = fetch_posts()
    if not posts:
        raise SystemExit("검색 결과가 없습니다. 쿼리/정렬/페이지 수를 늘려보세요.")

    df_raw = pd.DataFrame(posts)
    df_raw.to_csv("raw_posts.csv", index=False, encoding="utf-8-sig")
    print(f" - 수집 포스트 수: {len(df_raw)}  (raw_posts.csv 저장)")

    print("\n2) 포스트별 공감/댓글 수 크롤링 중...")
    enriched = enrich_with_engagement(posts)
    df = pd.DataFrame(enriched)
    df["engagement"] = df["engagement"].fillna(0).astype(int)
    df.to_csv("raw_posts_with_engagement.csv", index=False, encoding="utf-8-sig")
    print(f" - 크롤링 완료 (raw_posts_with_engagement.csv 저장)")

    print("\n3) 블로거 레벨로 고참여 선별 및 점수화...")
    top_bloggers, df_posts = rank_bloggers(df)
    if top_bloggers.empty:
        print("⚠️ 최근 글(필터 기준) 보유한 고참여 블로거가 없습니다. RECENT_DAYS_FILTER/QUERIES를 조정하세요.")
        # 필터 없이 점수순 상위 출력(참고용)
        fallback, _ = rank_bloggers(df)  # 같은 함수지만 필터 때문에 empty이면 아래 참고만 출력
    else:
        print(f" - 추천 블로거 수: {len(top_bloggers)}")
        print(top_bloggers[["blogger", "blog_id", "median_engagement", "posts_last_window", "score"]])

        print("\n4) 추천 블로거의 최신 포스트 선정...")
        picks = pick_latest_posts_for_top_bloggers(top_bloggers, df_posts)
        picks.to_csv("top_bloggers_recent_posts.csv", index=False, encoding="utf-8-sig")
        print("✅ top_bloggers_recent_posts.csv 저장 완료!")
        print(picks[["blogger","latest_post_title","latest_post_date","latest_post_engagement","score","latest_post_link"]])
