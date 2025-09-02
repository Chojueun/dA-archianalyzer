# agent_executor.py
import dspy
from dspy import Module, Signature, InputField, OutputField
from dspy.teleprompt.bootstrap import BootstrapFewShot
from dspy.predict.react import ReAct
# 순환 import 방지를 위해 필요한 함수만 import
# Narrative 전용 모델 사용
from init_dspy import execute_with_sdk, execute_with_sdk_with_retry, get_narrative_optimal_model
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

# --- 기존 블록들을 위한 Signature & ReAct 클래스들
class DocumentAnalyzerSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    document_analysis = OutputField(desc="문서 분석 결과. 구조, 언어 패턴, 의도 추론")

class DocumentAnalyzerReAct(ReAct):
    def __init__(self):
        super().__init__(DocumentAnalyzerSignature)

class RequirementAnalyzerSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    requirement_analysis = OutputField(desc="요구사항 분석 결과. 분류, 우선순위, 전략")

class RequirementAnalyzerReAct(ReAct):
    def __init__(self):
        super().__init__(RequirementAnalyzerSignature)

class TaskComprehensionSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    task_comprehension = OutputField(desc="과업 이해 및 목표 설정 결과")

class TaskComprehensionReAct(ReAct):
    def __init__(self):
        super().__init__(TaskComprehensionSignature)

class RiskStrategistSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    risk_analysis = OutputField(desc="리스크 분석 및 대응 전략 결과")

class RiskStrategistReAct(ReAct):
    def __init__(self):
        super().__init__(RiskStrategistSignature)

class SiteRegulationAnalysisSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    site_regulation_analysis = OutputField(desc="대지 및 규제 분석 결과")

class SiteRegulationAnalysisReAct(ReAct):
    def __init__(self):
        super().__init__(SiteRegulationAnalysisSignature)

class ComplianceAnalyzerSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    compliance_analysis = OutputField(desc="규정 준수 및 적법성 분석 결과")

class ComplianceAnalyzerReAct(ReAct):
    def __init__(self):
        super().__init__(ComplianceAnalyzerSignature)

class PrecedentBenchmarkingSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    precedent_benchmarking = OutputField(desc="사례 벤치마킹 및 비교 분석 결과")

class PrecedentBenchmarkingReAct(ReAct):
    def __init__(self):
        super().__init__(PrecedentBenchmarkingSignature)

class CompetitorAnalyzerSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    competitor_analysis = OutputField(desc="경쟁사 분석 및 차별화 전략 결과")

class CompetitorAnalyzerReAct(ReAct):
    def __init__(self):
        super().__init__(CompetitorAnalyzerSignature)

class DesignTrendApplicationSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    design_trend_application = OutputField(desc="설계 트렌드 적용 및 혁신 방안 결과")

class DesignTrendApplicationReAct(ReAct):
    def __init__(self):
        super().__init__(DesignTrendApplicationSignature)

class MassStrategySignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    mass_strategy = OutputField(desc="매스 전략 및 배치 방향 결과")

class MassStrategyReAct(ReAct):
    def __init__(self):
        super().__init__(MassStrategySignature)

class FlexibleSpaceStrategySignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    flexible_space_strategy = OutputField(desc="가변형 공간 및 확장성 전략 결과")

class FlexibleSpaceStrategyReAct(ReAct):
    def __init__(self):
        super().__init__(FlexibleSpaceStrategySignature)

class ConceptDevelopmentSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    concept_development = OutputField(desc="설계 컨셉 개발 및 평가 결과")

class ConceptDevelopmentReAct(ReAct):
    def __init__(self):
        super().__init__(ConceptDevelopmentSignature)

class AreaProgrammingSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    area_programming = OutputField(desc="면적 프로그래밍 및 공간 배분 결과")

class AreaProgrammingReAct(ReAct):
    def __init__(self):
        super().__init__(AreaProgrammingSignature)

class SchematicSpacePlanSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    schematic_space_plan = OutputField(desc="스키매틱 공간 계획 결과")

class SchematicSpacePlanReAct(ReAct):
    def __init__(self):
        super().__init__(SchematicSpacePlanSignature)

class UXCirculationSimulationSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    ux_circulation_simulation = OutputField(desc="사용자 경험 및 동선 시뮬레이션 결과")

class UXCirculationSimulationReAct(ReAct):
    def __init__(self):
        super().__init__(UXCirculationSimulationSignature)

class DesignRequirementSummarySignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    design_requirement_summary = OutputField(desc="설계 요구사항 종합 요약 결과")

class DesignRequirementSummaryReAct(ReAct):
    def __init__(self):
        super().__init__(DesignRequirementSummarySignature)

class CostEstimationSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    cost_estimation = OutputField(desc="비용 추정 및 경제성 분석 결과")

class CostEstimationReAct(ReAct):
    def __init__(self):
        super().__init__(CostEstimationSignature)

class ArchitecturalBrandingIdentitySignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    architectural_branding_identity = OutputField(desc="건축 브랜딩 및 정체성 전략 결과")

class ArchitecturalBrandingIdentityReAct(ReAct):
    def __init__(self):
        super().__init__(ArchitecturalBrandingIdentitySignature)

class ActionPlannerSignature(Signature):
    input = InputField(desc="분석 목표, PDF, 맥락 등")
    action_planner = OutputField(desc="실행 계획 및 액션 플랜 결과")

class ActionPlannerReAct(ReAct):
    def __init__(self):
        super().__init__(ActionPlannerSignature)

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

# --- 기존 블록들을 위한 실행 함수들
def run_document_analyzer(full_prompt):
    """문서 분석 실행 함수"""
    def _run():
        result = dspy.Predict(DocumentAnalyzerSignature)(input=full_prompt)
        value = getattr(result, "document_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 문서 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_requirement_analyzer(full_prompt):
    """요구사항 분석 실행 함수"""
    def _run():
        result = dspy.Predict(RequirementAnalyzerSignature)(input=full_prompt)
        value = getattr(result, "requirement_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 요구사항 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_task_comprehension(full_prompt):
    """과업 이해 실행 함수"""
    def _run():
        result = dspy.Predict(TaskComprehensionSignature)(input=full_prompt)
        value = getattr(result, "task_comprehension", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 과업 이해가 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_risk_strategist(full_prompt):
    """리스크 분석 실행 함수"""
    def _run():
        result = dspy.Predict(RiskStrategistSignature)(input=full_prompt)
        value = getattr(result, "risk_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 리스크 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_site_regulation_analysis(full_prompt):
    """대지 규제 분석 실행 함수"""
    def _run():
        result = dspy.Predict(SiteRegulationAnalysisSignature)(input=full_prompt)
        value = getattr(result, "site_regulation_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 대지 규제 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_compliance_analyzer(full_prompt):
    """규정 준수 분석 실행 함수"""
    def _run():
        result = dspy.Predict(ComplianceAnalyzerSignature)(input=full_prompt)
        value = getattr(result, "compliance_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 규정 준수 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_precedent_benchmarking(full_prompt):
    """사례 벤치마킹 실행 함수"""
    def _run():
        result = dspy.Predict(PrecedentBenchmarkingSignature)(input=full_prompt)
        value = getattr(result, "precedent_benchmarking", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 사례 벤치마킹이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_competitor_analyzer(full_prompt):
    """경쟁사 분석 실행 함수"""
    def _run():
        result = dspy.Predict(CompetitorAnalyzerSignature)(input=full_prompt)
        value = getattr(result, "competitor_analysis", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 경쟁사 분석이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_design_trend_application(full_prompt):
    """설계 트렌드 적용 실행 함수"""
    def _run():
        result = dspy.Predict(DesignTrendApplicationSignature)(input=full_prompt)
        value = getattr(result, "design_trend_application", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 설계 트렌드 적용이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_mass_strategy(full_prompt):
    """매스 전략 실행 함수"""
    def _run():
        result = dspy.Predict(MassStrategySignature)(input=full_prompt)
        value = getattr(result, "mass_strategy", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 매스 전략이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_flexible_space_strategy(full_prompt):
    """가변형 공간 전략 실행 함수"""
    def _run():
        result = dspy.Predict(FlexibleSpaceStrategySignature)(input=full_prompt)
        value = getattr(result, "flexible_space_strategy", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 가변형 공간 전략이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_concept_development(full_prompt):
    """컨셉 개발 실행 함수"""
    def _run():
        result = dspy.Predict(ConceptDevelopmentSignature)(input=full_prompt)
        value = getattr(result, "concept_development", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 컨셉 개발이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_area_programming(full_prompt):
    """면적 프로그래밍 실행 함수"""
    def _run():
        result = dspy.Predict(AreaProgrammingSignature)(input=full_prompt)
        value = getattr(result, "area_programming", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 면적 프로그래밍이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_schematic_space_plan(full_prompt):
    """스키매틱 공간 계획 실행 함수"""
    def _run():
        result = dspy.Predict(SchematicSpacePlanSignature)(input=full_prompt)
        value = getattr(result, "schematic_space_plan", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 스키매틱 공간 계획이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_ux_circulation_simulation(full_prompt):
    """사용자 경험 및 동선 시뮬레이션 실행 함수"""
    def _run():
        result = dspy.Predict(UXCirculationSimulationSignature)(input=full_prompt)
        value = getattr(result, "ux_circulation_simulation", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 사용자 경험 및 동선 시뮬레이션이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_design_requirement_summary(full_prompt):
    """설계 요구사항 종합 요약 실행 함수"""
    def _run():
        result = dspy.Predict(DesignRequirementSummarySignature)(input=full_prompt)
        value = getattr(result, "design_requirement_summary", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 설계 요구사항 종합 요약이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_cost_estimation(full_prompt):
    """비용 추정 실행 함수"""
    def _run():
        result = dspy.Predict(CostEstimationSignature)(input=full_prompt)
        value = getattr(result, "cost_estimation", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 비용 추정이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_architectural_branding_identity(full_prompt):
    """건축 브랜딩 정체성 실행 함수"""
    def _run():
        result = dspy.Predict(ArchitecturalBrandingIdentitySignature)(input=full_prompt)
        value = getattr(result, "architectural_branding_identity", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 건축 브랜딩 정체성이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

def run_action_planner(full_prompt):
    """실행 계획 실행 함수"""
    def _run():
        result = dspy.Predict(ActionPlannerSignature)(input=full_prompt)
        value = getattr(result, "action_planner", "")
        if not value or value.strip() == "" or "error" in value.lower():
            return "⚠️ 결과 생성 실패: 실행 계획이 정상적으로 생성되지 않았습니다."
        return value
    
    return execute_with_retry(_run)

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

# # --- 하이데라바드 프로젝트 전용 블록들을 위한 Signature & ReAct 클래스들
# class HyderabadCampusExpansionAnalysisSignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_campus_expansion_analysis = OutputField(desc="하이데라바드 캠퍼스 확장성 분석 결과. 확장 시나리오, 우선순위, ROI 분석")

# class HyderabadCampusExpansionAnalysisReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadCampusExpansionAnalysisSignature)

# class HyderabadResearchInfraStrategySignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_research_infra_strategy = OutputField(desc="하이데라바드 연구 인프라 전략. 기능별 필요면적, 확충 계획, 단계별 로드맵")

# class HyderabadResearchInfraStrategyReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadResearchInfraStrategySignature)

# class HyderabadTalentCollaborationInfraSignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_talent_collaboration_infra = OutputField(desc="하이데라바드 인재 육성 및 협업 인프라. 교육 공간, 이노베이션 센터, 브랜딩 효과")

# class HyderabadTalentCollaborationInfraReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadTalentCollaborationInfraSignature)

# class HyderabadWelfareBrandingEnvironmentSignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_welfare_branding_environment = OutputField(desc="하이데라바드 복지 및 브랜드 환경. 편의시설, 브랜드 경험, 사용자 만족도")

# class HyderabadWelfareBrandingEnvironmentReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadWelfareBrandingEnvironmentSignature)

# class HyderabadSecurityZoningPlanSignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_security_zoning_plan = OutputField(desc="하이데라바드 보안 및 존잉 계획. 보안등급, 위험요인, 대응방안")

# class HyderabadSecurityZoningPlanReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadSecurityZoningPlanSignature)

# class HyderabadMasterplanRoadmapSignature(Signature):
#     input = InputField(desc="분석 목표, PDF, 맥락 등")
#     hyderabad_masterplan_roadmap = OutputField(desc="하이데라바드 마스터플랜 로드맵. 단계별 실행계획, ROI 분석, 종합 전략")

# class HyderabadMasterplanRoadmapReAct(ReAct):
#     def __init__(self):
#         super().__init__(HyderabadMasterplanRoadmapSignature)

# # --- 하이데라바드 프로젝트 전용 블록들을 위한 실행 함수들
# def run_hyderabad_campus_expansion_analysis(full_prompt):
#     """하이데라바드 캠퍼스 확장성 분석 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadCampusExpansionAnalysisSignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_campus_expansion_analysis", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 캠퍼스 확장성 분석이 정상적으로 생성되지 않았습니다."
#         return value
    
#     return execute_with_retry(_run)

# def run_hyderabad_research_infra_strategy(full_prompt):
#     """하이데라바드 연구 인프라 전략 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadResearchInfraStrategySignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_research_infra_strategy", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 연구 인프라 전략이 정상적으로 생성되지 않았습니다."
#         return value
    
#     return execute_with_retry(_run)

# def run_hyderabad_talent_collaboration_infra(full_prompt):
#     """하이데라바드 인재 육성 및 협업 인프라 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadTalentCollaborationInfraSignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_talent_collaboration_infra", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 인재 육성 및 협업 인프라가 정상적으로 생성되지 않았습니다."
#         return value
    
#     return execute_with_retry(_run)

# def run_hyderabad_welfare_branding_environment(full_prompt):
#     """하이데라바드 복지 및 브랜드 환경 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadWelfareBrandingEnvironmentSignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_welfare_branding_environment", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 복지 및 브랜드 환경이 정상적으로 생성되지 않았습니다."
#         return value
    
#     return execute_with_retry(_run)

# def run_hyderabad_security_zoning_plan(full_prompt):
#     """하이데라바드 보안 및 존잉 계획 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadSecurityZoningPlanSignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_security_zoning_plan", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 보안 및 존잉 계획이 정상적으로 생성되지 않았습니다."
#         return value
    
#     return execute_with_retry(_run)

# def run_hyderabad_masterplan_roadmap(full_prompt):
#     """하이데라바드 마스터플랜 로드맵 실행 함수"""
#     def _run():
#         result = dspy.Predict(HyderabadMasterplanRoadmapSignature)(input=full_prompt)
#         value = getattr(result, "hyderabad_masterplan_roadmap", "")
#         if not value or value.strip() == "" or "error" in value.lower():
#             return "⚠️ 결과 생성 실패: 하이데라바드 마스터플랜 로드맵이 정상적으로 생성되지 않았습니다."
#         return value
    
    return execute_with_retry(_run)
