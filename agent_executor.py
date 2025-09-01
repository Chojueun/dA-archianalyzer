# agent_executor.py
import dspy
from dspy import Module, Signature, InputField, OutputField
from dspy.teleprompt.bootstrap import BootstrapFewShot
from dspy.predict.react import ReAct
# 순환 import 방지를 위해 필요한 함수만 import
from init_dspy import execute_with_sdk, execute_with_sdk_with_retry, get_optimal_model
import time
import random

# --- 기존 Signature & ReAct 클래스들 (유지)
class RequirementTableSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    requirement_table = OutputField(desc="요구사항 정리 또는 핵심 요약 표 형식 출력. 항목별 구분 및 단위 포함")

class RequirementTableReAct(ReAct):
    def __init__(self):
        super().__init__(RequirementTableSignature)

# --- AI Reasoning Signature & ReAct 클래스
class AIReasoningSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    ai_reasoning = OutputField(desc="Chain-of-Thought 기반 추론 해설. 각 항목별 논리 전개 및 AI 추론 명시")

class AIReasoningReAct(ReAct):
    def __init__(self):
        super().__init__(AIReasoningSignature)

# --- 사례 비교 Signature & ReAct 클래스
class PrecedentComparisonSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    precedent_comparison = OutputField(desc="유사 사례 비교. 표 또는 요약 문단 포함")

class PrecedentComparisonReAct(ReAct):
    def __init__(self):
        super().__init__(PrecedentComparisonSignature)

# --- 전략 제언 Signature & ReAct 클래스
class StrategyRecommendationSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    strategy_recommendation = OutputField(desc="전략적 제언 및 우선순위 정리. 실행 가능한 제안 포함")

class StrategyReAct(ReAct):
    def __init__(self):
        super().__init__(StrategyRecommendationSignature)

# --- 최적화 조건 분석 Signature & ReAct 클래스
class OptimizationConditionSignature(Signature):
    input = InputField(desc="분석 목표, 프로그램, 조건, 분석 텍스트 등")
    optimization_analysis = OutputField(desc="최적화 조건 분석 결과. 목적, 중요도, 고려사항 포함")

class OptimizationReAct(ReAct):
    def __init__(self):
        super().__init__(OptimizationConditionSignature)

# --- Narrative 생성 Signature & ReAct 클래스
class NarrativeGenerationSignature(Signature):
    input = InputField(desc="프로젝트 정보, Narrative 방향 설정, 분석 결과 등")
    narrative_story = OutputField(desc="소설처럼 감성적이고 몰입감 있는 건축설계 발표용 Narrative. 스토리텔링 중심의 서술")

class NarrativeReAct(ReAct):
    def __init__(self):
        super().__init__(NarrativeGenerationSignature)

# --- 고급 분석 파이프라인 (3개 기능 모두 활용)
class AdvancedAnalysisPipeline(Module):
    def __init__(self):
        super().__init__()
        # BootstrapFewShot으로 학습된 ReAct 모델들
        self.requirement_analyzer = BootstrapFewShot(RequirementTableReAct())
        self.reasoning_engine = BootstrapFewShot(AIReasoningReAct())
        self.strategy_generator = BootstrapFewShot(StrategyReAct())
    
    def forward(self, input):
        # ReAct 기반 단계별 추론
        req_result = self.requirement_analyzer(input)
        reasoning_result = self.reasoning_engine(input + req_result)
        strategy_result = self.strategy_generator(input + req_result + reasoning_result)
        return strategy_result

def execute_with_retry(func, *args, max_retries=3, **kwargs):
    """재시도 로직을 포함한 함수 실행"""
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            if result and not str(result).startswith("❌") and not str(result).startswith("⚠️"):
                return result
            elif attempt == max_retries - 1:  # 마지막 시도
                return result
        except Exception as e:
            if attempt == max_retries - 1:  # 마지막 시도
                return f"❌ 오류: {e}"
            
            # 지수 백오프로 대기
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"⚠️ 오류 발생. {wait_time:.1f}초 후 재시도... (시도 {attempt + 1}/{max_retries})")
            time.sleep(wait_time)
    
    return "❌ 최대 재시도 횟수 초과. 잠시 후 다시 시도해주세요."

# --- 새로운 Anthropic SDK 기반 실행 함수들
def execute_agent_sdk(prompt: str, model: str = None):
    """Anthropic SDK를 사용한 일반적인 AI 에이전트 실행 함수"""
    return execute_with_sdk(prompt, model)

def execute_agent_hybrid(prompt: str, model: str = None, use_sdk: bool = True):
    """하이브리드 실행: SDK 우선, 실패 시 DSPy 폴백"""
    if use_sdk:
        try:
            result = execute_with_sdk(prompt, model)
            if result and not result.startswith("❌") and not result.startswith("⚠️"):
                return result
        except Exception as e:
            print(f"SDK 실행 실패, DSPy로 폴백: {e}")
    
    # DSPy 폴백
    return execute_with_retry(lambda: dspy.Predict(OptimizationConditionSignature)(input=prompt))

# --- 기존 함수들 (하위 호환성 유지) - 재시도 로직 추가
def run_requirement_table(full_prompt):
    def _run():
        result = dspy.Predict(RequirementTableSignature)(input=full_prompt)
        value = getattr(result, "requirement_table", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 요구사항표가 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_ai_reasoning(full_prompt):
    def _run():
        result = dspy.Predict(AIReasoningSignature)(input=full_prompt)
        value = getattr(result, "ai_reasoning", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: AI reasoning이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_precedent_comparison(full_prompt):
    def _run():
        result = dspy.Predict(PrecedentComparisonSignature)(input=full_prompt)
        value = getattr(result, "precedent_comparison", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 유사 사례 비교가 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_strategy_recommendation(full_prompt):
    def _run():
        result = dspy.Predict(StrategyRecommendationSignature)(input=full_prompt)
        value = getattr(result, "strategy_recommendation", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 전략 제언이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)



def execute_agent(prompt):
    """기존 DSPy 기반 실행 함수 (하위 호환성)"""
    def _run():
        result = dspy.Predict(OptimizationConditionSignature)(input=prompt)
        value = getattr(result, "optimization_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: AI 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def generate_narrative(prompt):
    """Narrative 생성 함수 - 개선된 버전"""
    def _run():
        # Narrative 전용 모델 사용
        from init_dspy import get_narrative_optimal_model, execute_with_sdk_with_retry
        
        # 직접 SDK 호출로 더 나은 성능
        result = execute_with_sdk_with_retry(prompt, get_narrative_optimal_model(), max_retries=3)
        
        if not result or result.strip() == "" or "error" in result.lower():
            # DSPy 폴백
            result = dspy.Predict(NarrativeGenerationSignature)(input=prompt)
            value = getattr(result, "narrative_story", "")
            if not value or value.strip() == "" or "error" in value.lower():
                return "⚠️ 결과 생성 실패: Narrative가 정상적으로 생성되지 않았습니다."
            return value
        
        return result
    
    return execute_with_retry(_run)

# --- 전체 합치기용 (실제 사용은 버튼 분할이 안전!)
def run_full_analysis(full_prompt):
    req = run_requirement_table(full_prompt)
    ai = run_ai_reasoning(full_prompt)
    pre = run_precedent_comparison(full_prompt)
    strat = run_strategy_recommendation(full_prompt)
    output = (
        "요구사항 정리표\n" + req + "\n\n" +
        "AI 추론 해설\n" + ai + "\n\n" +
        "유사 사례 비교\n" + pre + "\n\n" +
        "전략적 제언 및 시사점\n" + strat
    )
    return output

# --- Midjourney 프롬프트 생성 Signature & ReAct 클래스
class MidjourneyPromptSignature(Signature):
    input = InputField(desc="프로젝트 정보, 분석 결과, 이미지 설정 등")
    midjourney_prompt = OutputField(desc="한글 설명과 영어 Midjourney 프롬프트를 포함한 완전한 응답")

class MidjourneyPromptReAct(ReAct):
    def __init__(self):
        super().__init__(MidjourneyPromptSignature)

def execute_midjourney_prompt(prompt):
    """Midjourney 프롬프트 생성 전용 함수"""
    def _run():
        result = dspy.Predict(MidjourneyPromptSignature)(input=prompt)
        value = getattr(result, "midjourney_prompt", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: Midjourney 프롬프트가 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

# --- 새 블록들을 위한 Signature & ReAct 클래스들
class SiteEnvironmentAnalysisSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    site_environment_analysis = OutputField(desc="대지 환경 분석 결과. 지형, 향, 기후, 지반, 인프라 등 종합 분석")

class SiteEnvironmentAnalysisReAct(ReAct):
    def __init__(self):
        super().__init__(SiteEnvironmentAnalysisSignature)

class StructureTechnologyAnalysisSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    structure_technology_analysis = OutputField(desc="구조 기술 분석 결과. 구조 시스템, 기술적 요구사항, 최적화 방안")

class StructureTechnologyAnalysisReAct(ReAct):
    def __init__(self):
        super().__init__(StructureTechnologyAnalysisSignature)

class ProposalFrameworkSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    proposal_framework = OutputField(desc="제안서 프레임워크 설계. 구조, 핵심 메시지, 작성 가이드")

class ProposalFrameworkReAct(ReAct):
    def __init__(self):
        super().__init__(ProposalFrameworkSignature)

# --- 새 블록들을 위한 실행 함수들
def run_site_environment_analysis(full_prompt):
    """대지 환경 분석 실행 함수"""
    def _run():
        result = dspy.Predict(SiteEnvironmentAnalysisSignature)(input=full_prompt)
        value = getattr(result, "site_environment_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 대지 환경 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_structure_technology_analysis(full_prompt):
    """구조 기술 분석 실행 함수"""
    def _run():
        result = dspy.Predict(StructureTechnologyAnalysisSignature)(input=full_prompt)
        value = getattr(result, "structure_technology_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 구조 기술 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_proposal_framework(full_prompt):
    """제안서 프레임워크 실행 함수"""
    def _run():
        result = dspy.Predict(ProposalFrameworkSignature)(input=full_prompt)
        value = getattr(result, "proposal_framework", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 제안서 프레임워크가 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)
