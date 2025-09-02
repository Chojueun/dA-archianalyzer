
# init_dspy.py
import dspy
import os
import time
import random
from dotenv import load_dotenv
import anthropic
from anthropic import Anthropic

load_dotenv()

# Anthropic API 키 설정
anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
if not anthropic_api_key:
    print("💡 로컬 개발에서는 .streamlit/secrets.toml 파일을 사용하세요.")
    raise ValueError("ANTHROPIC_API_KEY를 설정해주세요.")

# Anthropic SDK 클라이언트 추가
anthropic_client = Anthropic(api_key=anthropic_api_key)

if not getattr(dspy.settings, "lm", None):
    try:
        lm = dspy.LM(
            "claude-sonnet-4-20250514",  # 더 강력한 모델로 업그레이드
            provider="anthropic",
            api_key=anthropic_api_key,
            max_tokens=8000  # 토큰 수 증가
        )
        dspy.configure(lm=lm, track_usage=True)
        print("✅ Claude Sonnet 4 모델이 성공적으로 설정되었습니다.")
    except Exception as e:
        print(f"❌ Claude 모델 설정 실패: {e}")
        raise

# 사용 가능한 Claude 모델들
available_models = [
    "claude-opus-4-1-20250805",    # 최신 Opus 4.1
    "claude-opus-4-20250514",      # Opus 4
    "claude-sonnet-4-20250514",    # Sonnet 4
    "claude-3-7-sonnet-20250219",  # Sonnet 3.7
]

def get_available_models_sdk():
    """Anthropic SDK로 사용 가능한 모델 조회 - 조건에 맞지 않는 모델 제외"""
    try:
        models = anthropic_client.models.list()
        
        # 모든 Claude 모델 가져오기
        claude_models = [model.id for model in models if 'claude' in model.id]
        
        # 허용할 모델들만 명시적으로 정의
        allowed_models = [
            "claude-opus-4-1-20250805",
            "claude-opus-4-20250514", 
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-20250219",
        ]
        
        # 허용된 모델만 필터링
        filtered_models = []
        for model_id in claude_models:
            if model_id in allowed_models:
                filtered_models.append(model_id)
        
        # 날짜순으로 정렬 (최신 버전 우선)
        filtered_models.sort(reverse=True)
        
        print(f"✅ SDK에서 {len(filtered_models)}개 모델 조회됨 (허용된 모델만)")
        return filtered_models
        
    except Exception as e:
        print(f"⚠️ SDK 모델 목록 조회 실패: {e}")
        # 폴백: 기본 모델 목록
        fallback_models = [
            "claude-opus-4-1-20250805",
            "claude-opus-4-20250514", 
            "claude-sonnet-4-20250514",
            "claude-3-7-sonnet-20250219",
        ]
        return fallback_models

def debug_model_filtering():
    """모델 필터링 디버깅용 함수"""
    try:
        models = anthropic_client.models.list()
        claude_models = [model.id for model in models if 'claude' in model.id]
        
        print("🔍 모든 Claude 모델:")
        for model in claude_models:
            print(f"  - {model}")
        
        print("\n🔍 필터링 후 모델:")
        filtered = get_available_models_sdk()
        for model in filtered:
            print(f"  - {model}")
            
    except Exception as e:
        print(f"❌ 디버깅 실패: {e}")

def execute_with_sdk_with_retry(prompt: str, model: str = None, max_retries: int = 3):
    """Anthropic SDK로 직접 실행 - 재시도 로직 포함"""
    if model is None:
        model = "claude-sonnet-4-20250514"  # 기본 모델을 Sonnet 4로 변경
    
    # 모델별 max_tokens 설정
    model_max_tokens = {
        "claude-3-7-sonnet-20250219": 8192,      # 최대 8192 토큰
        "claude-sonnet-4-20250514": 12000,       # 최대 12000 토큰
        "claude-opus-4-20250514": 12000,         # 최대 12000 토큰
        "claude-opus-4-1-20250805": 12000        # 최대 12000 토큰
    }
    
    # 선택된 모델의 max_tokens 가져오기
    max_tokens = model_max_tokens.get(model, 8192)  # 기본값 8192
    
    for attempt in range(max_retries):
        try:
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,  # 모델별 적절한 토큰 수 사용
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        except anthropic.RateLimitError:
            wait_time = (2 ** attempt) + random.uniform(0, 1)  # 지수 백오프
            print(f"⚠️ Rate limit 도달. {wait_time:.1f}초 후 재시도... (시도 {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
            
        except anthropic.APIError as e:
            if "overloaded_error" in str(e) or "Overloaded" in str(e):
                wait_time = (3 ** attempt) + random.uniform(1, 3)  # 과부하 시 더 긴 대기
                print(f"⚠️ API 과부하. {wait_time:.1f}초 후 재시도... (시도 {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                return f"❌ API 오류: {e}"
                
        except Exception as e:
            if attempt == max_retries - 1:  # 마지막 시도
                return f"❌ 오류: {e}"
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"⚠️ 일반 오류. {wait_time:.1f}초 후 재시도... (시도 {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    return "❌ 최대 재시도 횟수 초과. 잠시 후 다시 시도해주세요."

def execute_with_sdk(prompt: str, model: str = None):
    """Anthropic SDK로 직접 실행 - 기존 함수 호환성 유지"""
    return execute_with_sdk_with_retry(prompt, model, max_retries=3)

def get_optimal_model(task_type: str) -> str:
    """작업 유형에 따른 최적 모델 선택"""
    model_mapping = {
        "detailed_analysis": "claude-sonnet-4-20250514",  # 상세 분석
        "complex_analysis": "claude-opus-4-1-20250805",   # 복잡한 분석
        "cost_sensitive": "claude-3-5-sonnet-20241022",   # 비용 민감
        "narrative_generation": "claude-sonnet-4-20250514"  # Narrative 생성 전용
    }
    return model_mapping.get(task_type, "claude-sonnet-4-20250514")  # 기본값을 Sonnet 4로 변경

def configure_model(model_name: str):
    """모델 동적 변경 - 스레드 안전 버전"""
    if model_name not in available_models:
        raise ValueError(f"지원하지 않는 모델: {model_name}")
    
    # 모델별 max_tokens 설정
    model_max_tokens = {
        "claude-3-7-sonnet-20250219": 8192,      # 최대 8192 토큰
        "claude-sonnet-4-20250514": 12000,       # 최대 12000 토큰
        "claude-opus-4-20250514": 12000,         # 최대 12000 토큰
        "claude-opus-4-1-20250805": 12000        # 최대 12000 토큰
    }
    
    # 선택된 모델의 max_tokens 가져오기
    max_tokens = model_max_tokens.get(model_name, 8192)  # 기본값 8192
    
    try:
        # 기존 설정 제거
        if hasattr(dspy.settings, "lm"):
            delattr(dspy.settings, "lm")
        
        # 새 모델 설정
        lm = dspy.LM(
            model_name,
            provider="anthropic",
            api_key=anthropic_api_key,
            max_tokens=max_tokens  # 모델별 적절한 토큰 수 사용
        )
        dspy.configure(lm=lm, track_usage=True)
        print(f"✅ 모델이 {model_name}로 변경되었습니다. (max_tokens: {max_tokens})")
    except Exception as e:
        print(f"❌ 모델 변경 실패: {e}")
        # 기본 모델로 복구
        try:
            lm = dspy.LM(
                "claude-sonnet-4-20250514",  # 기본 모델을 Sonnet 4로 변경
                provider="anthropic",
                api_key=anthropic_api_key,
                max_tokens=12000
            )
            dspy.configure(lm=lm, track_usage=True)
        except:
            pass
        raise

def run_analysis_with_optimal_model(task_type: str, prompt: str, signature_class=None):
    """작업 유형에 따른 최적 모델로 분석 실행"""
    optimal_model = get_optimal_model(task_type)
    
    # 모델 변경
    configure_model(optimal_model)
    
    # 분석 실행 (기본값 또는 지정된 Signature 사용)
    if signature_class is None:
        # 순환 import 방지를 위해 동적 import
        try:
            from agent_executor import RequirementTableSignature
            signature_class = RequirementTableSignature
        except ImportError:
            # Signature 클래스가 없으면 기본 DSPy Predict 사용
            result = dspy.Predict()(input=prompt)
            return result
    
    result = dspy.Predict(signature_class)(input=prompt)
    return result

# 모델 정보 제공 함수
def get_model_info():
    """모델별 정보 반환"""
    return {
        "claude-opus-4-1-20250805": {
            "name": "Claude Opus 4.1",
            "speed": "보통",
            "power": "매우 높음",
            "cost": "높음",
            "best_for": "최고 수준의 복잡한 분석"
        },
        "claude-opus-4-20250514": {
            "name": "Claude Opus 4",
            "speed": "보통",
            "power": "매우 높음", 
            "cost": "높음",
            "best_for": "복잡한 분석"
        },
        "claude-sonnet-4-20250514": {
            "name": "Claude Sonnet 4",
            "speed": "빠름",
            "power": "높음",
            "cost": "보통",
            "best_for": "일반적인 분석 및 Narrative 생성"
        },
        "claude-3-7-sonnet-20250219": {
            "name": "Claude 3.7 Sonnet",
            "speed": "빠름",
            "power": "높음",
            "cost": "보통",
            "best_for": "균형잡힌 분석"
        }
    }

# Narrative 전용 모델 선택 함수 추가
def get_narrative_optimal_model():
    """Narrative 생성에 최적화된 모델 선택"""
    return "claude-sonnet-4-20250514"  # Narrative 생성에 최적화된 모델
