import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="AI 뉴스 요약기", page_icon="📰", layout="wide")

st.title("📰 AI 실시간 뉴스 요약 & CSV 추출기")
st.markdown("비전공자도 쉽게 사용하는 뉴스 수집 도구입니다.")

# 사이드바 설정
with st.sidebar:
    st.header("1. 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    st.info("[API 키 발급받기](https://aistudio.google.com/app/apikey)")
    st.markdown("---")
    st.write("제작: 세계 최고의 앱 개발자")

# 메인 화면
keyword = st.text_input("2. 어떤 뉴스를 찾을까요?", placeholder="예: 엔비디아 주가, 한국 축구 결과")

if st.button("뉴스 검색 및 요약 시작"):
    if not api_key:
        st.error("오른쪽 사이드바에 API 키를 입력해주세요!")
    elif not keyword:
        st.warning("검색할 키워드를 입력해주세요!")
    else:
        try:
            # Gemini 설정 (구글 검색 기능 포함)
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash-8b",
                tools=[{"google_search_retrieval": {}}]
            )
            

            with st.spinner('AI가 실시간 뉴스를 검색하고 요약 중입니다...'):
                prompt = f"'{keyword}'와 관련된 가장 최신 뉴스 기사 5개를 찾아줘. 각 기사의 제목, 원본 URL, 2줄 핵심 요약을 알려줘. 기사 사이에는 반드시 '---'를 넣어서 구분해줘."

                response = model.generate_content(prompt)

                # 결과 텍스트 처리 및 데이터프레임 변환
                raw_text = response.text
                items = raw_text.split("---")

                news_list = []
                for item in items:
                    if "제목" in item and "URL" in item:
                        # 텍스트에서 정보 추출 (간이 파싱)
                        lines = [line.strip() for line in item.strip().split('\n') if line.strip()]
                        title = next((l for l in lines if "제목" in l), "제목 없음").split(":", 1)[-1].strip()
                        url = next((l for l in lines if "URL" in l or "http" in l), "URL 없음").split(":", 1)[-1].strip()
                        summary = next((l for l in lines if "요약" in l), "요약 없음").split(":", 1)[-1].strip()
                        news_list.append({"제목": title, "URL": url, "요약내용": summary})

                df = pd.DataFrame(news_list).head(5)

                if not df.empty:
                    st.success(f"'{keyword}'에 대한 최신 뉴스 5개를 찾았습니다!")

                    # 화면 표시
                    for i, row in df.iterrows():
                        with st.expander(f"{i+1}. {row['제목']}"):
                            st.write(f"🔗 [기사 원문 보기]({row['URL']})")
                            st.write(f"📝 **요약**: {row['요약내용']}")

                    # CSV 다운로드 버튼
                    csv = df.to_csv(index=False, encoding='utf-8-sig') # 한글 깨짐 방지
                    st.download_button(
                        label="📥 결과 CSV 파일로 다운로드",
                        data=csv,
                        file_name=f"news_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv",
                    )
                else:
                    st.write("검색 결과가 없습니다. 다시 시도해보세요.")
                    st.write(raw_text) # 파싱 실패 시 원문 출력

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
