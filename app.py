
# app.py
import streamlit as st
import os
import time
from dsl_to_prompt import load_prompt_blocks
from user_state import (
    init_user_state, get_user_inputs, save_step_result, append_step_history, get_current_step_index,
    save_user_data, save_current_project, load_project, get_user_project_list
)
from summary_generator import summarize_pdf, extract_site_analysis_fields, analyze_pdf_in_chunks
from utils_pdf import save_pdf_chunks_to_chroma, get_pdf_summary_from_session, set_pdf_summary_to_session
from utils import extract_summary, extract_insight
# DSPy import 제거 - 필요할 때만 import
# from init_dspy import *
from dsl_to_prompt import (
    convert_dsl_to_prompt, prompt_requirement_table, prompt_ai_reasoning,
    prompt_precedent_comparison, prompt_strategy_recommendation
)
from agent_executor import (
    run_requirement_table, run_ai_reasoning,
    run_precedent_comparison, run_strategy_recommendation
)
from PIL import Image
from auth_system import init_auth, login_page, admin_panel, logout
from analysis_system import AnalysisStep, AnalysisSystem

# dA-logo.png가 프로젝트 폴더에 있어야 함!
logo = Image.open("dA-logo.png")

# 방법 1: CSS로 강제 크기 조정
st.markdown("""
<style>
.sidebar .stImage img {
    width: 30px !important;
    height: auto !important;
}
</style>
""", unsafe_allow_html=True)

# PIL로 이미지를 직접 리사이즈
logo = Image.open("dA-logo.png")
logo_resized = logo.resize((100, int(100 * logo.height / logo.width)), Image.Resampling.LANCZOS)
st.sidebar.image(logo_resized, use_container_width=False)

# 로고 아래에 초기화 버튼 추가
if st.sidebar.button("🔄 초기화", type="secondary", help="모든 분석 데이터를 초기 상태로 리셋합니다"):
    # 분석 관련 상태 초기화
    st.session_state.analysis_started = False
    st.session_state.analysis_completed = False
    st.session_state.current_step_index = 0
    st.session_state.cot_history = []
    st.session_state.step_history = []
    st.session_state.step_results = {}
    st.session_state.workflow_steps = []
    st.session_state.editable_steps = []
    st.session_state.current_step_display_data = None
    st.session_state.current_step_outputs = {}
    st.session_state.web_search_settings = {}
    st.session_state.show_next_step_button = False
    
    # PDF 관련 데이터 초기화
    st.session_state.pdf_summary = ""
    st.session_state.uploaded_pdf = None
    st.session_state.pdf_analysis_result = {}
    st.session_state.pdf_quality_report = {}
    
    # 사용자 입력 초기화 (개별 필드들도 초기화)
    st.session_state.user_inputs = {
        "project_name": "",
        "owner": "",
        "site_location": "",
        "site_area": "",
        "zoning": "",
        "building_type": "",
        "project_goal": "",
    }
    
    # 개별 프로젝트 정보 필드들도 초기화
    st.session_state.project_name = ""
    st.session_state.owner = ""
    st.session_state.site_location = ""
    st.session_state.site_area = ""
    st.session_state.zoning = ""
    st.session_state.building_type = ""
    st.session_state.project_goal = ""
    
    # 선택된 목적/용도 초기화
    st.session_state.selected_purpose = None
    st.session_state.selected_objectives = []
    
    # 워크플로우 관련 초기화
    st.session_state.removed_steps = set()
    st.session_state.added_steps = set()
    
    st.success("✅ 모든 데이터가 초기 상태로 리셋되었습니다!")
    st.rerun()

# 인증 시스템 초기화
init_auth()

# 로그인 상태 확인
if not st.session_state.authenticated:
    login_page()
    st.stop()

# 로그인된 사용자 정보 표시
st.sidebar.markdown(f"### {st.session_state.current_user}")
if st.sidebar.button("로그아웃"):
    logout()

# 관리자만 접근 가능한 패널
if st.session_state.current_user == "admin":
    with st.sidebar.expander("관리자 패널"):
        admin_panel()

# 프로젝트 관리 섹션 추가
with st.sidebar.expander("📁 프로젝트 관리"):
    # 프로젝트 저장
    project_name = st.text_input("프로젝트 이름", placeholder="예: Woori Bank Project")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 저장", type="primary"):
            if project_name:
                if save_current_project(project_name):
                    st.success(f"프로젝트 '{project_name}' 저장 완료!")
                else:
                    st.error("프로젝트 저장 실패!")
            else:
                st.warning("프로젝트 이름을 입력해주세요.")
    
    with col2:
        if st.button("🔄 자동 저장"):
            if save_user_data():
                st.success("자동 저장 완료!")
            else:
                st.error("자동 저장 실패!")
    
    # 저장된 프로젝트 목록
    st.markdown("### 저장된 프로젝트")
    project_list = get_user_project_list()
    
    if project_list:
        selected_project = st.selectbox("프로젝트 선택", [""] + project_list)
        if selected_project and st.button("📂 불러오기"):
            if load_project(selected_project):
                st.success(f"프로젝트 '{selected_project}' 불러오기 완료!")
                st.rerun()
            else:
                st.error("프로젝트 불러오기 실패!")
    else:
        st.info("저장된 프로젝트가 없습니다.")

# 사이드바에서 실행 방식 선택 제거
with st.sidebar:
    st.markdown("### AI 모델 선택")
    
    # DSPy import 지연
    try:
        from init_dspy import get_model_info, get_available_models_sdk
        
        # SDK로 실시간 모델 목록 가져오기
        try:
            sdk_models = get_available_models_sdk()
            if sdk_models:
                display_models = sdk_models
                st.success(f"SDK에서 {len(sdk_models)}개 모델 조회됨")
            else:
                from init_dspy import available_models
                display_models = available_models
                st.warning("SDK 조회 실패, 기본 모델 목록 사용")
        except Exception as e:
            from init_dspy import available_models
            display_models = available_models
            st.error(f"모델 목록 조회 오류: {e}")
        
        # 현재 선택된 모델
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = "claude-sonnet-4-20250514"
        
        # 모델 선택 드롭다운
        selected_model = st.selectbox(
            "Claude 모델 선택",
            options=display_models,
            index=display_models.index(st.session_state.selected_model) if st.session_state.selected_model in display_models else 0,
            format_func=lambda x: f"{x} (SDK)" if x in sdk_models else f"{x} (기본)",
            help="분석에 사용할 Claude 모델을 선택하세요"
        )
        
        # 모델 변경 시 세션 상태만 업데이트 (DSPy 설정 변경 안함)
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.success(f"모델이 {selected_model}로 변경되었습니다!")
            
    except Exception as e:
        st.error(f"모델 설정 오류: {e}")
        st.info("기본 모델을 사용합니다.")



# ─── 초기화 ─────────────────────────────────────────────
init_user_state()



# ─── 1. 프로젝트 기본 정보 입력 (탭 위에 배치) ─────────────────────────

st.markdown("### 프로젝트 기본 정보")

# 접을 수 있는 섹션
with st.expander("프로젝트 정보 입력", expanded=st.session_state.get('show_project_info', True)):
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("프로젝트명", key="project_name", placeholder="예: Woori Bank Dasan Campus")
        st.text_input("건축주", key="owner", placeholder="예: Woori Bank")
        st.text_input("대지위치", key="site_location", placeholder="예: Namyangju-si, Gyeonggi-do")
        st.text_input("대지면적", key="site_area", placeholder="예: 30,396.0㎡ ")
    
    with col2:
        st.text_input("용적률", key="zoning", placeholder="예: General Residential Zone")
        st.text_input("건물용도", key="building_type", placeholder="예: Training Center")
        st.text_input("프로젝트 목표", key="project_goal", placeholder="예: Develop an innovative training campus...")
    
    # PDF 업로드
    uploaded_pdf = st.file_uploader("PDF 업로드", type=["pdf"])
    if uploaded_pdf:
        # PDF 처리 로직 (간단 저장만 사용)
        pdf_bytes = uploaded_pdf.read()
        temp_path = "temp_uploaded.pdf"
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        # 사용자별 PDF 저장
        current_user = st.session_state.get('current_user')
        if current_user and 'auth_system' in st.session_state:
            pdf_name = f"{current_user}_{uploaded_pdf.name.replace('.pdf', '')}"
            saved_pdf_path = st.session_state.auth_system.save_user_pdf(current_user, pdf_name, pdf_bytes)
            st.success(f"PDF가 사용자 폴더에 저장되었습니다: {saved_pdf_path}")
        
        # 간단 저장 사용
        if save_pdf_chunks_to_chroma(temp_path, pdf_id="projectA"):
            st.success("PDF 저장 완료!")
        else:
            st.error("PDF 저장 실패!")
        
        # PDF 텍스트 추출 및 요약 (기존 코드)
        from utils_pdf import extract_text_from_pdf
        from summary_generator import summarize_pdf, extract_site_analysis_fields, analyze_pdf_comprehensive, get_pdf_quality_report

        pdf_text = extract_text_from_pdf(pdf_bytes, "bytes")

        # 새로운 고급 분석 사용 (청크 분석)
        comprehensive_result = analyze_pdf_in_chunks(pdf_text)

        # 기존 호환성을 위한 처리
        pdf_summary = comprehensive_result["summary"]
        set_pdf_summary_to_session(pdf_summary)
        st.session_state["site_fields"] = comprehensive_result["site_fields"]

        # 새로운 고급 정보 저장
        st.session_state["pdf_analysis_result"] = comprehensive_result
        st.session_state["pdf_quality_report"] = get_pdf_quality_report(pdf_text)

        # 품질 정보 표시
        quality = comprehensive_result["quality"]
        if quality["grade"] in ["A+", "A"]:
            st.success("PDF 분석 품질: 우수")
        elif quality["grade"] in ["B+", "B"]:
            st.info("PDF 분석 품질: 양호")
        else:
            st.warning("PDF 분석 품질: 개선 필요")

        st.success("PDF 요약 완료!")
    
    # 정보 입력 완료 버튼
    if st.button("정보 입력 완료", type="primary"):
        st.session_state.show_project_info = False
        
        # 워크플로우 관련 상태 초기화
        st.session_state.workflow_steps = []
        st.session_state.removed_steps = set()
        st.session_state.added_steps = set()
        # current_step_index를 0으로 초기화하지 않고 기존 값 유지
        if 'current_step_index' not in st.session_state:
            st.session_state.current_step_index = 0
        st.session_state.analysis_started = False
        # cot_history를 초기화하지 않고 기존 값 유지
        if 'cot_history' not in st.session_state:
            st.session_state.cot_history = []
        st.session_state.ordered_blocks = []
        st.session_state.selected_purpose = None
        st.session_state.selected_objectives = []
        st.session_state.current_workflow = None
        
        # 자동 저장
        if save_user_data():
            st.success("프로젝트 정보 입력이 완료되었습니다! (자동 저장됨)")
        else:
            st.success("프로젝트 정보 입력이 완료되었습니다!")
        st.rerun()

# ─── 사이드바에 추가 선택 가능한 단계들 (프로젝트 정보 완료 후 표시) ─────────────────────────
if not st.session_state.get('show_project_info', True):
    st.sidebar.markdown("### 추가 선택 가능한 단계")
    
    # 프롬프트 블록 로드
    from dsl_to_prompt import load_prompt_blocks
    blocks = load_prompt_blocks()
    extra_blocks = blocks["extra"]
    
    # 현재 선택된 단계들 (editable_steps 기준으로 확인)
    current_step_ids = set()
    if st.session_state.get('editable_steps'):
        for step in st.session_state.editable_steps:
            current_step_ids.add(step.id)
    elif st.session_state.get('workflow_steps'):
        for step in st.session_state.workflow_steps:
            current_step_ids.add(step.id)
    
    # 추가된 단계들도 포함
    added_step_ids = st.session_state.get('added_steps', set())
    current_step_ids.update(added_step_ids)
    
    # 자동 제안된 단계들 (제외)
    auto_suggested_ids = set()
    if st.session_state.get('current_workflow'):
        from analysis_system import AnalysisSystem
        system = AnalysisSystem()
        selected_purpose = st.session_state.get('selected_purpose')
        selected_objectives = st.session_state.get('selected_objectives', [])
        
        if selected_purpose and selected_objectives:
            # 용도별 권장 단계들
            purpose_enum = None
            for purpose in system.recommended_steps.keys():
                if purpose.value == selected_purpose:
                    purpose_enum = purpose
                    break
            
            if purpose_enum:
                auto_suggested_ids.update({step.id for step in system.recommended_steps[purpose_enum]})
    
    # 자동 제안되지 않은 추가 선택 가능한 단계들만 필터링
    additional_blocks = []
    for block in extra_blocks:
        block_id = block["id"]
        if block_id not in auto_suggested_ids and block_id not in current_step_ids:
            additional_blocks.append(block)
    
    if additional_blocks:
        st.sidebar.write("**추가로 선택 가능한 단계**:")
        
        for block in additional_blocks:
            block_id = block["id"]
            
            # 선택 가능한 단계
            if st.sidebar.button(f"➕ {block['title']}", key=f"add_block_{block_id}"):
                # 단계 추가
                from analysis_system import AnalysisSystem, AnalysisStep
                system = AnalysisSystem()
                cot_order = system._load_recommended_cot_order()
                
                # 권장 순서에 따른 적절한 위치 찾기
                new_step_order = cot_order.get(block_id, 999)  # 기본값을 높게 설정
                
                new_step = AnalysisStep(
                    id=block_id,
                    title=block['title'],
                    description=block.get('description', ''),
                    is_optional=True,
                    order=new_step_order,
                    category="추가 단계"
                )
                
                # editable_steps에 추가 (메인 편집 인터페이스에 반영)
                if 'editable_steps' not in st.session_state:
                    st.session_state.editable_steps = []
                
                st.session_state.editable_steps.append(new_step)
                
                # workflow_steps에도 추가 (동기화)
                if 'workflow_steps' not in st.session_state:
                    st.session_state.workflow_steps = []
                
                st.session_state.workflow_steps.append(new_step)
                
                # 권장 순서로 재정렬 (editable_steps 기준)
                sorted_steps = system.sort_steps_by_recommended_order(st.session_state.editable_steps)
                for i, step in enumerate(sorted_steps, 1):
                    step.order = i
                
                # 두 리스트 모두 업데이트
                st.session_state.editable_steps = sorted_steps
                st.session_state.workflow_steps = sorted_steps.copy()
                
                # 성공 메시지 표시 (rerun 없이)
                st.sidebar.success(f"'{block['title']}' 단계가 권장 순서에 맞게 추가되었습니다!")
                
                # 추가된 단계 ID를 저장
                if 'added_steps' not in st.session_state:
                    st.session_state.added_steps = set()
                st.session_state.added_steps.add(block_id)
    else:
        st.sidebar.info("모든 관련 단계가 자동으로 선택되었습니다.")

# ─── 권장 CoT 순서 설명 ─────────────────────────
with st.expander("권장 CoT 순서 가이드", expanded=False):
    st.markdown("""
    ### 🎯 권장 분석 순서 (초기→중기→후기)
    
    **💡 왜 순서가 중요한가요?**
    
    건축 설계 분석은 논리적 사고 과정(Chain of Thought)을 따라야 합니다. 
    초기 단계에서 명확한 기반을 마련하고, 중기 단계에서 구체적 전략을 수립한 후, 
    후기 단계에서 실행 가능한 설계안을 도출하는 것이 핵심입니다.
    
    ---
    
    **🎯 1단계: 초기 분석 (기초 정보 수집 및 기본 분석)**
    
    1. **document_analyzer** — 문서 분석 및 건축주 의도 추론
    2. **requirement_analyzer** — 요구사항 종합 분석 및 전략 도출
    3. **task_comprehension** — 과업 이해 및 목표 설정
    4. **risk_strategist** — 리스크 분석 및 대응 전략
    5. **site_regulation_analysis** — 대지 환경 및 법규 분석
    6. **compliance_analyzer** — 규정 준수 및 적법성 분석
    
    **🔍 2단계: 중기 분석 (참고 자료 조사 및 설계 전략 수립)**
    
    7. **precedent_benchmarking** — 선진사례 벤치마킹 및 최적 운영전략
    8. **competitor_analyzer** — 경쟁사 분석 및 차별화 전략
    9. **design_trend_application** — 통합 디자인 트렌드 적용 전략
    10. **mass_strategy** — 건축설계 방향 및 매스(Mass) 전략
    11. **flexible_space_strategy** — 가변형 공간 및 확장성 전략
    12. **concept_development** — 설계 컨셉 개발 및 평가
    13. **area_programming** — 면적 프로그래밍 및 공간 배분
    14. **schematic_space_plan** — 스키매틱 공간 계획
    15. **ux_circulation_simulation** — 사용자 경험 및 동선 시뮬레이션
    
    **📋 3단계: 후기 분석 (종합 정리 및 실행 계획)**
    
    16. **design_requirement_summary** — 설계 요구사항 종합 요약
    17. **cost_estimation** — 비용 추정 및 경제성 분석
    18. **architectural_branding_identity** — 건축 브랜딩 및 정체성 전략
    19. **action_planner** — 실행 계획 및 액션 플랜
    20. **proposal_framework** — 제안서 프레임워크 및 작성 가이드
    
    ---
    
    **📊 각 단계별 특징**
    
    | 단계 | 블록 수 | 주요 목적 | 특징 |
    |------|---------|-----------|------|
    | **초기 분석** | 6개 | 기초 정보 수집 및 기본 분석 | 문서 분석, 요구사항 파악, 리스크 식별 |
    | **중기 분석** | 9개 | 참고 자료 조사 및 설계 전략 | 사례 조사, 설계 전략, 공간 계획 |
    | **후기 분석** | 5개 | 종합 정리 및 실행 계획 | 요약, 비용 분석, 실행 계획 |
    """)


# ─── 3. 새로운 탭 기반 인터페이스 ───────────────────────────
from workflow_ui import render_tabbed_interface

# 탭 기반 인터페이스 렌더링
render_tabbed_interface()


# PDF 업로드 시 디버깅 정보
if st.session_state.get('uploaded_pdf'):
    st.sidebar.success("PDF 업로드 완료")
    
    # PDF 처리 상태 확인
    if st.session_state.get("pdf_summary"):
        st.sidebar.success("PDF 요약 완료")
    else:
        st.sidebar.warning("PDF 요약 처리 중...")
    
    # PDF 처리 상태 확인
    if st.session_state.get("pdf_chunks"):
        st.sidebar.success("PDF 텍스트 저장 완료")
    else:
        st.sidebar.warning("PDF 텍스트 처리 중...")

# Rate Limit 경고
if st.session_state.get("api_calls", 0) > 10:
    st.sidebar.warning("API 호출이 많습니다. 잠시 대기해주세요.")

# Rate Limit 오류 발생 시 대기 후 재시도
if "rate_limit_wait" not in st.session_state:
    st.session_state.rate_limit_wait = False

if st.session_state.rate_limit_wait:
    st.warning("Rate Limit으로 인해 1분 대기 중입니다...")
    time.sleep(60)
    st.session_state.rate_limit_wait = False
    st.rerun()
