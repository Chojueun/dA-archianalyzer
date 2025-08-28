from utils_pdf import search_pdf_chunks  # 통합된 PDF 모듈 사용
from search_helper import search_web_serpapi  # 주석 해제

def get_web_search_for_block(block_id: str, user_inputs: dict) -> str:
    """각 블록별로 관련된 웹 검색 수행"""
    
    # 블록별 검색 쿼리 매핑
    search_queries = {
        "requirement_analyzer": [  # requirement_analysis → requirement_analyzer로 수정
            f"{user_inputs.get('building_type', '건축')} 요구사항 분석 2024",
            f"{user_inputs.get('building_type', '건축')} 설계 가이드라인"
        ],
        "precedent_benchmarking": [
            f"{user_inputs.get('building_type', '건축')} 사례 2024",
            f"{user_inputs.get('building_type', '건축')} 벤치마킹"
        ],
        "design_trend_application": [
            "건축 디자인 트렌드 2024",
            "건축 기술 트렌드 2024"
        ],
        "cost_estimation": [
            "건축 공사비 트렌드 2024",
            "건축 원가 분석 2024"
        ],
        "mass_strategy": [
            "건축 매스 전략 2024",
            "건축 설계 트렌드 2024"
        ],

    }
    
    queries = search_queries.get(block_id, ["건축 분석 2024"])
    
    all_results = []
    for query in queries:
        try:
            result = search_web_serpapi(query)
            if result and result != "[검색 API 키 없음]":
                all_results.append(f"검색어: {query}\n{result}")
        except Exception as e:
            print(f"웹 검색 실패 ({query}): {e}")
    
    return "\n\n".join(all_results) if all_results else ""

def convert_dsl_to_prompt(
    dsl_block: dict,
    user_inputs: dict,
    previous_summary: str = "",
    pdf_summary: dict = None,
    site_fields: dict = None,
    include_web_search: bool = True
) -> str:
    """완전히 개선된 DSL을 프롬프트로 변환"""
    
    dsl = dsl_block.get("content_dsl", {})
    prompt_parts = []
    
    # 0. 블록 ID 및 제목 명시 (새로 추가)
    block_id = dsl_block.get("id", "")
    block_title = dsl_block.get("title", "")
    prompt_parts.append(f"# 현재 분석 블록\n")
    prompt_parts.append(f"**블록 ID:** {block_id}\n")
    prompt_parts.append(f"**블록 제목:** {block_title}\n")
    prompt_parts.append(f"**분석 목적:** 이 블록만의 고유한 분석을 수행하세요.\n\n")
    
    # 1. 기본 역할 및 목표
    prompt_parts.append(f"# 분석 목표\n{dsl.get('goal', '')}")
    prompt_parts.append(f"# 역할\n{dsl.get('role', '건축 분석 전문가')}")
    
    if dsl.get('context'):
        prompt_parts.append(f"# 맥락\n{dsl['context']}")
    
    # 2. 분석 프레임워크
    framework = dsl.get('analysis_framework', {})
    if framework:
        framework_text = f"# 분석 프레임워크\n"
        framework_text += f"접근 방식: {framework.get('approach', '')}\n"
        framework_text += f"방법론: {framework.get('methodology', '')}\n"
        
        criteria = framework.get('criteria', [])
        if criteria:
            framework_text += f"\n평가 기준:\n"
            for i, criterion in enumerate(criteria, 1):
                framework_text += f"{i}. {criterion}\n"
        
        prompt_parts.append(framework_text)
    
    # 3. 작업 목록
    tasks = dsl.get('tasks', [])
    if tasks:
        tasks_text = f"# 📋 주요 분석 작업\n"
        for i, task in enumerate(tasks, 1):
            tasks_text += f"{i}. {task}\n"
        prompt_parts.append(tasks_text)
    
    # 4. 품질 기준 - 확장된 버전
    quality = dsl.get('quality_standards', {})
    if quality:
        quality_text = f"# ⚠️ 품질 기준\n"
        
        constraints = quality.get('constraints', [])
        if constraints:
            quality_text += f"제약사항:\n"
            for constraint in constraints:
                quality_text += f"- {constraint}\n"
        
        required_phrases = quality.get('required_phrases', [])
        if required_phrases:
            quality_text += f"\n필수 포함 문구: {', '.join(required_phrases)}\n"
        
        validation_rules = quality.get('validation_rules', [])
        if validation_rules:
            quality_text += f"\n검증 규칙:\n"
            for rule in validation_rules:
                quality_text += f"- {rule}\n"
        
        prompt_parts.append(quality_text)
    
    # 5. 출력 형식 - 대폭 확장된 버전
    presentation = dsl.get('presentation', {})
    if presentation:
        presentation_text = f"# 📋 출력 형식\n"
        presentation_text += f"언어 톤: {presentation.get('language_tone', '')}\n"
        presentation_text += f"형식: {presentation.get('target_format', '')}\n"
        
        # 새로 추가된 explanatory_template 처리
        explanatory_template = presentation.get('explanatory_template', '')
        if explanatory_template:
            presentation_text += f"해설 템플릿: {explanatory_template}\n"
        
        visual_elements = presentation.get('visual_elements', [])
        if visual_elements:
            presentation_text += f"시각 요소: {', '.join(visual_elements)}\n"
        
        # 새로 추가된 section_templates 처리 - 대폭 확장
        section_templates = presentation.get('section_templates', {})
        if section_templates:
            presentation_text += f"\n## 📋 섹션별 상세 템플릿:\n"
            for section_name, template in section_templates.items():
                presentation_text += f"\n### {section_name}:\n"
                
                # table_title 처리
                table_title = template.get('table_title', '')
                if table_title:
                    presentation_text += f"- **표 제목:** {table_title}\n"
                
                # required_columns 처리 - 배열 형태로 확장
                required_columns = template.get('required_columns', [])
                if required_columns:
                    presentation_text += f"- **필수 컬럼:**\n"
                    for i, column in enumerate(required_columns, 1):
                        if isinstance(column, str):
                            presentation_text += f"  {i}. {column}\n"
                        else:
                            presentation_text += f"  {i}. {column}\n"
                
                # narrative_template 처리
                narrative_template = template.get('narrative_template', '')
                if narrative_template:
                    presentation_text += f"- **해설 템플릿:** {narrative_template}\n"
                
                # diagram_title 처리 (새로 추가)
                diagram_title = template.get('diagram_title', '')
                if diagram_title:
                    presentation_text += f"- **다이어그램 제목:** {diagram_title}\n"
        
        prompt_parts.append(presentation_text)
    
    # 6. 프로젝트 기본 정보
    project_info = f"# 프로젝트 기본 정보\n"
    project_info += f"- 프로젝트명: {user_inputs.get('project_name', 'N/A')}\n"
    project_info += f"- 소유자: {user_inputs.get('owner', 'N/A')}\n"
    project_info += f"- 위치: {user_inputs.get('site_location', 'N/A')}\n"
    project_info += f"- 면적: {user_inputs.get('site_area', 'N/A')}\n"
    project_info += f"- 건물유형: {user_inputs.get('building_type', 'N/A')}\n"
    project_info += f"- 프로젝트 목표: {user_inputs.get('project_goal', 'N/A')}\n"
    prompt_parts.append(project_info)
    
    # 7. 사이트 분석 정보
    if site_fields:
        site_text = f"# 사이트 분석 정보\n"
        for key, value in site_fields.items():
            if value and str(value).strip():
                readable_key = key.replace('_', ' ').title()
                site_text += f"- {readable_key}: {value}\n"
        prompt_parts.append(site_text)
    
    # 8. 출력 구조 - 강화된 버전
    output_structure = dsl.get('output_structure', [])
    if output_structure:
        structure_text = f"# 📋 출력 구조\n"
        structure_text += f"**중요: 이 블록({block_title})의 고유한 분석만 수행하세요.**\n\n"
        structure_text += f"다음 구조로 분석 결과를 제공하세요. 각 구조는 반드시 지정된 형식으로 작성하세요:\n\n"
        
        for i, structure in enumerate(output_structure, 1):
            structure_text += f"## {i}. {structure}\n"
            structure_text += f"[{structure}에 해당하는 내용만 여기에 작성]\n\n"
        
        structure_text += f"⚠️ **중요 지시사항:**\n"
        structure_text += f"1. 각 구조는 반드시 '## 번호. 구조명' 형식으로 시작하세요\n"
        structure_text += f"2. 각 구조의 내용은 해당 구조에만 관련된 내용으로 작성하세요\n"
        structure_text += f"3. 모든 구조를 빠짐없이 작성하되, 내용이 중복되지 않도록 하세요\n"
        structure_text += f"4. 구조 간 구분을 명확히 하세요\n"
        structure_text += f"5. 각 구조는 독립적으로 완성된 내용이어야 합니다\n"
        structure_text += f"6. **이 블록의 고유한 분석만 수행하고, 다른 블록의 내용을 포함하지 마세요**\n\n"
        
        prompt_parts.append(structure_text)
    
    # 9. 이전 분석 결과
    if previous_summary:
        prompt_parts.append(f"# 📚 이전 분석 결과\n{previous_summary}\n")
    
    # 10. PDF 요약
    if pdf_summary:
        prompt_parts.append(f"# 📄 PDF 문서 요약\n{pdf_summary}\n")
    
    # 11. 웹 검색 결과
    if include_web_search:
        web_search_results = get_web_search_for_block(dsl_block.get("id", ""), user_inputs)
        if web_search_results:
            web_search_text = f"# 🌐 최신 웹 검색 결과\n{web_search_results}\n"
            prompt_parts.append(web_search_text)
    
    return "\n\n".join(prompt_parts)

# 단계별 특화된 프롬프트 함수들 - 확장된 버전
def prompt_requirement_table(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """요구사항 분석 프롬프트 (웹 검색 포함)"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    
    # 웹 검색 결과가 있으면 추가 지시사항
    if "🌐 최신 웹 검색 결과" in base_prompt:
        base_prompt += "\n\n⚠️ 위의 최신 웹 검색 결과를 참고하여 요구사항을 분석해주세요. 최신 트렌드와 가이드라인을 반영한 현실적인 요구사항을 제시해주세요."
    
    return base_prompt + "\n\n⚠️ 반드시 '요구사항 정리표' 항목만 표로 생성. 그 외 항목은 출력하지 마세요."

def prompt_ai_reasoning(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    base = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields)
    output_structure = dsl_block.get("content_dsl", {}).get("output_structure", [])
    
    if output_structure and len(output_structure) >= 2:
        target = output_structure[1]  # 두 번째 출력 구조
        return base + f"\n\n⚠️ 반드시 '{target}' 항목만 생성. 그 외 항목은 출력하지 마세요."
    else:
        return base + f"\n\n⚠️ 반드시 'AI 추론 해설' 항목만 생성. 그 외 항목은 출력하지 마세요."

def prompt_precedent_comparison(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """사례 비교 프롬프트 (웹 검색 포함)"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    
    # 웹 검색 결과가 있으면 추가 지시사항
    if "🌐 최신 웹 검색 결과" in base_prompt:
        base_prompt += "\n\n⚠️ 위의 최신 웹 검색 결과에 포함된 사례들을 참고하여 비교 분석해주세요. 최신 사례와 트렌드를 반영한 비교를 제공해주세요."
    
    return base_prompt + "\n\n⚠️ 반드시 '유사 사례 비교' 표 또는 비교 해설만 출력. 그 외 항목은 출력하지 마세요."

def prompt_strategy_recommendation(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """전략 제언 프롬프트 (웹 검색 포함)"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    
    # 웹 검색 결과가 있으면 추가 지시사항
    if "🌐 최신 웹 검색 결과" in base_prompt:
        base_prompt += "\n\n⚠️ 위의 최신 웹 검색 결과를 바탕으로 현실적이고 실행 가능한 전략을 제시해주세요. 최신 트렌드와 시장 동향을 반영한 전략적 제언을 해주세요."
    
    return base_prompt + "\n\n⚠️ 반드시 '전략적 제언 및 시사점'만 출력. 그 외 항목은 출력하지 마세요."

# 새로운 블록별 특화 함수들 추가
def prompt_task_comprehension(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """과업 이해도 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 과업 이해도 및 설계 주안점에 집중하여 분석하세요."

def prompt_site_regulation_analysis(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """대지 환경 및 법규 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 대지 환경 및 법규 분석에 집중하여 분석하세요."

def prompt_precedent_benchmarking(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """선진사례 벤치마킹 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 선진사례 벤치마킹 및 최적 운영전략에 집중하여 분석하세요."

def prompt_design_trend_application(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """디자인 트렌드 적용 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 통합 디자인 트렌드 적용 전략에 집중하여 분석하세요."

def prompt_mass_strategy(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """매스 전략 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 건축설계 방향 및 매스(Mass) 전략에 집중하여 분석하세요."

def prompt_concept_development(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """컨셉 개발 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 설계 컨셉 도출 및 평가에 집중하여 분석하세요."

def prompt_schematic_space_plan(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """스키매틱 공간 계획 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 평면·단면 스키매틱 및 공간 계획에 집중하여 분석하세요."

def prompt_design_requirement_summary(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """설계 요구사항 요약 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 최종 설계 요구사항 및 가이드라인에 집중하여 분석하세요."

def prompt_area_programming(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """면적 프로그래밍 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 면적 산출 및 공간 배분 전략에 집중하여 분석하세요."

def prompt_cost_estimation(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """비용 및 경제성 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 비용 및 경제성 분석(공사비 예측, 운영비 분석, 투자수익률 등)에 집중하여 분석하세요."

def prompt_architectural_branding_identity(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """건축적 브랜딩 정체성 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 건축적 차별화·브랜딩·정체성 전략에 집중하여 분석하세요."

def prompt_ux_circulation_simulation(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """사용자 동선 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 사용자 동선 분석 및 시나리오별 공간 최적화 전략에 집중하여 분석하세요."

def prompt_flexible_space_strategy(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """가변형 공간 전략 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 가변형 공간·프로그램 유연성 및 확장성 설계 전략에 집중하여 분석하세요."

# 문서 분석 관련 새로운 함수들
def prompt_doc_collector(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """문서 구조 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 문서 구조 및 요구사항 매트릭스화에 집중하여 분석하세요."

def prompt_context_analyzer(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """문맥 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 건축주 의도 및 문맥 AI 추론에 집중하여 분석하세요."

def prompt_requirements_extractor(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """요구사항 추출 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 요구사항 분류 및 우선순위 도출에 집중하여 분석하세요."

def prompt_compliance_analyzer(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """법규 준수 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 법규·지침 준수 체크에 집중하여 분석하세요."

def prompt_risk_strategist(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """리스크 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 주요 리스크 도출 및 대응에 집중하여 분석하세요."

def prompt_action_planner(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """액션 플래너 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 실행 체크리스트 및 핵심 포인트에 집중하여 분석하세요."

def prompt_competitor_analyzer(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """경쟁사 분석 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 경쟁사 분석 및 차별화 전략에 집중하여 분석하세요."

def prompt_proposal_framework(dsl_block, user_inputs, previous_summary="", pdf_summary=None, site_fields=None):
    """제안서 프레임워크 프롬프트"""
    base_prompt = convert_dsl_to_prompt(dsl_block, user_inputs, previous_summary, pdf_summary, site_fields, include_web_search=True)
    return base_prompt + "\n\n⚠️ 제안서 프레임워크 설계에 집중하여 분석하세요."

