# user_state.py
import streamlit as st
import json
from datetime import datetime
import os

def init_user_state():
    """사용자 상태 초기화 - 로그인된 사용자의 기존 데이터 로드"""
    current_user = st.session_state.get('current_user')
    
    if current_user and 'auth_system' in st.session_state:
        # 기존 사용자 데이터 로드
        saved_data = st.session_state.auth_system.load_user_session_data(current_user)
        
        # 기본값 설정 (저장된 데이터가 있으면 사용, 없으면 기본값)
        if "pdf_summary" not in st.session_state:
            st.session_state.pdf_summary = saved_data.get("pdf_summary", "")
        
        if "user_inputs" not in st.session_state:
            st.session_state.user_inputs = saved_data.get("user_inputs", {
                "project_name": "",
                "owner": "",
                "site_location": "",
                "site_area": "",
                "zoning": "",
                "building_type": "",
                "project_goal": "",
            })
        
        if "step_results" not in st.session_state:
            st.session_state.step_results = saved_data.get("step_results", {})
        
        if "cot_history" not in st.session_state:
            st.session_state.cot_history = saved_data.get("cot_history", [])
        
        if "step_history" not in st.session_state:
            st.session_state.step_history = saved_data.get("step_history", [])
        
        if "current_step_index" not in st.session_state:
            st.session_state.current_step_index = saved_data.get("current_step_index", 0)
        
        # 워크플로우 관련 상태 초기화
        if "workflow_steps" not in st.session_state:
            saved_workflow_steps = saved_data.get("workflow_steps", [])
            st.session_state.workflow_steps = convert_workflow_steps_from_dict(saved_workflow_steps)
        
        if "removed_steps" not in st.session_state:
            st.session_state.removed_steps = set(saved_data.get("removed_steps", []))
        
        if "added_steps" not in st.session_state:
            st.session_state.added_steps = set(saved_data.get("added_steps", []))
        
        if "analysis_started" not in st.session_state:
            st.session_state.analysis_started = saved_data.get("analysis_started", False)
        
        if "analysis_completed" not in st.session_state:
            st.session_state.analysis_completed = saved_data.get("analysis_completed", False)
        
        if "show_next_step_button" not in st.session_state:
            st.session_state.show_next_step_button = saved_data.get("show_next_step_button", False)
        
        if "current_step_display_data" not in st.session_state:
            st.session_state.current_step_display_data = saved_data.get("current_step_display_data", None)
        
        if "current_step_outputs" not in st.session_state:
            st.session_state.current_step_outputs = saved_data.get("current_step_outputs", {})
        
        if "web_search_settings" not in st.session_state:
            st.session_state.web_search_settings = saved_data.get("web_search_settings", {})
        
        if "uploaded_pdf" not in st.session_state:
            st.session_state.uploaded_pdf = saved_data.get("uploaded_pdf", None)
        
        if "site_fields" not in st.session_state:
            st.session_state.site_fields = saved_data.get("site_fields", {})
        
        if "pdf_analysis_result" not in st.session_state:
            st.session_state.pdf_analysis_result = saved_data.get("pdf_analysis_result", {})
        
        if "pdf_quality_report" not in st.session_state:
            st.session_state.pdf_quality_report = saved_data.get("pdf_quality_report", {})
        
        if "selected_purpose" not in st.session_state:
            st.session_state.selected_purpose = saved_data.get("selected_purpose", None)
        
        if "selected_objectives" not in st.session_state:
            st.session_state.selected_objectives = saved_data.get("selected_objectives", [])
        
        if "analysis_system" not in st.session_state:
            from analysis_system import AnalysisSystem
            st.session_state.analysis_system = AnalysisSystem()
        
        # 마지막 로드 시간 기록
        st.session_state.last_data_load = datetime.now().isoformat()
        
        st.success(f"👋 {current_user}님의 기존 데이터를 불러왔습니다!")
    else:
        # 로그인되지 않은 경우 기본 초기화
        if "pdf_summary" not in st.session_state:
            st.session_state.pdf_summary = ""
        if "user_inputs" not in st.session_state:
            st.session_state.user_inputs = {
                "project_name": "",
                "owner": "",
                "site_location": "",
                "site_area": "",
                "zoning": "",
                "building_type": "",
                "project_goal": "",
            }
        if "step_results" not in st.session_state:
            st.session_state.step_results = {}
        if "cot_history" not in st.session_state:
            st.session_state.cot_history = []
        if "step_history" not in st.session_state:
            st.session_state.step_history = []
        if "current_step_index" not in st.session_state:
            st.session_state.current_step_index = 0
        
        # 워크플로우 관련 상태 초기화
        if "workflow_steps" not in st.session_state:
            st.session_state.workflow_steps = []
        if "removed_steps" not in st.session_state:
            st.session_state.removed_steps = set()
        if "added_steps" not in st.session_state:
            st.session_state.added_steps = set()
        if "analysis_started" not in st.session_state:
            st.session_state.analysis_started = False
        if "analysis_completed" not in st.session_state:
            st.session_state.analysis_completed = False
        if "show_next_step_button" not in st.session_state:
            st.session_state.show_next_step_button = False
        if "current_step_display_data" not in st.session_state:
            st.session_state.current_step_display_data = None
        if "current_step_outputs" not in st.session_state:
            st.session_state.current_step_outputs = {}
        if "web_search_settings" not in st.session_state:
            st.session_state.web_search_settings = {}
        if "uploaded_pdf" not in st.session_state:
            st.session_state.uploaded_pdf = None
        if "site_fields" not in st.session_state:
            st.session_state.site_fields = {}
        if "pdf_analysis_result" not in st.session_state:
            st.session_state.pdf_analysis_result = {}
        if "pdf_quality_report" not in st.session_state:
            st.session_state.pdf_quality_report = {}
        if "selected_purpose" not in st.session_state:
            st.session_state.selected_purpose = None
        if "selected_objectives" not in st.session_state:
            st.session_state.selected_objectives = []
        if "analysis_system" not in st.session_state:
            from analysis_system import AnalysisSystem
            st.session_state.analysis_system = AnalysisSystem()

def convert_analysis_step_to_dict(step):
    """AnalysisStep 객체를 딕셔너리로 변환"""
    if hasattr(step, '__dict__'):
        return {
            'id': step.id,
            'title': step.title,
            'description': step.description,
            'is_required': step.is_required,
            'is_recommended': step.is_recommended,
            'is_optional': step.is_optional,
            'order': step.order,
            'category': step.category,
            'dependencies': step.dependencies
        }
    return step

def convert_workflow_steps_to_dict(workflow_steps):
    """워크플로우 스텝들을 딕셔너리로 변환"""
    if not workflow_steps:
        return []
    
    converted_steps = []
    for step in workflow_steps:
        if hasattr(step, 'id'):  # AnalysisStep 객체인지 확인
            converted_steps.append(convert_analysis_step_to_dict(step))
        else:
            converted_steps.append(step)
    
    return converted_steps

def convert_dict_to_analysis_step(step_dict):
    """딕셔너리를 AnalysisStep 객체로 변환"""
    if isinstance(step_dict, dict) and 'id' in step_dict:
        from analysis_system import AnalysisStep
        return AnalysisStep(
            id=step_dict['id'],
            title=step_dict['title'],
            description=step_dict['description'],
            is_required=step_dict.get('is_required', False),
            is_recommended=step_dict.get('is_recommended', False),
            is_optional=step_dict.get('is_optional', False),
            order=step_dict.get('order', 0),
            category=step_dict.get('category', ''),
            dependencies=step_dict.get('dependencies', [])
        )
    return step_dict

def convert_workflow_steps_from_dict(workflow_steps_dict):
    """딕셔너리 리스트를 AnalysisStep 객체 리스트로 변환"""
    if not workflow_steps_dict:
        return []
    
    converted_steps = []
    for step in workflow_steps_dict:
        converted_steps.append(convert_dict_to_analysis_step(step))
    
    return converted_steps

def save_user_data():
    """사용자 데이터 저장"""
    current_user = st.session_state.get('current_user')
    if not current_user or 'auth_system' not in st.session_state:
        return False
    
    # 저장할 데이터 준비
    session_data = {
        "pdf_summary": st.session_state.get("pdf_summary", ""),
        "user_inputs": st.session_state.get("user_inputs", {}),
        "step_results": st.session_state.get("step_results", {}),
        "cot_history": st.session_state.get("cot_history", []),
        "step_history": st.session_state.get("step_history", []),
        "current_step_index": st.session_state.get("current_step_index", 0),
        "workflow_steps": convert_workflow_steps_to_dict(st.session_state.get("workflow_steps", [])),  # 변환 추가
        "removed_steps": list(st.session_state.get("removed_steps", set())),
        "added_steps": list(st.session_state.get("added_steps", set())),
        "analysis_started": st.session_state.get("analysis_started", False),
        "analysis_completed": st.session_state.get("analysis_completed", False),
        "show_next_step_button": st.session_state.get("show_next_step_button", False),
        "current_step_display_data": st.session_state.get("current_step_display_data", None),
        "current_step_outputs": st.session_state.get("current_step_outputs", {}),
        "web_search_settings": st.session_state.get("web_search_settings", {}),
        "uploaded_pdf": st.session_state.get("uploaded_pdf", None),
        "site_fields": st.session_state.get("site_fields", {}),
        "pdf_analysis_result": st.session_state.get("pdf_analysis_result", {}),
        "pdf_quality_report": st.session_state.get("pdf_quality_report", {}),
        "selected_purpose": st.session_state.get("selected_purpose", None),
        "selected_objectives": st.session_state.get("selected_objectives", []),
        "last_saved": datetime.now().isoformat()
    }
    
    try:
        st.session_state.auth_system.save_user_session_data(current_user, session_data)
        return True
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {e}")
        return False

def get_user_inputs():
    """st.session_state에서 직접 프로젝트 정보를 가져옴"""
    return {
        "project_name": st.session_state.get("project_name", ""),
        "owner": st.session_state.get("owner", ""),
        "site_location": st.session_state.get("site_location", ""),
        "site_area": st.session_state.get("site_area", ""),
        "zoning": st.session_state.get("zoning", ""),
        "building_type": st.session_state.get("building_type", ""),
        "project_goal": st.session_state.get("project_goal", "")
    }

def save_step_result(step_id: str, result: str):
    st.session_state.step_results[step_id] = result
    # 자동 저장
    save_user_data()

def append_step_history(step_id: str, title: str, prompt: str, result: str):
    st.session_state.step_history.append({
        "id": step_id,
        "title": title,
        "prompt": prompt,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })
    # 자동 저장
    save_user_data()

def get_current_step_index() -> int:
    return st.session_state.current_step_index

def reset_workflow_state():
    """워크플로우 상태 초기화"""
    st.session_state.workflow_steps = []
    st.session_state.removed_steps = set()
    st.session_state.added_steps = set()
    st.session_state.analysis_started = False
    st.session_state.analysis_completed = False
    # current_step_index를 0으로 초기화하지 않고 기존 값 유지
    if 'current_step_index' not in st.session_state:
        st.session_state.current_step_index = 0
    # cot_history를 초기화하지 않고 기존 값 유지
    if 'cot_history' not in st.session_state:
        st.session_state.cot_history = []
    st.session_state.show_next_step_button = False
    st.session_state.current_step_display_data = None
    st.session_state.current_step_outputs = {}
    # 자동 저장
    save_user_data()

def get_user_project_list():
    """사용자의 프로젝트 목록 반환"""
    current_user = st.session_state.get('current_user')
    if not current_user or 'auth_system' not in st.session_state:
        return []
    
    return st.session_state.auth_system.get_user_analysis_results(current_user)

def save_current_project(project_name):
    """현재 프로젝트를 지정된 이름으로 저장"""
    current_user = st.session_state.get('current_user')
    if not current_user or 'auth_system' not in st.session_state:
        return False
    
    project_data = {
        "project_name": project_name,
        "user_inputs": get_user_inputs(),
        "cot_history": st.session_state.get("cot_history", []),
        "step_history": st.session_state.get("step_history", []),
        "pdf_summary": st.session_state.get("pdf_summary", ""),
        "site_fields": st.session_state.get("site_fields", {}),
        "pdf_analysis_result": st.session_state.get("pdf_analysis_result", {}),
        "created_at": datetime.now().isoformat()
    }
    
    try:
        st.session_state.auth_system.save_user_analysis_result(current_user, project_name, project_data)
        return True
    except Exception as e:
        st.error(f"프로젝트 저장 중 오류 발생: {e}")
        return False

def load_project(project_name):
    """지정된 프로젝트 로드"""
    current_user = st.session_state.get('current_user')
    if not current_user or 'auth_system' not in st.session_state:
        return False
    
    try:
        user_path = st.session_state.auth_system.get_user_data_path(current_user)
        project_file = os.path.join(user_path, "analysis_results", f"{project_name}.json")
        
        if os.path.exists(project_file):
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 세션 상태 업데이트
            st.session_state.user_inputs = project_data.get("user_inputs", {})
            st.session_state.cot_history = project_data.get("cot_history", [])
            st.session_state.step_history = project_data.get("step_history", [])
            st.session_state.pdf_summary = project_data.get("pdf_summary", "")
            st.session_state.site_fields = project_data.get("site_fields", {})
            st.session_state.pdf_analysis_result = project_data.get("pdf_analysis_result", {})
            
            # 프로젝트 정보를 세션 상태에 설정
            for key, value in st.session_state.user_inputs.items():
                st.session_state[key] = value
            
            return True
        else:
            st.error(f"프로젝트 '{project_name}'을 찾을 수 없습니다.")
            return False
    except Exception as e:
        st.error(f"프로젝트 로드 중 오류 발생: {e}")
        return False

