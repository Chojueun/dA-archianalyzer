# summary_generator.py

import dspy
from dspy import Signature, InputField, OutputField
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st
import time
import random
import anthropic

# === Rate Limiting 및 재시도 설정 ===
MAX_RETRIES = 5
BASE_WAIT_TIME = 60  # 기본 대기 시간 (초)
MAX_WAIT_TIME = 300  # 최대 대기 시간 (초)

class RateLimitHandler:
    """Rate Limit 처리를 위한 클래스"""
    
    @staticmethod
    def handle_rate_limit_error(error, attempt: int) -> bool:
        """Rate limit 오류 처리 및 재시도 여부 결정"""
        if "rate_limit_error" in str(error) or "RateLimitError" in str(error):
            # 지수 백오프 + 지터 적용
            wait_time = min(BASE_WAIT_TIME * (2 ** attempt) + random.uniform(0, 30), MAX_WAIT_TIME)
            
            st.warning(f"⚠️ API 속도 제한에 도달했습니다. {wait_time:.0f}초 후 재시도합니다... (시도 {attempt + 1}/{MAX_RETRIES})")
            
            # 프로그레스 바 표시
            progress_bar = st.progress(0)
            for i in range(int(wait_time)):
                time.sleep(1)
                progress_bar.progress((i + 1) / int(wait_time))
            progress_bar.empty()
            
            return True  # 재시도
        return False  # 재시도하지 않음
    
    @staticmethod
    def handle_overloaded_error(error, attempt: int) -> bool:
        """과부하 오류 처리"""
        if "overloaded_error" in str(error) or "Overloaded" in str(error):
            wait_time = min(30 * (3 ** attempt) + random.uniform(10, 60), MAX_WAIT_TIME)
            st.warning(f"⚠️ API 서버 과부하. {wait_time:.0f}초 후 재시도합니다... (시도 {attempt + 1}/{MAX_RETRIES})")
            
            progress_bar = st.progress(0)
            for i in range(int(wait_time)):
                time.sleep(1)
                progress_bar.progress((i + 1) / int(wait_time))
            progress_bar.empty()
            
            return True
        return False
    


# === DSPy Signature 클래스들 ===

class SiteAnalysisFields(Signature):
    text: str = InputField(desc="PDF에서 추출한 전체 텍스트")
    site_area: str = OutputField(desc="대지면적")
    site_address: str = OutputField(desc="대지 주소")
    site_slope: str = OutputField(desc="대지 경사, 고도, 방위")
    zoning: str = OutputField(desc="용도지역, 지구단위계획 등")
    restrictions: str = OutputField(desc="고도제한, 일조권, 환경, 소음, 특이 규제")
    traffic: str = OutputField(desc="주변 도로, 교통, 진출입")
    precedent_comparison: str = OutputField(desc="유사 연수원·교육시설과 비교 포인트")
    risk_factors: str = OutputField(desc="대지·법규 관련 주요 리스크")

class PDFSummary(Signature):
    text: str = InputField(desc="PDF에서 추출한 전체 텍스트")
    summary: str = OutputField(desc="PDF 내용의 핵심 요약")

class QualityCheck(Signature):
    text: str = InputField(desc="추출된 텍스트")
    quality_score: str = OutputField(desc="품질 점수 (0-100)")
    confidence_level: str = OutputField(desc="신뢰도 (높음/보통/낮음)")
    missing_info: str = OutputField(desc="누락된 정보 목록")

class PDFTypeDetector(Signature):
    text: str = InputField(desc="PDF에서 추출한 전체 텍스트")
    pdf_type: str = OutputField(desc="PDF 유형 (architectural_plan/land_use_plan/environmental_assessment/general_document)")
    document_category: str = OutputField(desc="문서 카테고리")

# === 고급 PDF 분석기 클래스 ===

class AdvancedPDFAnalyzer:
    def __init__(self):
        """고급 PDF 분석기 초기화"""
        self.site_parser = dspy.Predict(SiteAnalysisFields)
        self.summary_predictor = dspy.Predict(PDFSummary)
        self.quality_checker = dspy.Predict(QualityCheck)
        self.type_detector = dspy.Predict(PDFTypeDetector)
        
        # 필수 필드 정의
        self.required_fields = [
            "site_area", "site_address", "site_slope", "zoning", 
            "restrictions", "traffic", "precedent_comparison", "risk_factors"
        ]
        
        # 기본값 정의
        self.default_values = {
            "site_area": "대지면적 정보 없음",
            "site_address": "대지 주소 정보 없음",
            "site_slope": "대지 경사 정보 없음",
            "zoning": "용도지역 정보 없음",
            "restrictions": "건축 규제 정보 없음",
            "traffic": "교통 정보 없음",
            "precedent_comparison": "유사 사례 비교 정보 없음",
            "risk_factors": "리스크 요인 정보 없음"
        }
    
    def detect_pdf_type(self, pdf_text: str) -> Dict[str, str]:
        """PDF 유형 자동 감지"""
        try:
            result = self.type_detector(text=pdf_text)
            return {
                "pdf_type": getattr(result, "pdf_type", "general_document"),
                "document_category": getattr(result, "document_category", "일반문서")
            }
        except Exception as e:
            # 기본 감지 로직
            if "건축계획서" in pdf_text or "건축도면" in pdf_text:
                return {"pdf_type": "architectural_plan", "document_category": "건축계획서"}
            elif "토지이용계획" in pdf_text or "지구단위계획" in pdf_text:
                return {"pdf_type": "land_use_plan", "document_category": "토지이용계획"}
            elif "환경영향평가" in pdf_text or "환경" in pdf_text:
                return {"pdf_type": "environmental_assessment", "document_category": "환경평가"}
            else:
                return {"pdf_type": "general_document", "document_category": "일반문서"}
    
    def validate_and_clean_data(self, extracted_data: Dict[str, str]) -> Dict[str, str]:
        """추출된 데이터 검증 및 정제"""
        cleaned_data = {}
        
        for field, value in extracted_data.items():
            # 1. 빈 값 확인
            if not value or value.strip() == "":
                cleaned_data[field] = self.default_values.get(field, "정보 없음")
                continue
            
            # 2. 형식 검증
            if field == "site_area":
                cleaned_data[field] = self.validate_area_format(value)
            elif field == "site_address":
                cleaned_data[field] = self.validate_address_format(value)
            else:
                cleaned_data[field] = value.strip()
            
            # 3. 내용 품질 검증
            if self.is_low_quality_content(cleaned_data[field]):
                cleaned_data[field] = self.improve_content_quality(cleaned_data[field])
        
        return cleaned_data
    
    def validate_area_format(self, value: str) -> str:
        """대지면적 형식 검증"""
        # 숫자 + 단위 패턴 확인
        area_pattern = r'(\d+(?:,\d+)*)\s*(㎡|m²|평|제곱미터)'
        match = re.search(area_pattern, value)
        if match:
            return value
        else:
            return f"대지면적: {value} (형식 검증 필요)"
    
    def validate_address_format(self, value: str) -> str:
        """주소 형식 검증"""
        # 한국 주소 패턴 확인
        address_pattern = r'[가-힣]+시\s*[가-힣]+구\s*[가-힣]+동'
        if re.search(address_pattern, value):
            return value
        else:
            return f"주소: {value} (형식 검증 필요)"
    
    def is_low_quality_content(self, content: str) -> bool:
        """낮은 품질의 내용인지 확인"""
        if len(content) < 10:
            return True
        if content in self.default_values.values():
            return True
        if "정보 없음" in content or "없음" in content:
            return True
        return False
    
    def improve_content_quality(self, content: str) -> str:
        """내용 품질 개선"""
        if len(content) < 10:
            return f"{content} (추가 정보 필요)"
        return content
    
    def assess_extraction_quality(self, extracted_data: Dict[str, str]) -> Dict[str, Any]:
        """추출 품질 평가"""
        total_fields = len(self.required_fields)
        filled_fields = sum(1 for field in self.required_fields if extracted_data.get(field) and extracted_data[field] not in self.default_values.values())
        
        completeness = (filled_fields / total_fields) * 100
        
        # 품질 점수 계산
        quality_score = min(100, completeness + 20)  # 기본 20점 보너스
        
        return {
            "completeness": round(completeness, 1),
            "filled_fields": filled_fields,
            "total_fields": total_fields,
            "quality_score": round(quality_score, 1),
            "grade": self.assign_grade(quality_score),
            "confidence_level": self.assign_confidence_level(quality_score)
        }
    
    def assign_grade(self, score: float) -> str:
        """점수에 따른 등급 부여"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        else:
            return "C"
    
    def assign_confidence_level(self, score: float) -> str:
        """점수에 따른 신뢰도 부여"""
        if score >= 80:
            return "높음"
        elif score >= 60:
            return "보통"
        else:
            return "낮음"
    
    def handle_extraction_failure(self, pdf_text: str, error: Exception) -> Dict[str, str]:
        """추출 실패 시 대안 생성"""
        st.warning(f"⚠️ PDF 분석 중 오류 발생: {str(error)}")
        
        # 키워드 기반 간단한 추출 시도
        fallback_data = {}
        
        # 대지면적 추출 시도
        area_match = re.search(r'(\d+(?:,\d+)*)\s*(㎡|m²|평)', pdf_text)
        if area_match:
            fallback_data["site_area"] = f"대지면적: {area_match.group(0)}"
        
        # 주소 추출 시도
        address_match = re.search(r'[가-힣]+시\s*[가-힣]+구\s*[가-힣]+동', pdf_text)
        if address_match:
            fallback_data["site_address"] = f"주소: {address_match.group(0)}"
        
        # 기본값으로 채우기
        for field in self.required_fields:
            if field not in fallback_data:
                fallback_data[field] = self.default_values[field]
        
        return fallback_data
    
    def comprehensive_analysis(self, pdf_text: str) -> Dict[str, Any]:
        """종합적인 PDF 분석 - Rate Limiting 처리 포함"""
        for attempt in range(MAX_RETRIES):
            try:
                # 1. PDF 유형 감지
                pdf_type_info = self.detect_pdf_type(pdf_text)
                
                # 2. 기본 분석 수행
                summary_result = self.summary_predictor(text=pdf_text)
                site_result = self.site_parser(text=pdf_text)
                
                # 3. 데이터 추출
                extracted_data = {
                    "site_area": getattr(site_result, "site_area", ""),
                    "site_address": getattr(site_result, "site_address", ""),
                    "site_slope": getattr(site_result, "site_slope", ""),
                    "zoning": getattr(site_result, "zoning", ""),
                    "restrictions": getattr(site_result, "restrictions", ""),
                    "traffic": getattr(site_result, "traffic", ""),
                    "precedent_comparison": getattr(site_result, "precedent_comparison", ""),
                    "risk_factors": getattr(site_result, "risk_factors", "")
                }
                
                # 4. 데이터 검증 및 정제
                cleaned_data = self.validate_and_clean_data(extracted_data)
                
                # 5. 품질 평가
                quality_assessment = self.assess_extraction_quality(cleaned_data)
                
                return {
                    "summary": getattr(summary_result, "summary", "요약을 생성할 수 없습니다."),
                    "site_fields": cleaned_data,
                    "pdf_type": pdf_type_info,
                    "quality": quality_assessment,
                    "metadata": {
                        "analysis_timestamp": datetime.now().isoformat(),
                        "text_length": len(pdf_text),
                        "status": "success"
                    }
                }
                
            except Exception as e:
                # Rate Limit 오류 처리
                if RateLimitHandler.handle_rate_limit_error(e, attempt):
                    continue
                
                # 과부하 오류 처리
                if RateLimitHandler.handle_overloaded_error(e, attempt):
                    continue
                
                # 마지막 시도에서 실패한 경우
                if attempt == MAX_RETRIES - 1:
                    st.error(f"❌ PDF 분석 중 오류 발생: {str(e)}")
                    
                    # 오류 발생 시 대안 생성
                    fallback_data = self.handle_extraction_failure(pdf_text, e)
                    
                    return {
                        "summary": "PDF 분석 중 오류가 발생했습니다.",
                        "site_fields": fallback_data,
                        "pdf_type": {"pdf_type": "unknown", "document_category": "알 수 없음"},
                        "quality": {
                            "completeness": 0,
                            "quality_score": 0,
                            "grade": "F",
                            "confidence_level": "낮음"
                        },
                        "metadata": {
                            "analysis_timestamp": datetime.now().isoformat(),
                            "text_length": len(pdf_text),
                            "status": "error",
                            "error_message": str(e)
                        }
                    }
                
                # 일반 오류의 경우 짧은 대기 후 재시도
                wait_time = 5 + random.uniform(0, 5)
                st.warning(f"⚠️ 분석 중 오류 발생. {wait_time:.1f}초 후 재시도합니다... (시도 {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait_time)
        
        # 모든 재시도 실패
        return {
            "summary": "PDF 분석에 실패했습니다. 잠시 후 다시 시도해주세요.",
            "site_fields": self.default_values,
            "pdf_type": {"pdf_type": "unknown", "document_category": "알 수 없음"},
            "quality": {
                "completeness": 0,
                "quality_score": 0,
                "grade": "F",
                "confidence_level": "낮음"
            },
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "text_length": len(pdf_text),
                "status": "failed_after_retries"
            }
        }

# === 전역 분석기 인스턴스 ===
analyzer = AdvancedPDFAnalyzer()

# === 기존 함수들과의 호환성을 위한 래퍼 함수들 ===

def summarize_pdf(pdf_text: str) -> str:
    """PDF 텍스트를 요약하는 함수 (기존 호환성) - Rate Limiting 처리 포함"""
    for attempt in range(MAX_RETRIES):
        try:
            result = analyzer.comprehensive_analysis(pdf_text)
            return result["summary"]
        except Exception as e:
            # Rate Limit 오류 처리
            if RateLimitHandler.handle_rate_limit_error(e, attempt):
                continue
            
            # 과부하 오류 처리
            if RateLimitHandler.handle_overloaded_error(e, attempt):
                continue
            
            # 마지막 시도에서 실패한 경우
            if attempt == MAX_RETRIES - 1:
                return f"요약 생성 중 오류 발생: {str(e)}"
            
            # 일반 오류의 경우 짧은 대기 후 재시도
            wait_time = 5 + random.uniform(0, 5)
            st.warning(f"⚠️ 요약 생성 중 오류 발생. {wait_time:.1f}초 후 재시도합니다... (시도 {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait_time)
    
    return "요약 생성에 실패했습니다. 잠시 후 다시 시도해주세요."

def extract_site_analysis_fields(pdf_text: str) -> dict:
    """PDF에서 대지 및 법규 관련 필드를 추출하는 함수 (기존 호환성) - Rate Limiting 처리 포함"""
    for attempt in range(MAX_RETRIES):
        try:
            result = analyzer.comprehensive_analysis(pdf_text)
            return result["site_fields"]
        except Exception as e:
            # Rate Limit 오류 처리
            if RateLimitHandler.handle_rate_limit_error(e, attempt):
                continue
            
            # 과부하 오류 처리
            if RateLimitHandler.handle_overloaded_error(e, attempt):
                continue
            
            # 마지막 시도에서 실패한 경우
            if attempt == MAX_RETRIES - 1:
                return analyzer.default_values
            
            # 일반 오류의 경우 짧은 대기 후 재시도
            wait_time = 5 + random.uniform(0, 5)
            st.warning(f"⚠️ 필드 추출 중 오류 발생. {wait_time:.1f}초 후 재시도합니다... (시도 {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait_time)
    
    return analyzer.default_values

# === 새로운 고급 함수들 ===

def analyze_pdf_comprehensive(pdf_text: str) -> Dict[str, Any]:
    """종합적인 PDF 분석 (새로운 고급 기능)"""
    return analyzer.comprehensive_analysis(pdf_text)

def analyze_pdf_in_chunks(pdf_text: str, chunk_size: int = 4000, max_chunks: int = 20) -> Dict[str, Any]:
    """큰 PDF를 청크로 나누어 분석 - 개선된 버전"""
    if len(pdf_text) <= chunk_size:
        return analyzer.comprehensive_analysis(pdf_text)
    
    # 대용량 PDF 경고
    if len(pdf_text) > 100000:  # 10만자 이상
        st.warning("⚠️ 매우 큰 PDF입니다. 분석에 시간이 오래 걸릴 수 있습니다.")
    
    # 청크 크기 조정 (너무 많은 청크 방지)
    if len(pdf_text) > chunk_size * max_chunks:
        chunk_size = len(pdf_text) // max_chunks
        st.warning(f"📄 PDF가 너무 큽니다. 청크 크기를 {chunk_size:,}자로 조정합니다.")
    
    st.info(f"📄 큰 PDF를 {chunk_size:,}자 단위로 나누어 분석합니다...")
    
    # PDF를 청크로 분할 (문장 경계 고려)
    chunks = []
    current_pos = 0
    
    while current_pos < len(pdf_text):
        end_pos = min(current_pos + chunk_size, len(pdf_text))
        
        # 문장 경계에서 자르기 시도
        if end_pos < len(pdf_text):
            # 마침표, 느낌표, 물음표 뒤에서 자르기
            for punct in ['.', '!', '?', '\n\n']:
                last_punct = pdf_text.rfind(punct, current_pos, end_pos)
                if last_punct > current_pos + chunk_size * 0.8:  # 80% 이상 채웠을 때만
                    end_pos = last_punct + 1
                    break
        
        chunk = pdf_text[current_pos:end_pos]
        chunks.append(chunk)
        current_pos = end_pos
    
    total_chunks = len(chunks)
    st.info(f"총 {total_chunks}개 청크로 분할되었습니다.")
    
    # 진행 상황 표시를 위한 프로그레스 바
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 각 청크 분석 (메모리 효율성을 위해 하나씩 처리)
    chunk_results = []
    successful_chunks = 0
    
    for i, chunk in enumerate(chunks):
        # 진행 상황 업데이트
        progress = (i + 1) / total_chunks
        progress_bar.progress(progress)
        status_text.text(f"청크 {i+1}/{total_chunks} 분석 중... ({successful_chunks}개 성공)")
        
        try:
            # 청크가 너무 작으면 건너뛰기
            if len(chunk.strip()) < 100:
                st.info(f"청크 {i+1} 건너뛰기 (너무 짧음)")
                continue
                
            result = analyzer.comprehensive_analysis(chunk)
            chunk_results.append(result)
            successful_chunks += 1
            
            # 성공률이 낮으면 경고
            if i > 0 and successful_chunks / (i + 1) < 0.5:
                st.warning(f"⚠️ 청크 분석 성공률이 낮습니다. ({successful_chunks}/{i+1})")
                
        except Exception as e:
            st.warning(f"청크 {i+1} 분석 실패: {str(e)}")
            continue
    
    # 진행 상황 표시 제거
    progress_bar.empty()
    status_text.empty()
    
    # 결과 요약 표시
    if successful_chunks == total_chunks:
        st.success(f"✅ 모든 청크 분석 완료! ({successful_chunks}/{total_chunks})")
    elif successful_chunks > 0:
        st.warning(f"⚠️ 부분 분석 완료 ({successful_chunks}/{total_chunks})")
    else:
        st.error("❌ 모든 청크 분석에 실패했습니다.")
    
    if not chunk_results:
        return {
            "summary": "모든 청크 분석에 실패했습니다.",
            "site_fields": analyzer.default_values,
            "pdf_type": {"pdf_type": "unknown", "document_category": "알 수 없음"},
            "quality": {
                "completeness": 0,
                "quality_score": 0,
                "grade": "F",
                "confidence_level": "낮음"
            },
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "text_length": len(pdf_text),
                "status": "failed_all_chunks",
                "chunks_processed": 0,
                "total_chunks": total_chunks
            }
        }
    
    # 청크 결과 통합
    combined_summary = "\n\n".join([r["summary"] for r in chunk_results if r["summary"]])
    
    # 사이트 필드 통합 (가장 완전한 정보 우선)
    combined_site_fields = {}
    for field in analyzer.required_fields:
        for result in chunk_results:
            if result["site_fields"].get(field) and result["site_fields"][field] != analyzer.default_values[field]:
                combined_site_fields[field] = result["site_fields"][field]
                break
        if field not in combined_site_fields:
            combined_site_fields[field] = analyzer.default_values[field]
    
    # 품질 평가 통합
    avg_quality_score = sum(r["quality"]["quality_score"] for r in chunk_results) / len(chunk_results)
    avg_completeness = sum(r["quality"]["completeness"] for r in chunk_results) / len(chunk_results)
    
    combined_quality = {
        "completeness": round(avg_completeness, 1),
        "quality_score": round(avg_quality_score, 1),
        "grade": analyzer.assign_grade(avg_quality_score),
        "confidence_level": analyzer.assign_confidence_level(avg_quality_score)
    }
    
    # PDF 타입 결정 (가장 많이 나타난 타입 선택)
    pdf_types = {}
    for result in chunk_results:
        pdf_type = result["pdf_type"]["pdf_type"]
        pdf_types[pdf_type] = pdf_types.get(pdf_type, 0) + 1
    
    most_common_type = max(pdf_types.items(), key=lambda x: x[1])[0] if pdf_types else "unknown"
    
    return {
        "summary": combined_summary,
        "site_fields": combined_site_fields,
        "pdf_type": {"pdf_type": most_common_type, "document_category": "대용량 문서"},
        "quality": combined_quality,
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "text_length": len(pdf_text),
            "status": "success_chunked",
            "chunks_processed": len(chunk_results),
            "total_chunks": total_chunks,
            "success_rate": round(successful_chunks / total_chunks * 100, 1)
        }
    }

def get_pdf_quality_report(pdf_text: str) -> Dict[str, Any]:
    """PDF 품질 보고서 생성"""
    result = analyzer.comprehensive_analysis(pdf_text)
    return {
        "quality_assessment": result["quality"],
        "pdf_type": result["pdf_type"],
        "recommendations": generate_improvement_recommendations(result["quality"])
    }

def generate_improvement_recommendations(quality: Dict[str, Any]) -> List[str]:
    """품질 개선 권장사항 생성"""
    recommendations = []
    
    if quality["completeness"] < 50:
        recommendations.append("PDF에 더 많은 건축 관련 정보가 포함되어야 합니다.")
    
    if quality["quality_score"] < 60:
        recommendations.append("PDF 내용의 품질을 개선해야 합니다.")
    
    if quality["confidence_level"] == "낮음":
        recommendations.append("PDF 분석 결과의 신뢰도가 낮습니다. 추가 검토가 필요합니다.")
    
    if not recommendations:
        recommendations.append("PDF 분석 품질이 양호합니다.")
    
    return recommendations