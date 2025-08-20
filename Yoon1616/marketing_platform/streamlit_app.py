import os
import json
import time
from datetime import datetime
from typing import List, Dict

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

try:
    # 패키지 실행 환경용
    from .blogdex_scraper import scrape_blogdex, score_candidates
    from .promo_generator import PromoRequest, generate_blogger_writing_kit
except Exception:  # streamlit 직접 실행 시 상대임포트 실패 가능
    from mini_project.marketing_platform.blogdex_scraper import scrape_blogdex, score_candidates
    from mini_project.marketing_platform.promo_generator import PromoRequest, generate_blogger_writing_kit


load_dotenv()


st.set_page_config(page_title="라인 마케팅 자동화", page_icon="🚀", layout="wide")


def section_inputs():
    st.sidebar.header("제품/캠페인 정보")
    product_name = st.sidebar.text_input("제품명", "라인 마케팅 플랫폼")
    category = st.sidebar.text_input("카테고리", "마케팅/생산성")
    usp = st.sidebar.text_area("USP/핵심 혜택", "한 번에 추천-카피-연락 자동화")
    target = st.sidebar.text_input("타겟", "스타트업/이커머스 마케터")
    tone = st.sidebar.selectbox("톤", ["전문적", "친근함", "젊고 캐주얼", "권위적"])
    keywords = st.sidebar.text_input("핵심 키워드(쉼표)", "AI, 자동화, n8n, 마케팅, 블로그")
    cta = st.sidebar.text_input("CTA", "지금 데모 신청")
    st.sidebar.markdown("---")
    min_reach = st.sidebar.number_input("최소 도달(추정)", 0.0, 1e9, 0.0)
    min_eng = st.sidebar.number_input("최소 참여율(%)", 0.0, 100.0, 0.0)
    return product_name, category, usp, target, tone, [x.strip() for x in keywords.split(',') if x.strip()], cta, min_reach, min_eng


def section_scrape_and_filter(category: str, min_reach: float, min_eng: float) -> pd.DataFrame:
    st.subheader("1) 블로거 추천")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.caption("blogdex.space/네이버 API에서 후보 추출을 시도합니다. 실패 시 CSV 업로드를 이용하세요.")
        if st.button("블로거 후보 수집 (Blogdex)", use_container_width=True):
            with st.spinner("수집 중"):
                candidates = scrape_blogdex(category)
                st.session_state["raw_candidates"] = candidates
                st.success(f"{len(candidates)}건 수집")

        if st.button("블로거 후보 수집 (네이버 API)", use_container_width=True):
            with st.spinner("네이버 API 수집 중"):
                try:
                    try:
                        from .naver_integration import recommend_bloggers_with_naver
                    except Exception:
                        from mini_project.marketing_platform.naver_integration import recommend_bloggers_with_naver
                    ndf = recommend_bloggers_with_naver(query=category, total=50)
                    st.session_state["raw_candidates"] = ndf.to_dict(orient="records")
                    st.success(f"{len(ndf)}건 수집")
                except Exception as e:
                    st.error(f"네이버 수집 실패: {e}")

        uploaded = st.file_uploader("대안: 후보 CSV 업로드(name,url,reach,engagement)", type=["csv"]) 
        if uploaded is not None:
            df = pd.read_csv(uploaded)
            st.session_state["raw_candidates"] = df.to_dict(orient="records")
            st.success(f"{len(df)}건 업로드")

    with col2:
        raw: List[Dict] = st.session_state.get("raw_candidates", [])
        if not raw:
            st.info("좌측에서 후보 수집/업로드 후 필터링하세요.")
            return pd.DataFrame()

        df = pd.DataFrame(raw)
        df["reach"] = pd.to_numeric(df.get("reach", 0), errors="coerce").fillna(0)
        df["engagement"] = pd.to_numeric(df.get("engagement", 0), errors="coerce").fillna(0)
        df = df[(df["reach"] >= min_reach) & (df["engagement"] >= min_eng)]
        scored = score_candidates(df.to_dict(orient="records"))
        sdf = pd.DataFrame(scored)
        st.dataframe(sdf, use_container_width=True)
        st.download_button("CSV 다운로드", sdf.to_csv(index=False), file_name=f"blogger_candidates_{datetime.now().strftime('%Y%m%d')}.csv")
        return sdf


def section_promo_generator(product_name, category, usp, target, tone, keywords, cta):
    st.subheader("2) 블로거용 '작성 틀' 생성 & 이메일 초안")
    if st.button("작성 틀 생성", use_container_width=True):
        with st.spinner("생성 중"):
            req = PromoRequest(
                product_name=product_name,
                category=category,
                usp=usp,
                target_audience=target,
                tone=tone,
                keywords=keywords,
                cta=cta,
            )
            out = generate_blogger_writing_kit(req)
            st.session_state["kit_md"] = out["kit_markdown"]
            st.session_state["email_subject"] = out["email_subject"]
            st.session_state["email_body"] = out["email_body"]

    md = st.session_state.get("kit_md")
    if md:
        st.markdown(md)
        with st.expander("이메일 초안 미리보기", expanded=True):
            st.text_input("제목", st.session_state.get("email_subject", ""))
            st.text_area("본문", st.session_state.get("email_body", ""), height=180)


def _post_to_n8n(items: List[Dict]) -> Dict:
    url = os.environ.get("N8N_OUTREACH_WEBHOOK_URL")
    if not url:
        raise RuntimeError("N8N_OUTREACH_WEBHOOK_URL 환경변수가 필요합니다")
    resp = requests.post(url, json=items, timeout=20)
    return {"status_code": resp.status_code, "text": resp.text}


def section_outreach(sdf: pd.DataFrame):
    st.subheader("3) 연락 자동화 (이메일 발송)")
    if sdf is None or sdf.empty:
        st.info("추천 목록이 비어있습니다")
        return

    st.caption("선택된 블로거에게 작성 틀(템플릿)과 안내 메일을 발송합니다.")
    selected = st.multiselect("연락 대상 선택(이름)", options=list(sdf["name"]) if "name" in sdf else [])
    subject = st.text_input("제목", st.session_state.get("email_subject", f"[{datetime.now().strftime('%m/%d')}] 협업 제안 - {st.session_state.get('product_name', '제품')}"))
    default_body = (st.session_state.get("email_body") or "안녕하세요. 협업 제안드립니다.") + "\n\n---\n아래는 블로그 글 작성 틀입니다:\n\n" + (st.session_state.get("kit_md") or "")
    body = st.text_area("본문", default_body, height=260)

    use_smtp = st.checkbox("SMTP로 직접 발송", value=True)
    n8n_url = os.environ.get("N8N_OUTREACH_WEBHOOK_URL")

    if st.button("발송", use_container_width=True):
        rows = sdf[sdf["name"].isin(selected)] if selected else sdf.head(3)
        if rows.empty:
            st.warning("선택된 대상이 없습니다")
            return

        successes, failures = 0, 0
        with st.spinner("발송 중"):
            for _, r in rows.iterrows():
                to_addr = r.get("email") or r.get("url") or ""
                if not to_addr:
                    failures += 1
                    continue
                try:
                    if use_smtp:
                        try:
                            from .mailer import send_email_via_smtp  # 지연 임포트
                        except Exception:
                            from mini_project.marketing_platform.mailer import send_email_via_smtp
                        send_email_via_smtp(to_addr, subject, body)
                    else:
                        if not n8n_url:
                            raise RuntimeError("N8N_OUTREACH_WEBHOOK_URL이 없습니다")
                        _post_to_n8n([{ "to": to_addr, "subject": subject, "message": body, "meta": {"name": r.get("name", "")}}])
                    successes += 1
                except Exception as e:
                    failures += 1
            st.success(f"발송 완료: 성공 {successes}건, 실패 {failures}건")


def main():
    product_name, category, usp, target, tone, keywords, cta, min_reach, min_eng = section_inputs()
    st.session_state['product_name'] = product_name

    sdf = section_scrape_and_filter(category, min_reach, min_eng)
    st.markdown("---")
    section_promo_generator(product_name, category, usp, target, tone, keywords, cta)
    st.markdown("---")
    section_outreach(sdf)


if __name__ == "__main__":
    main()

