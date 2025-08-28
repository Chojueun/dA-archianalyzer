# search_helper.py
import requests
import os
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1단계: Streamlit Secrets에서 가져오기 (우선순위)
SERP_API_KEY = st.secrets.get("SERP_API_KEY")

# 2단계: 환경 변수에서 가져오기 (로컬 개발용)
if not SERP_API_KEY:
    SERP_API_KEY = os.environ.get("SERP_API_KEY")

def search_web_serpapi(query):
    """웹 검색 함수 - 오류 처리 및 디버깅 강화"""
    
    # API 키 확인
    if not SERP_API_KEY:
        st.warning("⚠️ SERP_API_KEY가 설정되지 않았습니다.")
        return "[검색 API 키 없음]"
    
    try:
        params = {
            "q": query,
            "api_key": SERP_API_KEY,
            "engine": "google",
            "num": 3,
            "gl": "kr",  # 한국 지역 설정
            "hl": "ko"   # 한국어 결과
        }
        
        resp = requests.get("https://serpapi.com/search", params=params, timeout=10)
        
        # 응답 상태 확인
        if resp.status_code != 200:
            st.error(f"❌ SerpAPI 오류: {resp.status_code}")
            return f"[검색 API 오류: {resp.status_code}]"
        
        data = resp.json()
        
        # 오류 응답 확인
        if "error" in data:
            st.error(f"❌ SerpAPI 오류: {data['error']}")
            return f"[검색 API 오류: {data['error']}]"
        
        # 결과 처리
        if "organic_results" in data and data["organic_results"]:
            results = data["organic_results"]
            formatted_results = []
            for r in results:
                title = r.get('title', '제목 없음')
                snippet = r.get('snippet', '내용 없음')
                formatted_results.append(f"📄 {title}\n{snippet}")
            return "\n---\n".join(formatted_results)
        else:
            st.info("ℹ️ 검색 결과가 없습니다.")
            return "[검색 결과 없음]"
            
    except requests.exceptions.Timeout:
        st.error("❌ 검색 시간 초과")
        return "[검색 시간 초과]"
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 네트워크 오류: {e}")
        return f"[네트워크 오류: {e}]"
    except Exception as e:
        st.error(f"❌ 예상치 못한 오류: {e}")
        return f"[검색 오류: {e}]"