
#utils.py

import re
from typing import Dict, Any
import streamlit as st
from datetime import datetime


def extract_summary(result: str, max_length: int = 300) -> str:
    """
    전체 Claude 출력 텍스트에서 동적 길이 요약을 자동 추출
    """
    # 1. 더 많은 섹션 키워드로 우선순위 검색
    section_keywords = [
        "요구사항 분석", "핵심 요약", "요약", "결론",
        "주요 내용", "핵심 내용", "분석 결과",
        "Summary", "Conclusion", "Key Points"
    ]
    
    for keyword in section_keywords:
        if keyword in result:
            m = re.search(rf"({keyword}.*?)\n\n", result, re.DOTALL)
            if m:
                extracted = m.group(1).strip()
                return adjust_length(extracted, max_length)

    # 2. 동적 길이 조절로 기본 제공
    return adjust_length(result.strip(), max_length)


def adjust_length(text: str, max_length: int) -> str:
    """
    텍스트 길이를 동적으로 조절
    """
    if len(text) <= max_length:
        return text
    elif len(text) < 500:
        return text[:max_length] + "..."
    elif len(text) < 1000:
        return text[:500] + "..."
    else:
        return text[:max_length] + "..."


def extract_insight(result: str) -> str:
    """
    GPT 출력 텍스트에서 전략 제언 또는 시사점 섹션을 추출 (향상된 버전)
    """
    # 더 많은 인사이트 키워드
    insight_keywords = [
        "전략적 제언", "시사점", "권장사항", "제안사항",
        "핵심 제언", "주요 제언", "실행 방안", "전략 제안",
        "Insight", "Recommendation", "Strategy", "Suggestion"
    ]
    
    for keyword in insight_keywords:
        if keyword in result:
            # 더 정교한 패턴 매칭
            patterns = [
                rf"({keyword}.*?)\n\n",
                rf"({keyword}.*?)(?=\n#|\n##|\n###)",
                rf"({keyword}.*?)(?=\n\n[A-Z가-힣])"
            ]
            
            for pattern in patterns:
                m = re.search(pattern, result, re.DOTALL)
                if m:
                    return m.group(1).strip()

    # fallback
    return "※ 전략적 제언 항목이 명확히 감지되지 않았습니다."


def extract_text_from_pdf(pdf_bytes) -> str:
    """
    PDF 바이트에서 전체 텍스트를 추출한다.
    """
    import fitz
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])


def assess_result_quality(result: str) -> Dict[str, Any]:
    """
    분석 결과 품질 평가 (추가 기능)
    """
    quality_metrics = {
        "length": len(result),
        "has_summary": any(keyword in result for keyword in ["요약", "Summary", "결론"]),
        "has_insight": any(keyword in result for keyword in ["제언", "Insight", "권장사항"]),
        "has_structure": result.count("\n\n") > 5,
        "has_bullet_points": result.count("- ") > 3 or result.count("• ") > 3
    }
    
    # 품질 점수 계산
    score = sum(quality_metrics.values())
    grade = "A" if score >= 4 else "B" if score >= 3 else "C"
    
    return {
        "metrics": quality_metrics,
        "score": score,
        "grade": grade
    }


