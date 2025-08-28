#prompt_loader.py

import json

# ✅ 핵심 원칙 선언 블록 (항상 맨 앞에 삽입됨)
CORE_PRINCIPLES_BLOCK = {
    "id": "core_principles",
    "title": "핵심 원칙 선언 및 유의사항",
    "content": """📌 (AI 추론을 통한 분석 결과:)
    1. **건축주 중심 접근**: 입력된 정보를 바탕으로 건축주의 명시적, 암묵적 니즈를 모두 파악합니다.
    2. **데이터 기반 추론**: '~인 것으로 보입니다', '~를 원하시는 것 같습니다' 등 부드러운 표현을 사용하되, 모든 추론은 분석된 데이터에 근거합니다.
    3. **사례 기반 제안**: 구체적인 국내외 사례 조사를 통해 실증적 근거를 제시합니다.
    4. **단계별 심화 분석**: 각 단계의 분석 결과를 다음 단계에 누적 반영하여 분석의 깊이를 더합니다.
    """
}


def load_prompt_blocks(json_path="prompt_blocks_dsl.json"):
    """
    고정 블럭(core)은 따로, 나머지 분석 블럭은 따로 리턴.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # JSON에서 default_intro 로드
    default_intro = data.get("default_intro", {})
    core = [default_intro] if default_intro else []
    
    # JSON에 정의된 나머지 블럭
    extra = data["blocks"] if isinstance(data, dict) else []
    return {
        "core": core,      # 리스트 형태
        "extra": extra     # 리스트 형태
    }



def dsl_to_content(dsl: dict) -> str:
    """
    content_dsl 형식을 일반 텍스트 content로 변환
    """
    lines = [f"(AI 추론을 통한 분석 결과:)"]

    if "goal" in dsl:
        lines.append(f"\n목표: {dsl['goal']}")
    
    if "role" in dsl:
        lines.append(f"\n역할: {dsl['role']}")
    
    if "context" in dsl:
        lines.append(f"\n맥락: {dsl['context']}")
    
    if "source" in dsl:
        sources = ", ".join(dsl["source"])
        lines.append(f"\n정보 출처: {sources}")
    
    if "tasks" in dsl:
        lines.append("\n주요 분석 항목:")
        for t in dsl["tasks"]:
            lines.append(f"- {t}")
    
    # analysis_framework 처리
    if "analysis_framework" in dsl:
        framework = dsl["analysis_framework"]
        lines.append(f"\n분석 프레임워크:")
        if "approach" in framework:
            lines.append(f"- 접근 방식: {framework['approach']}")
        if "methodology" in framework:
            lines.append(f"- 방법론: {framework['methodology']}")
        if "criteria" in framework:
            lines.append("- 평가 기준:")
            for criterion in framework["criteria"]:
                lines.append(f"  • {criterion}")
    
    # output_structure 처리
    if "output_structure" in dsl:
        lines.append(f"\n출력 구조:")
        for structure in dsl["output_structure"]:
            lines.append(f"- {structure}")
    
    # quality_standards 처리
    if "quality_standards" in dsl:
        quality = dsl["quality_standards"]
        lines.append(f"\n⚠️ 품질 기준:")
        if "constraints" in quality:
            lines.append("- 제약사항:")
            for constraint in quality["constraints"]:
                lines.append(f"  • {constraint}")
        if "required_phrases" in quality:
            lines.append(f"- 필수 포함 문구: {', '.join(quality['required_phrases'])}")
        if "validation_rules" in quality:
            lines.append("- 검증 규칙:")
            for rule in quality["validation_rules"]:
                lines.append(f"  • {rule}")
    
    # presentation 처리
    if "presentation" in dsl:
        presentation = dsl["presentation"]
        lines.append(f"\n💡 프레젠테이션:")
        if "language_tone" in presentation:
            lines.append(f"- 언어 톤: {presentation['language_tone']}")
        if "target_format" in presentation:
            lines.append(f"- 목표 형식: {presentation['target_format']}")
        if "visual_elements" in presentation:
            lines.append(f"- 시각 요소: {', '.join(presentation['visual_elements'])}")

    return "\n".join(lines)