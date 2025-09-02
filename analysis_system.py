#analysis_system.py

"""
분석 시스템 핵심 구조
- 용도/목적 분류
- 단계 자동 제안
- 필수 단계 포함
- 번외 항목 추가
- 순서 변경 및 추가/삭제
- 전체 순서 확정 및 분석 실행
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class PurposeType(Enum):
    """용도 분류"""
    NEIGHBORHOOD_FACILITY = "근린생활시설"
    CULTURAL_FACILITY = "문화 및 집회시설"
    RETAIL_FACILITY = "판매시설(리테일)"
    TRANSPORTATION_FACILITY = "운수시설"
    MEDICAL_FACILITY = "의료시설"
    EDUCATIONAL_FACILITY = "교육연구시설"
    ELDERLY_FACILITY = "노유자시설"
    TRAINING_FACILITY = "수련시설"
    SPORTS_FACILITY = "운동시설"
    OFFICE_FACILITY = "업무시설"
    ACCOMMODATION_FACILITY = "숙박시설"
    RESIDENTIAL_FACILITY = "공동주택"
    OTHER_FACILITY = "기타시설"

class ObjectiveType(Enum):
    """목적 분류"""
    PLANNING_CONCEPT_DESIGN = "계획안/컨셉/디자인"
    MARKET_PROFITABILITY_INVESTMENT = "상권/수익성/투자"
    LEGAL_PERMIT = "법적/인허가"
    SPACE_CIRCULATION_UX = "공간/동선/UX"
    OPERATION_MANAGEMENT = "운영/관리"
    OTHER = "기타"

@dataclass
class AnalysisStep:
    """분석 단계 정보"""
    id: str
    title: str
    description: str
    is_required: bool = False
    is_recommended: bool = False
    is_optional: bool = False
    order: int = 0
    category: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AnalysisWorkflow:
    """분석 워크플로우"""
    purpose: PurposeType
    objective: ObjectiveType
    steps: List[AnalysisStep]
    custom_steps: List[AnalysisStep] = None
    
    def __post_init__(self):
        if self.custom_steps is None:
            self.custom_steps = []

class AnalysisSystem:
    """분석 시스템 핵심 클래스"""
    
    def __init__(self):
        self.purpose_objective_mapping = self._load_purpose_objective_mapping()
        self.required_steps = self._load_required_steps()
        self.recommended_steps = self._load_recommended_steps()
        self.optional_steps = self._load_optional_steps()

    # ─── 실행과 관련된 핵심 로직 (과거 코드 통합) ─────────────────────────────
    
    def get_available_objectives(self, purpose: PurposeType) -> List[ObjectiveType]:
        """용도에 따른 사용 가능한 목적 반환"""
        return self.purpose_objective_mapping.get(purpose, [ObjectiveType.OTHER])
    
    def suggest_analysis_steps(self, purpose: PurposeType, objectives: List[ObjectiveType]) -> AnalysisWorkflow:
        """분석 단계 자동 제안 - 용도별 권장 블록 기반"""
        # 1. 필수 단계 추가
        steps = self.required_steps.copy()
        print(f"DEBUG: 필수 단계 수 = {len(steps)}")
        
        # 2. 용도별 권장 단계 추가
        if purpose in self.recommended_steps:
            steps.extend(self.recommended_steps[purpose])
            print(f"DEBUG: 용도별 권장 단계 추가됨 = {len(self.recommended_steps[purpose])}개")
        else:
            print(f"DEBUG: 용도 {purpose.value}에 대한 권장 단계 없음")
        
        # 3. 목적별 추가 필수 단계 추가 (목적에 따라)
        for objective in objectives:
            print(f"DEBUG: 목적 {objective.value} 처리 중...")
            if objective == ObjectiveType.PLANNING_CONCEPT_DESIGN:
                # 계획안/컨셉/디자인 목적일 때 추가 필수
                additional_steps = [
                    AnalysisStep(
                        id="design_trend_application",
                        title="통합 디자인 트렌드 적용 전략",
                        description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                        is_recommended=True,
                        order=11,
                        category="디자인트렌드"
                    ),
                    AnalysisStep(
                        id="design_requirement_summary",
                        title="최종 설계 요구사항 및 가이드라인",
                        description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                        is_recommended=True,
                        order=12,
                        category="요구사항정리"
                    )
                ]
                steps.extend(additional_steps)
                print(f"DEBUG: 계획안/컨셉/디자인 목적 추가 단계 = {len(additional_steps)}개")
            
            elif objective == ObjectiveType.MARKET_PROFITABILITY_INVESTMENT:
                # 상권/수익성/투자 목적일 때 추가 필수
                additional_steps = [
                    AnalysisStep(
                        id="precedent_benchmarking",
                        title="선진사례 벤치마킹 및 최적 운영전략",
                        description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                        is_recommended=True,
                        order=11,
                        category="벤치마킹"
                    ),

                ]
                steps.extend(additional_steps)
                print(f"DEBUG: 상권/수익성/투자 목적 추가 단계 = {len(additional_steps)}개")
            
            elif objective == ObjectiveType.LEGAL_PERMIT:
                # 법적/인허가 목적일 때 추가 필수
                additional_steps = [
                    AnalysisStep(
                        id="design_requirement_summary",
                        title="최종 설계 요구사항 및 가이드라인",
                        description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                        is_recommended=True,
                        order=11,
                        category="요구사항정리"
                    )
                ]
                steps.extend(additional_steps)
                print(f"DEBUG: 법적/인허가 목적 추가 단계 = {len(additional_steps)}개")
            
            elif objective == ObjectiveType.OPERATION_MANAGEMENT:
                # 운영/관리 목적일 때는 추가 단계 없음 (cost_estimation에 통합됨)
                pass
        
        print(f"DEBUG: 중복 제거 전 총 단계 수 = {len(steps)}")
        
        # 4. 중복 제거 (ID 기준)
        unique_steps = []
        seen_ids = set()
        for step in steps:
            if step.id not in seen_ids:
                unique_steps.append(step)
                seen_ids.add(step.id)
        
        print(f"DEBUG: 중복 제거 후 총 단계 수 = {len(unique_steps)}")
        
        # 5. 순서 정렬
        unique_steps.sort(key=lambda x: x.order)
        
        return AnalysisWorkflow(
            purpose=purpose,
            objective=objectives[0] if objectives else ObjectiveType.OTHER,
            steps=unique_steps
        )

    def add_optional_step(self, workflow: AnalysisWorkflow, step_id: str) -> AnalysisWorkflow:
        """번외 단계 추가 (과거 코드 방식)"""
        optional_step = next((step for step in self.optional_steps if step.id == step_id), None)
        if optional_step:
            workflow.custom_steps.append(optional_step)
        return workflow

    def remove_step(self, workflow: AnalysisWorkflow, step_id: str) -> AnalysisWorkflow:
        """단계 제거 (필수 단계는 제거 불가)"""
        workflow.steps = [step for step in workflow.steps if not (step.id == step_id and not step.is_required)]
        workflow.custom_steps = [step for step in workflow.custom_steps if step.id != step_id]
        return workflow

    def reorder_steps(self, workflow: AnalysisWorkflow, new_order: List[str]) -> AnalysisWorkflow:
        """순서 변경 (과거 코드 방식)"""
        all_steps = workflow.steps + workflow.custom_steps
        
        ordered_steps = []
        for step_id in new_order:
            step = next((s for s in all_steps if s.id == step_id), None)
            if step:
                ordered_steps.append(step)
        
        required_steps = [step for step in ordered_steps if step.is_required]
        other_steps = [step for step in ordered_steps if not step.is_required]
        
        workflow.steps = required_steps
        workflow.custom_steps = other_steps
        
        return workflow

    def get_final_workflow(self, workflow: AnalysisWorkflow) -> List[AnalysisStep]:
        """최종 실행 단계 목록 (과거 코드 방식)"""
        all_steps = workflow.steps + workflow.custom_steps
        all_steps.sort(key=lambda x: x.order)
        return all_steps

    # ─── 실행 상태 관리 (새로 추가) ─────────────────────────────
    
    def get_current_step(self, workflow: AnalysisWorkflow, current_index: int) -> AnalysisStep:
        """현재 실행할 단계 반환"""
        all_steps = self.get_final_workflow(workflow)
        if 0 <= current_index < len(all_steps):
            return all_steps[current_index]
        return None

    def get_step_progress(self, workflow: AnalysisWorkflow, completed_steps: List[str]) -> Dict:
        """단계별 진행 상황 반환"""
        all_steps = self.get_final_workflow(workflow)
        progress = {
            "total": len(all_steps),
            "completed": len(completed_steps),
            "current_index": len(completed_steps),
            "progress_percentage": (len(completed_steps) / len(all_steps)) * 100 if all_steps else 0,
            "steps_status": []
        }
        
        for i, step in enumerate(all_steps):
            status = "completed" if step.title in completed_steps else "pending"
            if i == len(completed_steps):
                status = "current"
            
            progress["steps_status"].append({
                "index": i,
                "step": step,
                "status": status
            })
        
        return progress

    def can_execute_step(self, workflow: AnalysisWorkflow, step_id: str, completed_steps: List[str]) -> bool:
        """단계 실행 가능 여부 확인"""
        step = next((s for s in self.get_final_workflow(workflow) if s.id == step_id), None)
        if not step:
            return False
        
        # 의존성 확인
        for dependency in step.dependencies:
            if dependency not in completed_steps:
                return False
        
        return True

    def get_next_executable_step(self, workflow: AnalysisWorkflow, completed_steps: List[str]) -> AnalysisStep:
        """다음 실행 가능한 단계 반환"""
        all_steps = self.get_final_workflow(workflow)
        
        for step in all_steps:
            if step.title not in completed_steps and self.can_execute_step(workflow, step.id, completed_steps):
                return step
        
        return None

    # ─── 기존 메서드들 (유지) ─────────────────────────────
    
    def _load_purpose_objective_mapping(self) -> Dict[PurposeType, List[ObjectiveType]]:
        """용도별 목적 매핑 로드"""
        return {
            PurposeType.NEIGHBORHOOD_FACILITY: [
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.SPACE_CIRCULATION_UX,
                ObjectiveType.OPERATION_MANAGEMENT
            ],
            PurposeType.CULTURAL_FACILITY: [
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.RETAIL_FACILITY: [
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.OPERATION_MANAGEMENT
            ],
            PurposeType.TRANSPORTATION_FACILITY: [
                ObjectiveType.LEGAL_PERMIT,
                ObjectiveType.OPERATION_MANAGEMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.MEDICAL_FACILITY: [
                ObjectiveType.LEGAL_PERMIT,
                ObjectiveType.OPERATION_MANAGEMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.EDUCATIONAL_FACILITY: [
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.SPACE_CIRCULATION_UX,
                ObjectiveType.OPERATION_MANAGEMENT
            ],
            PurposeType.ELDERLY_FACILITY: [
                ObjectiveType.LEGAL_PERMIT,
                ObjectiveType.OPERATION_MANAGEMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.TRAINING_FACILITY: [
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.SPORTS_FACILITY: [
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.OPERATION_MANAGEMENT,
                ObjectiveType.SPACE_CIRCULATION_UX
            ],
            PurposeType.OFFICE_FACILITY: [
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.OPERATION_MANAGEMENT
            ],
            PurposeType.ACCOMMODATION_FACILITY: [
                ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
                ObjectiveType.OPERATION_MANAGEMENT,
                ObjectiveType.PLANNING_CONCEPT_DESIGN
            ],
            PurposeType.RESIDENTIAL_FACILITY: [
            ObjectiveType.PLANNING_CONCEPT_DESIGN,
            ObjectiveType.MARKET_PROFITABILITY_INVESTMENT,
            ObjectiveType.LEGAL_PERMIT,
            ObjectiveType.SPACE_CIRCULATION_UX,
            ObjectiveType.OPERATION_MANAGEMENT,
            ObjectiveType.OTHER
            ],
            PurposeType.OTHER_FACILITY: [
                ObjectiveType.PLANNING_CONCEPT_DESIGN,
                ObjectiveType.OPERATION_MANAGEMENT
            ]
        }

    def _load_required_steps(self) -> List[AnalysisStep]:
        """전용도·전목적 공통 필수 블록"""
        return [
            AnalysisStep(
                id="document_analyzer",
                title="문서 분석 및 건축주 의도 추론",
                description="입찰/계약 문서의 구조, 요구사항, 언어 패턴을 종합 분석하여 건축주의 명시적/암묵적 의도를 파악",
                is_required=True,
                order=1,
                category="문서분석"
            ),
            AnalysisStep(
                id="requirement_analyzer",
                title="요구사항 종합 분석 및 전략 도출",
                description="문서에서 추출된 요구사항을 종합 분석하여 설계 전략과 실행 가능한 방안 도출",
                is_required=True,
                order=2,
                category="요구사항분석"
            ),
            AnalysisStep(
                id="task_comprehension",
                title="과업 이해 및 목표 설정",
                description="프로젝트의 핵심 과업과 목표를 명확히 이해하고 분석 방향 설정",
                is_required=True,
                order=3,
                category="과업이해도"
            ),
            AnalysisStep(
                id="risk_strategist",
                title="리스크 분석 및 대응 전략",
                description="프로젝트의 주요 리스크를 식별하고 대응 전략 수립",
                is_required=True,
                order=4,
                category="리스크분석"
            ),
            AnalysisStep(
                id="site_environment_analysis",
                title="대지 환경 분석",
                description="지형·향·식생·지반·접근성·인프라 등 물리적 조건을 종합 분석하여 설계 기초 자료와 배치 전략을 도출",
                is_required=True,
                order=5,
                category="대지분석"
            ),
            AnalysisStep(
                id="site_regulation_analysis",
                title="대지 법규 분석",
                description="대상 대지의 법적 제약사항과 규제 요건을 분석하여 설계 시 준수해야 할 법규 기반을 마련",
                is_required=True,
                order=6,
                category="법규분석"
            ),
            AnalysisStep(
                id="compliance_analyzer",
                title="규정 준수 및 적법성 분석",
                description="모든 설계 요소가 관련 규정을 준수하는지 검증하고 적법성 확보",
                is_required=True,
                order=7,
                category="규정준수"
            ),
            AnalysisStep(
                id="concept_development",
                title="설계 컨셉 개발 및 평가",
                description="프로젝트의 핵심 아이디어와 설계 컨셉을 개발하고 평가하여 최적 방안 도출",
                is_required=True,
                order=8,
                category="컨셉개발"
            ),
            AnalysisStep(
                id="mass_strategy",
                title="건축설계 방향 및 매스(Mass) 전략",
                description="전 단계 분석 결과를 통합해 건축설계의 핵심 컨셉과 최적 매스 전략을 도출",
                is_required=True,
                order=9,
                category="매스전략"
            ),
            AnalysisStep(
                id="schematic_space_plan",
                title="스키매틱 공간 계획",
                description="설계 컨셉을 바탕으로 한 스키매틱 공간 계획 수립",
                is_required=True,
                order=10,
                category="공간계획"
            ),
            AnalysisStep(
                id="area_programming",
                title="면적 프로그래밍 및 공간 배분",
                description="수요 기반 분석과 시장/법적 기준을 바탕으로 최적의 공간구성과 면적 배분안을 도출",
                is_required=True,
                order=11,
                category="면적계획"
            ),
            AnalysisStep(
                id="cost_estimation",
                title="비용 추정 및 경제성 분석",
                description="연면적, 용도, 적용 공법 등 입력값을 바탕으로 개략 공사비와 비용구조를 산출하고, 운영비, 관리비, 투자수익률 등 주요 재무지표 기반으로 경제성·운영효율성을 평가",
                is_required=True,
                order=12,
                category="원가분석"
            )
        ]

    def _load_recommended_steps(self) -> Dict[PurposeType, List[AnalysisStep]]:
        """용도별 권장 블록"""
        return {
            PurposeType.NEIGHBORHOOD_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=10,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=11,
                    category="브랜딩전략"
                ),

                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=13,
                    category="요구사항정리"
                )
            ],
            PurposeType.CULTURAL_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=10,
                    category="브랜딩전략"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=11,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=12,
                    category="요구사항정리"
                )
            ],
            PurposeType.RETAIL_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=11,
                    category="브랜딩전략"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=12,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=13,
                    category="요구사항정리"
                )
            ],
            PurposeType.TRANSPORTATION_FACILITY: [
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인 (안전/보안/분리동선 규정화)",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=9,
                    category="요구사항정리"
                ),
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=11,
                    category="벤치마킹"
                )
            ],
            PurposeType.MEDICAL_FACILITY: [
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인 (감염·동선·규범)",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=9,
                    category="요구사항정리"
                ),
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=11,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=12,
                    category="브랜딩전략"
                )
            ],
            PurposeType.EDUCATIONAL_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=10,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=11,
                    category="요구사항정리"
                )
            ],
            PurposeType.ELDERLY_FACILITY: [
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인 (케어/안전)",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=9,
                    category="요구사항정리"
                ),
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=11,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=12,
                    category="브랜딩전략"
                )
            ],
            PurposeType.TRAINING_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=10,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=12,
                    category="요구사항정리"
                )
            ],
            PurposeType.SPORTS_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=11,
                    category="요구사항정리"
                )
            ],
            PurposeType.OFFICE_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=11,
                    category="브랜딩전략"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=12,
                    category="요구사항정리"
                )
            ],
            PurposeType.ACCOMMODATION_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=11,
                    category="브랜딩전략"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=12,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=13,
                    category="요구사항정리"
                )
            ],
            PurposeType.RESIDENTIAL_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_trend_application",
                    title="통합 디자인 트렌드 적용 전략",
                    description="건축·인테리어·조경 분야의 핵심 트렌드와 실현 가능한 적용 전략을 제시",
                    is_recommended=True,
                    order=10,
                    category="디자인트렌드"
                ),
                AnalysisStep(
                    id="architectural_branding_identity",
                    title="건축적 차별화·브랜딩·정체성 전략",
                    description="상징성, 로컬리티, 테마, 감성 건축 등 차별화 포인트를 반영한 프로젝트 고유의 브랜딩 및 정체성 전략을 도출",
                    is_recommended=True,
                    order=11,
                    category="브랜딩전략"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=12,
                    category="요구사항정리"
                )
            ],
            PurposeType.OTHER_FACILITY: [
                AnalysisStep(
                    id="precedent_benchmarking",
                    title="선진사례 벤치마킹 및 최적 운영전략",
                    description="국내외 유사 프로젝트 사례를 심층 분석해 차별화 요소와 최적 운영 방안을 도출",
                    is_recommended=True,
                    order=9,
                    category="벤치마킹"
                ),
                AnalysisStep(
                    id="design_requirement_summary",
                    title="최종 설계 요구사항 및 가이드라인",
                    description="분석 결과를 바탕으로 실제 설계에 적용 가능한 요구사항과 가이드라인을 구조화",
                    is_recommended=True,
                    order=10,
                    category="요구사항정리"
                )
            ]
        }

    def _load_optional_steps(self) -> List[AnalysisStep]:
        """선택적 분석 단계들"""
        return [
            AnalysisStep(
                id="ux_circulation_simulation",
                title="사용자 동선 분석 및 시나리오별 공간 최적화 전략",
                description="사용자 유형별 동선/체류 시나리오와 AI 기반 시뮬레이션 결과를 바탕으로 공간·동선 최적화 전략을 제시",
                is_optional=True,
                order=15,
                category="동선분석"
            ),
            AnalysisStep(
                id="flexible_space_strategy",
                title="가변형 공간·프로그램 유연성 및 확장성 설계 전략",
                description="프로그램 변화·미래 수요 대응을 위한 가변형 공간, 다목적 영역, Flexible Mass/Plan 설계 방안을 제시",
                is_optional=True,
                order=16,
                category="가변공간"
            ),
            AnalysisStep(
                id="requirements_extractor",
                title="요구사항 분류 및 우선순위 도출",
                description="문서 내 명시적/암묵적 요구사항을 입찰·설계·비용 등 카테고리로 구분, 우선순위 및 심사 포인트 도출",
                is_optional=True,
                order=17,
                category="요구사항분류"
            ),
            AnalysisStep(
                id="compliance_analyzer",
                title="법규·지침 준수 체크",
                description="요구사항별 관련 법령·지침 준수 여부 및 필수 인증·승인 절차 체크리스트 도출",
                is_optional=True,
                order=18,
                category="법규준수"
            ),
            AnalysisStep(
                id="action_planner",
                title="실행 체크리스트 및 핵심 포인트",
                description="입찰·계약 준비를 위한 우선 수행과제, 일정, 담당자, 필수 기억사항 정리",
                is_optional=True,
                order=19,
                category="실행계획"
            ),
            AnalysisStep(
                id="competitor_analyzer",
                title="경쟁사 분석 및 차별화 전략",
                description="예상 경쟁사 분석을 통해 차별화 포인트와 경쟁 우위 전략을 도출",
                is_optional=True,
                order=20,
                category="경쟁분석"
            ),
            AnalysisStep(
                id="structure_technology_analysis",
                title="구조 기술 분석",
                description="구조 시스템과 기술적 요구사항을 분석하여 최적의 구조 방안을 도출",
                is_optional=True,
                order=21,
                category="구조분석"
            ),
            AnalysisStep(
                id="proposal_framework",
                title="제안서 프레임워크 설계",
                description="분석 결과를 바탕으로 제안서 구조와 핵심 메시지를 설계",
                is_optional=True,
                order=22,
                category="제안서설계"
            )
        ]

    # ─── 유틸리티 메서드들 ─────────────────────────────
    
    def export_workflow_config(self, workflow: AnalysisWorkflow) -> Dict:
        """워크플로우 설정 내보내기"""
        return {
            "purpose": workflow.purpose.value,
            "objective": workflow.objective.value,
            "steps": [
                {
                    "id": step.id,
                    "title": step.title,
                    "description": step.description,
                    "is_required": step.is_required,
                    "is_recommended": step.is_recommended,
                    "is_optional": step.is_optional,
                    "order": step.order,
                    "category": step.category
                }
                for step in self.get_final_workflow(workflow)
            ]
        }

    def import_workflow_config(self, config: Dict) -> AnalysisWorkflow:
        """워크플로우 설정 가져오기"""
        purpose = PurposeType(config["purpose"])
        objective = ObjectiveType(config["objective"])
        
        steps = []
        for step_config in config["steps"]:
            step = AnalysisStep(
                id=step_config["id"],
                title=step_config["title"],
                description=step_config["description"],
                is_required=step_config["is_required"],
                is_recommended=step_config["is_recommended"],
                is_optional=step_config["is_optional"],
                order=step_config["order"],
                category=step_config["category"]
            )
            steps.append(step)
        
        return AnalysisWorkflow(
            purpose=purpose,
            objective=objective,
            steps=steps
        )

    def _load_recommended_cot_order(self) -> Dict[str, int]:
        """권장 CoT 순서 매핑 (하이데라바드 블록 추가)"""
        return {
            "document_analyzer": 1,           # doc_collector → document_analyzer
            "requirement_analyzer": 2,        # requirements_extractor → requirement_analyzer
            "task_comprehension": 3,          # requirement_analysis → task_comprehension
            "risk_strategist": 4,             # context_analyzer → risk_strategist
            "site_environment_analysis": 5,   # 대지 환경 분석 (필수로 변경)
            "site_regulation_analysis": 6,    # 대지 법규 분석
            "compliance_analyzer": 7,         # 순서 조정
            "precedent_benchmarking": 8,      # 순서 조정
            "competitor_analyzer": 9,         # 순서 조정
            "design_trend_application": 10,   # 순서 조정
            "mass_strategy": 11,              # 순서 조정
            "flexible_space_strategy": 12,    # 순서 조정
            "concept_development": 13,        # 순서 조정
            "area_programming": 14,           # 순서 조정
            "schematic_space_plan": 15,       # 순서 조정
            "ux_circulation_simulation": 16,  # 순서 조정
            "design_requirement_summary": 17, # 순서 조정
            "cost_estimation": 18,            # 순서 조정
            "architectural_branding_identity": 19, # 순서 조정
            "action_planner": 20,             # 순서 조정
            "structure_technology_analysis": 21, # 구조 기술 분석
            "proposal_framework": 22,          # 제안서 프레임워크
            
            # 하이데라바드 프로젝트 전용 블록들 (일시적으로 비활성화)
            # "hyderabad_campus_expansion_analysis": 23,
            # "hyderabad_research_infra_strategy": 24,
            # "hyderabad_talent_collaboration_infra": 25,
            # "hyderabad_welfare_branding_environment": 26,
            # "hyderabad_security_zoning_plan": 27,
            # "hyderabad_masterplan_roadmap": 28
        }

    def sort_steps_by_recommended_order(self, steps: List[AnalysisStep]) -> List[AnalysisStep]:
        """권장 CoT 순서에 따라 단계 정렬"""
        cot_order = self._load_recommended_cot_order()
        
        def get_order(step):
            return cot_order.get(step.id, 999)  # 매핑되지 않은 단계는 마지막에
        
        return sorted(steps, key=get_order)

# 사용 예시
if __name__ == "__main__":
    system = AnalysisSystem()
    
    # 용도와 목적 선택
    purpose = PurposeType.OFFICE_FACILITY
    objectives = [ObjectiveType.MARKET_PROFITABILITY_INVESTMENT, ObjectiveType.PLANNING_CONCEPT_DESIGN]
    
    # 분석 단계 자동 제안
    workflow = system.suggest_analysis_steps(purpose, objectives)
    
    print(f"용도: {purpose.value}")
    print(f"목적: {[obj.value for obj in objectives]}")
    print("\n제안된 분석 단계:")
    for step in workflow.steps:
        print(f"- {step.title} ({step.category})")
    
    # 번외 단계 추가
    workflow = system.add_optional_step(workflow, "concept_development")
    
    print("\n번외 단계 추가 후:")
    for step in system.get_final_workflow(workflow):
        print(f"- {step.title} ({step.category})") 