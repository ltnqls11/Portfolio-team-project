# chatbot.py
import streamlit as st
import openai # OpenAI 라이브러리 추가
import time
import os # os 라이브러리 추가
from dotenv import load_dotenv # python-dotenv 라이브러리에서 load_dotenv 함수를 불러옵니다.

def get_openai_response(prompt, api_key):
    """
    OpenAI API를 호출하여 응답을 받는 함수.
    """
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4.0-mini", # 사용하고 싶은 모델명으로 변경 가능합니다.
            messages=[
                {"role": "system", "content": "You are a helpful assistant specialized in providing information about VDT Syndrome and related health management for developers. Answer user questions concisely and informatively."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        return response
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        return None

def show_chatbot_page():
    """
    챗봇 페이지의 UI와 로직을 담당하는 함수.
    """
    st.title("🗣️ VDT 증후군 챗봇")
    st.markdown("VDT 증후군 관련해서 궁금한 점이 있다면 무엇이든 물어보세요!")
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # OpenAI API 키를 환경 변수에서 가져옵니다.
    api_key = os.getenv("OPENAI_API_KEY")
    
    # 🌟🌟🌟 아래 줄에 API 키를 직접 입력하세요. 🌟🌟🌟
    # api_key = "YOUR_API_KEY_HERE"  # 예시: api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # 🌟🌟🌟 위 줄의 주석(#)을 제거하고 YOUR_API_KEY_HERE 부분을 자신의 API 키로 바꾸세요. 🌟🌟🌟
    
    if not api_key:
        st.warning("OpenAI API 키가 .env 파일에 설정되지 않았거나 불러오는데 실패했습니다. 챗봇 기능이 비활성화됩니다.")
    else:
        # 대화 기록 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 사용자 입력 처리
        if prompt := st.chat_input("VDT 증후군에 대해 물어보세요"):
            # 사용자 메시지를 대화 기록에 추가하고 표시
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # OpenAI API 호출 및 응답 스트리밍
            with st.chat_message("assistant"):
                response = get_openai_response(prompt, api_key)
                if response:
                    placeholder = st.empty()
                    full_response = ""
                    for chunk in response:
                        if chunk.choices[0].delta.get("content"):
                            full_response += chunk.choices[0].delta["content"]
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                    
                    # 어시스턴트 메시지를 대화 기록에 추가
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    # .env 파일에서 환경 변수를 불러옵니다.
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))
    show_chatbot_page()

if __name__ == "__main__":
    main()
