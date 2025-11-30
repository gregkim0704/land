"""
토지 전문 AI 시스템 - 상업용 버전
Commercial Land AI System - Production Ready
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional

# 커스텀 모듈 임포트
from auth_system import AuthManager, login_form, register_form, show_user_info, require_auth
from database_manager import DatabaseManager
from api_integrations import PublicAPIManager, MarketDataAnalyzer, GeocodeService
from ai_models_gemini import UnifiedAIManager as AIManager, LandPricePredictor
from advanced_analytics import MarketAnalyzer, ReportGenerator
from security_manager import SecurityManager, ErrorHandler, secure_endpoint, validate_and_sanitize
from land_ai_core import LandInfo, LandAnalyzer, LandMatcher
from land_ai_chatbot import LandConsultingBot, SmartDocumentAnalyzer
from ai_models_gemini import UnifiedAIManager
from file_upload_handler import FileUploadHandler

# 페이지 설정
st.set_page_config(
    page_title="토지전문 AI 컨설팅 시스템 - Commercial",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 전역 객체 초기화
@st.cache_resource
def init_managers():
    """관리자 객체들 초기화"""
    return {
        'auth': AuthManager(),
        'db': DatabaseManager(),
        'api': PublicAPIManager(),
        'ai': AIManager(prefer_gemini=True),
        'security': SecurityManager(),
        'error_handler': ErrorHandler(),
        'market_analyzer': MarketAnalyzer(),
        'report_generator': ReportGenerator(),
        'price_predictor': LandPricePredictor(),
        'geocode': GeocodeService()
    }

managers = init_managers()

# 세션 상태 초기화
def init_session_state():
    """세션 상태 초기화"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

init_session_state()

# 인증 확인
def check_authentication():
    """인증 상태 확인"""
    if st.session_state.user is None:
        st.title("🔐 로그인이 필요합니다")
        
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            login_form()
        
        with tab2:
            register_form()
        
        st.stop()

# 메인 애플리케이션
def main():
    """메인 애플리케이션"""
    
    # 인증 확인
    check_authentication()
    
    # 사용자 정보 표시
    show_user_info()
    
    # 사이드바 메뉴
    st.sidebar.title("🏞️ 토지 AI 시스템")
    st.sidebar.markdown("---")
    
    # 사용자 등급별 메뉴 제한
    user = st.session_state.user
    available_menus = get_available_menus(user.user_type)
    
    menu = st.sidebar.radio("메뉴 선택", available_menus)
    
    # 사용량 정보 표시
    show_usage_info(user.user_id)
    
    # 메뉴별 페이지 라우팅
    try:
        if menu == "🏠 홈":
            show_dashboard()
        elif menu == "🔍 토지 분석":
            show_land_analysis()
        elif menu == "💬 AI 상담":
            show_ai_consultation()
        elif menu == "🎯 고객 매칭":
            show_customer_matching()
        elif menu == "📄 계약서 분석":
            show_contract_analysis()
        elif menu == "📊 시장 리포트":
            show_market_report()
        elif menu == "📈 고급 분석":
            show_advanced_analytics()
        elif menu == "⚙️ 설정":
            show_settings()
        elif menu == "📋 사용 이력":
            show_usage_history()
    
    except Exception as e:
        error_info = managers['error_handler'].handle_error(
            e, 
            context={'menu': menu, 'user_id': user.user_id},
            user_id=user.user_id
        )
        
        st.error(f"오류가 발생했습니다: {error_info['user_message']}")
        st.error(f"오류 ID: {error_info['error_id']}")
        
        if st.button("다시 시도"):
            st.rerun()

def get_available_menus(user_type: str) -> List[str]:
    """사용자 등급별 사용 가능한 메뉴"""
    base_menus = ["🏠 홈", "🔍 토지 분석", "💬 AI 상담"]
    
    if user_type in ['premium', 'admin']:
        base_menus.extend([
            "🎯 고객 매칭", "📄 계약서 분석", "📊 시장 리포트"
        ])
    
    if user_type == 'admin':
        base_menus.extend([
            "📈 고급 분석", "⚙️ 설정"
        ])
    
    base_menus.append("📋 사용 이력")
    
    return base_menus

def show_usage_info(user_id: str):
    """사용량 정보 표시"""
    try:
        analytics = managers['db'].get_analytics_data(user_id)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 사용 현황")
        st.sidebar.metric("분석 건수", analytics['land_analyses'])
        st.sidebar.metric("AI 상담", analytics['chat_messages'])
        st.sidebar.metric("등록 고객", analytics['customers'])
        
        # API 사용량 (실제 구현 시)
        st.sidebar.progress(0.3)  # 30% 사용
        st.sidebar.caption("월간 API 사용량: 30/100")
        
    except Exception as e:
        st.sidebar.error("사용량 정보를 불러올 수 없습니다.")

@secure_endpoint(require_auth=True, rate_limit=True)
def show_dashboard():
    """대시보드 페이지"""
    st.title("🏠 대시보드")
    
    user = st.session_state.user
    
    # 환영 메시지
    st.markdown(f"### 안녕하세요, {user.username}님! 👋")
    st.markdown(f"**{user.user_type.upper()}** 등급으로 이용 중입니다.")
    
    # 주요 지표
    col1, col2, col3, col4 = st.columns(4)
    
    analytics = managers['db'].get_analytics_data(user.user_id)
    
    with col1:
        st.metric("총 분석 건수", analytics['land_analyses'], "+2")
    with col2:
        st.metric("AI 상담 횟수", analytics['chat_messages'], "+5")
    with col3:
        st.metric("등록 고객 수", analytics['customers'], "+1")
    with col4:
        st.metric("이번 달 활동", "15건", "+3")
    
    st.markdown("---")
    
    # 최근 활동
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 최근 분석 결과")
        recent_lands = managers['db'].get_user_land_records(user.user_id, limit=5)
        
        if recent_lands:
            for land in recent_lands:
                with st.expander(f"📍 {land['address'][:30]}..."):
                    st.write(f"**지목**: {land['land_category']}")
                    st.write(f"**면적**: {land['area']:.1f}㎡")
                    st.write(f"**분석일**: {land['created_at'][:10]}")
        else:
            st.info("아직 분석한 토지가 없습니다. 토지 분석을 시작해보세요!")
    
    with col2:
        st.markdown("### 💬 최근 AI 상담")
        recent_chats = managers['db'].get_user_chat_history(user.user_id, limit=5)
        
        if recent_chats:
            for chat in recent_chats:
                with st.expander(f"💭 {chat['user_message'][:30]}..."):
                    st.write(f"**질문**: {chat['user_message']}")
                    st.write(f"**답변**: {chat['ai_response'][:100]}...")
                    st.write(f"**시간**: {chat['created_at'][:16]}")
        else:
            st.info("AI 상담 기록이 없습니다. AI 상담을 시작해보세요!")
    
    # 시장 동향 요약
    st.markdown("---")
    st.markdown("### 📈 오늘의 시장 동향")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("전국 평균 공시지가", "15.2만원/평", "+3.5%")
    with col2:
        st.metric("이번 달 거래량", "1,234건", "+12.3%")
    with col3:
        st.metric("유망 투자 지역", "경기 남부", "")
    
    # 빠른 액션
    st.markdown("---")
    st.markdown("### 🚀 빠른 시작")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 새 토지 분석", use_container_width=True):
            st.session_state.menu = "🔍 토지 분석"
            st.rerun()
    
    with col2:
        if st.button("💬 AI 상담하기", use_container_width=True):
            st.session_state.menu = "💬 AI 상담"
            st.rerun()
    
    with col3:
        if st.button("📊 시장 리포트", use_container_width=True):
            st.session_state.menu = "📊 시장 리포트"
            st.rerun()

@secure_endpoint(require_auth=True, rate_limit=True)
@validate_and_sanitize({
    'address': 'address',
    'area': 'numeric',
    'official_price': 'numeric'
})
def show_land_analysis():
    """토지 분석 페이지"""
    st.title("🔍 토지 종합 분석")
    
    user = st.session_state.user
    
    # API 사용량 확인
    if not managers['auth'].check_api_limit(user.user_id):
        st.error("월간 API 사용량을 초과했습니다. 다음 달에 다시 이용해주세요.")
        return
    
    st.markdown("토지 정보를 입력하거나 파일로 업로드하여 AI가 종합적으로 분석해드립니다.")
    
    # 입력 방식 선택
    input_method = st.radio(
        "입력 방식 선택",
        ["📝 직접 입력", "📤 파일 업로드"],
        horizontal=True
    )
    
    if input_method == "📤 파일 업로드":
        show_file_upload_section()
        return
    
    # 직접 입력 폼
    with st.form("land_analysis_form"):
        st.markdown("### 📝 토지 기본 정보 입력")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("주소", "경기도 성남시 분당구 정자동 123-45")
            land_category = st.selectbox(
                "지목",
                ["대지", "전", "답", "과수원", "임야", "목장용지", "공장용지", "학교용지", "주차장", "주유소용지"]
            )
            area = st.number_input("면적 (㎡)", min_value=10.0, value=500.0, step=10.0)
            official_price = st.number_input("공시지가 (원/㎡)", min_value=10000, value=3000000, step=100000)
        
        with col2:
            zone_type = st.selectbox(
                "용도지역",
                [
                    "제1종전용주거지역", "제2종전용주거지역",
                    "제1종일반주거지역", "제2종일반주거지역", "제3종일반주거지역",
                    "준주거지역", "중심상업지역", "일반상업지역", "근린상업지역",
                    "일반공업지역", "준공업지역",
                    "자연녹지지역", "생산녹지지역", "보전녹지지역"
                ]
            )
            district = st.text_input("용도지구", "일반")
            road_contact = st.checkbox("도로 접함", value=True)
            nearest_station_km = st.number_input("최근접 역까지 거리 (km)", min_value=0.0, value=0.8, step=0.1)
        
        # 고급 옵션
        with st.expander("🔧 고급 분석 옵션"):
            use_ai_analysis = st.checkbox("AI 고급 분석 사용", value=True)
            use_market_data = st.checkbox("실시간 시장 데이터 연동", value=True)
            include_development_plans = st.checkbox("개발계획 정보 포함", value=False)
        
        submitted = st.form_submit_button("🔍 분석 시작", use_container_width=True)
    
    if submitted:
        with st.spinner("AI가 토지를 종합 분석하고 있습니다..."):
            try:
                # 입력 데이터 검증
                land_data = {
                    'address': address,
                    'land_category': land_category,
                    'area': area,
                    'official_price': official_price,
                    'zone_type': zone_type,
                    'district': district,
                    'road_contact': road_contact,
                    'nearest_station_km': nearest_station_km
                }
                
                # 토지 정보 생성
                land = LandInfo(**land_data)
                
                # 기본 분석
                analyzer = LandAnalyzer(land)
                basic_report = analyzer.generate_comprehensive_report()
                
                # AI 고급 분석
                if use_ai_analysis:
                    ai_analysis = managers['ai'].analyze_land_with_ai(land_data)
                    basic_report['ai_analysis'] = ai_analysis
                
                # 시장 데이터 연동
                market_context = {}
                if use_market_data:
                    # 좌표 변환
                    coordinates = managers['geocode'].address_to_coordinates(address)
                    if coordinates:
                        # 토지이용계획 조회
                        land_use_plan = managers['api'].get_land_use_plan(
                            coordinates['x'], coordinates['y']
                        )
                        basic_report['land_use_plan'] = land_use_plan
                        market_context['land_use_plan'] = land_use_plan
                
                # 가격 예측
                price_prediction = managers['price_predictor'].predict_price(land_data, market_context)
                basic_report['price_prediction'] = {
                    'predicted_price': price_prediction.predicted_price,
                    'confidence_score': price_prediction.confidence_score,
                    'price_range_min': price_prediction.price_range_min,
                    'price_range_max': price_prediction.price_range_max,
                    'factors': price_prediction.factors
                }
                
                # 데이터베이스 저장
                record_id = managers['db'].save_land_analysis(
                    user.user_id, land_data, basic_report
                )
                
                # API 사용량 증가
                managers['auth'].increment_api_usage(user.user_id)
                
                # 보안 이벤트 로깅
                managers['security'].log_security_event(
                    'land_analysis_completed',
                    user_id=user.user_id,
                    details={'record_id': record_id, 'address': address}
                )
                
                st.session_state.current_analysis = basic_report
                st.success("✅ 분석이 완료되었습니다!")
                
            except Exception as e:
                error_info = managers['error_handler'].handle_error(
                    e, 
                    context={'function': 'land_analysis', 'address': address},
                    user_id=user.user_id
                )
                st.error(f"분석 중 오류가 발생했습니다: {error_info['user_message']}")
                return
    
    # 분석 결과 표시
    if st.session_state.current_analysis:
        show_analysis_results(st.session_state.current_analysis)

def show_analysis_results(report: Dict):
    """분석 결과 표시"""
    st.markdown("---")
    st.markdown("## 📊 분석 결과")
    
    # 탭으로 구성
    tabs = st.tabs([
        "📌 기본정보", "🏗️ 건축규제", "📈 개발가능성", 
        "💰 가격분석", "⚠️ 리스크", "🤖 AI 분석"
    ])
    
    with tabs[0]:
        show_basic_info_tab(report)
    
    with tabs[1]:
        show_building_regulations_tab(report)
    
    with tabs[2]:
        show_development_potential_tab(report)
    
    with tabs[3]:
        show_price_analysis_tab(report)
    
    with tabs[4]:
        show_risk_analysis_tab(report)
    
    with tabs[5]:
        show_ai_analysis_tab(report)
    
    # 리포트 다운로드
    show_report_download(report)

def show_basic_info_tab(report: Dict):
    """기본정보 탭"""
    st.markdown("### 📌 토지 기본 정보")
    info = report["기본정보"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("면적", f"{info['면적_평']}평")
        st.metric("지목", info['지목'])
    with col2:
        st.metric("공시지가", f"{info['공시지가_원_m2']:,}원/㎡")
        st.metric("총 공시지가", f"{info['총_공시지가_원']/100000000:.2f}억원")
    with col3:
        st.metric("용도지역", info['용도지역'])
        st.metric("용도지구", info['용도지구'])
    
    st.info(f"**주소**: {info['주소']}")

def show_building_regulations_tab(report: Dict):
    """건축규제 탭"""
    st.markdown("### 🏗️ 건축 규제")
    regs = report["건축규제"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("건폐율", regs['건폐율'])
        st.metric("건축가능면적", f"{regs['건축가능면적_평']}평")
    with col2:
        st.metric("용적률", regs['용적률'])
        st.metric("최대연면적", f"{regs['최대연면적_평']}평")
    
    st.info(f"""
    💡 **건축 가능 규모**  
    - 이 토지에는 최대 **{regs['건축가능면적_평']}평**의 건축면적으로 건물을 지을 수 있습니다.
    - 총 연면적은 최대 **{regs['최대연면적_평']}평**까지 가능합니다.
    """)

def show_development_potential_tab(report: Dict):
    """개발가능성 탭"""
    st.markdown("### 📈 개발 가능성 분석")
    dev = report["개발가능성"]
    
    # 점수 표시
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(
            "개발가능성 점수",
            f"{dev['개발가능성_점수']}점",
            f"{dev['개발가능성_등급']}"
        )
    with col2:
        # 프로그레스 바
        st.progress(dev['개발가능성_점수'] / 100)
    
    # 주요 요인
    st.markdown("#### 📋 주요 평가 요인")
    for factor in dev['주요_요인']:
        st.write(f"✓ {factor}")

def show_price_analysis_tab(report: Dict):
    """가격분석 탭"""
    st.markdown("### 💰 시장 가격 분석")
    
    # 기본 가격 분석
    if "시장가격_분석" in report:
        price = report["시장가격_분석"]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("예상 단가", f"{price['예상_단가_만원_평']}만원/평")
        with col2:
            st.metric("예상 총액", f"{price['예상_총액_억원']}억원")
        with col3:
            st.metric("공시지가 배율", f"{price['공시지가_대비_배율']}배")
    
    # AI 가격 예측
    if "price_prediction" in report:
        pred = report["price_prediction"]
        
        st.markdown("#### 🤖 AI 가격 예측")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "AI 예측가", 
                f"{pred['predicted_price']/100000000:.2f}억원",
                f"신뢰도: {pred['confidence_score']*100:.0f}%"
            )
        with col2:
            st.metric(
                "예측 범위",
                f"{pred['price_range_min']/100000000:.1f}~{pred['price_range_max']/100000000:.1f}억원"
            )
        
        st.markdown("#### 📊 예측 근거")
        for factor in pred['factors']:
            st.write(f"• {factor}")

def show_risk_analysis_tab(report: Dict):
    """리스크 분석 탭"""
    st.markdown("### ⚠️ 리스크 분석")
    risks = report["리스크_분석"]
    
    for risk in risks:
        severity_color = {
            "상": "🔴",
            "중": "🟡",
            "낮음": "🟢"
        }.get(risk["심각도"], "⚪")
        
        with st.expander(f"{severity_color} {risk['리스크_유형']} (심각도: {risk['심각도']})"):
            st.markdown(f"**설명**: {risk['설명']}")
            st.markdown(f"**대응방안**: {risk['대응방안']}")

def show_ai_analysis_tab(report: Dict):
    """AI 분석 탭"""
    st.markdown("### 🤖 AI 고급 분석")
    
    if "ai_analysis" in report:
        ai_data = report["ai_analysis"]
        
        # 개발가능성
        if "개발가능성" in ai_data:
            dev_data = ai_data["개발가능성"]
            st.markdown("#### 📈 AI 개발가능성 평가")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("AI 점수", f"{dev_data.get('점수', 0)}점")
            with col2:
                st.metric("AI 등급", dev_data.get('등급', 'N/A'))
            
            if "주요요인" in dev_data:
                st.markdown("**주요 요인:**")
                for factor in dev_data["주요요인"]:
                    st.write(f"• {factor}")
        
        # 투자 추천
        if "투자추천" in ai_data:
            st.markdown("#### 💡 AI 투자 추천")
            st.info(ai_data["투자추천"])
    
    else:
        st.info("AI 고급 분석을 사용하려면 분석 시 'AI 고급 분석 사용' 옵션을 선택해주세요.")

def show_report_download(report: Dict):
    """리포트 다운로드"""
    st.markdown("---")
    st.markdown("### 📥 리포트 다운로드")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_report = json.dumps(report, ensure_ascii=False, indent=2)
        st.download_button(
            label="📄 JSON 다운로드",
            data=json_report,
            file_name=f"land_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # 텍스트 리포트
        text_report = generate_text_report(report)
        st.download_button(
            label="📝 텍스트 다운로드",
            data=text_report,
            file_name=f"land_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    with col3:
        # PDF 리포트 (프리미엄 기능)
        user = st.session_state.user
        if user.user_type in ['premium', 'admin']:
            if st.button("📋 PDF 생성", use_container_width=True):
                with st.spinner("PDF를 생성하고 있습니다..."):
                    pdf_data = managers['report_generator'].generate_pdf_report(report)
                    if pdf_data:
                        st.download_button(
                            label="📋 PDF 다운로드",
                            data=pdf_data,
                            file_name=f"land_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("PDF 생성에 실패했습니다.")
        else:
            st.info("PDF 다운로드는 프리미엄 기능입니다.")

def generate_text_report(report: Dict) -> str:
    """텍스트 리포트 생성"""
    text_lines = [
        "=" * 50,
        "토지 종합 분석 리포트",
        "=" * 50,
        f"생성일시: {report.get('생성일시', '')}",
        f"주소: {report.get('기본정보', {}).get('주소', '')}",
        "",
        "[ 기본 정보 ]",
        f"지목: {report.get('기본정보', {}).get('지목', '')}",
        f"면적: {report.get('기본정보', {}).get('면적_평', 0)}평",
        f"용도지역: {report.get('기본정보', {}).get('용도지역', '')}",
        "",
        "[ 개발 가능성 ]",
        f"점수: {report.get('개발가능성', {}).get('개발가능성_점수', 0)}점",
        f"등급: {report.get('개발가능성', {}).get('개발가능성_등급', '')}",
        "",
        "[ 가격 분석 ]"
    ]
    
    if "시장가격_분석" in report:
        price = report["시장가격_분석"]
        text_lines.extend([
            f"예상 시세: {price.get('예상_총액_억원', 0)}억원",
            f"공시지가 배율: {price.get('공시지가_대비_배율', 0)}배"
        ])
    
    if "price_prediction" in report:
        pred = report["price_prediction"]
        text_lines.extend([
            "",
            "[ AI 가격 예측 ]",
            f"예측가: {pred['predicted_price']/100000000:.2f}억원",
            f"신뢰도: {pred['confidence_score']*100:.0f}%"
        ])
    
    text_lines.extend([
        "",
        "=" * 50,
        "본 리포트는 참고용이며, 투자 결정 시 전문가 상담을 권합니다.",
        "=" * 50
    ])
    
    return "\n".join(text_lines)

@secure_endpoint(require_auth=True, rate_limit=True)
def show_ai_consultation():
    """AI 상담 페이지"""
    st.title("💬 AI 토지 컨설팅")
    st.markdown("토지 투자 관련 궁금한 점을 AI 전문가에게 물어보세요!")
    
    user = st.session_state.user
    
    # 채팅 히스토리 로드
    if not st.session_state.chat_history:
        st.session_state.chat_history = managers['db'].get_user_chat_history(user.user_id, limit=20)
    
    # 채팅 히스토리 표시
    st.markdown("### 💬 상담 내역")
    
    chat_container = st.container()
    
    with chat_container:
        for chat in reversed(st.session_state.chat_history[-10:]):  # 최근 10개만 표시
            with st.chat_message("user"):
                st.write(chat['user_message'])
            with st.chat_message("assistant", avatar="🤖"):
                st.write(chat['ai_response'])
    
    # 입력 창
    user_input = st.chat_input("질문을 입력하세요... (예: 농지 투자 어떤가요?)")
    
    if user_input:
        # API 사용량 확인
        if not managers['auth'].check_api_limit(user.user_id):
            st.error("월간 API 사용량을 초과했습니다.")
            return
        
        # 입력 검증 및 정화
        clean_input = managers['security'].sanitize_input(user_input)
        
        # 민감한 데이터 스캔
        sensitive_patterns = managers['security'].scan_for_sensitive_data(clean_input)
        if sensitive_patterns:
            st.warning("입력하신 내용에 민감한 정보가 포함되어 있을 수 있습니다. 개인정보는 입력하지 마세요.")
        
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(clean_input)
        
        # AI 응답 생성
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI가 답변을 생성하고 있습니다..."):
                try:
                    # 컨텍스트 준비
                    context = {
                        'user_type': user.user_type,
                        'recent_analyses': len(managers['db'].get_user_land_records(user.user_id, limit=5))
                    }
                    
                    response = managers['ai'].chat_consultation(clean_input, context)
                    st.write(response)
                    
                    # 데이터베이스에 저장
                    managers['db'].save_chat_message(user.user_id, clean_input, response)
                    
                    # 세션 히스토리 업데이트
                    st.session_state.chat_history.append({
                        'user_message': clean_input,
                        'ai_response': response,
                        'created_at': datetime.now().isoformat()
                    })
                    
                    # API 사용량 증가
                    managers['auth'].increment_api_usage(user.user_id)
                    
                except Exception as e:
                    error_info = managers['error_handler'].handle_error(
                        e, 
                        context={'function': 'ai_consultation', 'user_input': clean_input[:50]},
                        user_id=user.user_id
                    )
                    st.error(f"답변 생성 중 오류가 발생했습니다: {error_info['user_message']}")
    
    # 사이드 정보
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 추천 질문")
    
    sample_questions = [
        "농지 투자 어떤가요?",
        "임야 개발이 가능한가요?",
        "맹지는 왜 문제인가요?",
        "토지 세금은 얼마나 나오나요?",
        "역세권 토지 추천해주세요",
        "농지전용 절차가 궁금해요"
    ]
    
    for question in sample_questions:
        if st.sidebar.button(question, key=f"sample_{question}"):
            st.session_state.sample_question = question
            st.rerun()

def show_file_upload_section():
    """파일 업로드 섹션"""
    st.markdown("### 📤 파일로 토지 정보 업로드")
    
    user = st.session_state.user
    file_handler = FileUploadHandler()
    
    # 템플릿 다운로드
    st.markdown("#### 📋 템플릿 다운로드")
    st.info("먼저 템플릿을 다운로드하여 토지 정보를 입력한 후 업로드하세요.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        excel_template = file_handler.create_template_excel()
        st.download_button(
            label="📊 Excel 템플릿",
            data=excel_template,
            file_name="토지정보_템플릿.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with col2:
        csv_template = file_handler.create_template_csv()
        st.download_button(
            label="📄 CSV 템플릿",
            data=csv_template,
            file_name="토지정보_템플릿.csv",
            mime="text/csv"
        )
    
    with col3:
        json_template = file_handler.create_template_json()
        st.download_button(
            label="📋 JSON 템플릿",
            data=json_template,
            file_name="토지정보_템플릿.json",
            mime="application/json"
        )
    
    st.markdown("---")
    
    # 파일 업로드
    st.markdown("#### 📁 파일 업로드")
    
    uploaded_file = st.file_uploader(
        "토지 정보 파일을 업로드하세요",
        type=['xlsx', 'xls', 'csv', 'json'],
        help="Excel, CSV, JSON 파일을 지원합니다."
    )
    
    if uploaded_file is not None:
        try:
            # 파일 타입에 따라 파싱
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            with st.spinner("파일을 읽고 있습니다..."):
                if file_extension in ['xlsx', 'xls']:
                    land_data_list = file_handler.parse_excel(uploaded_file.read())
                elif file_extension == 'csv':
                    land_data_list = file_handler.parse_csv(uploaded_file.read())
                elif file_extension == 'json':
                    land_data_list = file_handler.parse_json(uploaded_file.read())
                else:
                    st.error("지원하지 않는 파일 형식입니다.")
                    return
            
            st.success(f"✅ {len(land_data_list)}개의 토지 정보를 읽었습니다!")
            
            # 데이터 미리보기
            st.markdown("#### 📊 업로드된 데이터 미리보기")
            
            preview_data = []
            for idx, land in enumerate(land_data_list[:5], 1):  # 최대 5개만 표시
                preview_data.append({
                    '번호': idx,
                    '주소': land.address[:30] + '...' if len(land.address) > 30 else land.address,
                    '지목': land.land_category,
                    '면적(㎡)': f"{land.area:,.0f}",
                    '공시지가(원/㎡)': f"{land.official_price:,.0f}",
                    '용도지역': land.zone_type
                })
            
            st.dataframe(preview_data, use_container_width=True)
            
            if len(land_data_list) > 5:
                st.info(f"외 {len(land_data_list) - 5}개 더 있습니다.")
            
            # 분석 시작 버튼
            st.markdown("---")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                analyze_all = st.checkbox("모든 토지 일괄 분석", value=False)
                if analyze_all:
                    st.warning(f"⚠️ {len(land_data_list)}개의 토지를 분석합니다. API 사용량이 증가할 수 있습니다.")
            
            with col2:
                if st.button("🔍 분석 시작", use_container_width=True, type="primary"):
                    analyze_uploaded_lands(land_data_list, analyze_all)
        
        except Exception as e:
            st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")
            st.info("템플릿 형식에 맞게 파일을 작성했는지 확인해주세요.")


def analyze_uploaded_lands(land_data_list: list, analyze_all: bool = False):
    """업로드된 토지 분석"""
    user = st.session_state.user
    file_handler = FileUploadHandler()
    
    # 분석할 토지 선택
    lands_to_analyze = land_data_list if analyze_all else [land_data_list[0]]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    results = []
    
    for idx, land_data in enumerate(lands_to_analyze):
        # 진행률 업데이트
        progress = (idx + 1) / len(lands_to_analyze)
        progress_bar.progress(progress)
        status_text.text(f"분석 중... ({idx + 1}/{len(lands_to_analyze)})")
        
        try:
            # 데이터 유효성 검증
            is_valid, error_msg = file_handler.validate_land_data(land_data)
            if not is_valid:
                st.warning(f"⚠️ {land_data.address}: {error_msg}")
                continue
            
            # 토지 정보 생성
            land = LandInfo(**land_data.to_dict())
            
            # 분석 수행
            analyzer = LandAnalyzer(land)
            report = analyzer.generate_comprehensive_report()
            
            # AI 분석 (선택적)
            if user.user_type in ['premium', 'admin']:
                ai_analysis = managers['ai'].analyze_land_with_ai(land_data.to_dict())
                report['ai_analysis'] = ai_analysis
            
            # 가격 예측
            price_prediction = managers['price_predictor'].predict_price(land_data.to_dict())
            report['price_prediction'] = {
                'predicted_price': price_prediction.predicted_price,
                'confidence_score': price_prediction.confidence_score,
                'price_range_min': price_prediction.price_range_min,
                'price_range_max': price_prediction.price_range_max,
                'factors': price_prediction.factors
            }
            
            # 데이터베이스 저장
            record_id = managers['db'].save_land_analysis(
                user.user_id, land_data.to_dict(), report
            )
            
            results.append({
                'land_data': land_data,
                'report': report,
                'record_id': record_id
            })
            
            # API 사용량 증가
            managers['auth'].increment_api_usage(user.user_id)
            
        except Exception as e:
            st.error(f"❌ {land_data.address}: 분석 실패 - {str(e)}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if results:
        st.success(f"✅ {len(results)}개 토지 분석 완료!")
        
        # 첫 번째 결과 표시
        if results:
            st.session_state.current_analysis = results[0]['report']
            st.markdown("---")
            st.markdown("## 📊 분석 결과 (첫 번째 토지)")
            show_analysis_results(results[0]['report'])
        
        # 전체 결과 다운로드
        if len(results) > 1:
            st.markdown("---")
            st.markdown("### 📥 전체 결과 다운로드")
            
            all_results_json = json.dumps(
                [r['report'] for r in results],
                ensure_ascii=False,
                indent=2
            )
            
            st.download_button(
                label=f"📄 전체 {len(results)}개 결과 다운로드 (JSON)",
                data=all_results_json,
                file_name=f"토지분석결과_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def show_usage_history():
    """사용 이력 페이지"""
    st.title("📋 사용 이력")
    
    user = st.session_state.user
    
    tab1, tab2, tab3 = st.tabs(["🔍 분석 이력", "💬 상담 이력", "📊 통계"])
    
    with tab1:
        st.markdown("### 🔍 토지 분석 이력")
        
        land_records = managers['db'].get_user_land_records(user.user_id, limit=50)
        
        if land_records:
            df = pd.DataFrame(land_records)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at', ascending=False)
            
            # 필터
            col1, col2 = st.columns(2)
            with col1:
                date_filter = st.date_input("기간 필터", value=datetime.now().date() - timedelta(days=30))
            with col2:
                category_filter = st.selectbox("지목 필터", ["전체"] + df['land_category'].unique().tolist())
            
            # 필터 적용
            filtered_df = df[df['created_at'].dt.date >= date_filter]
            if category_filter != "전체":
                filtered_df = filtered_df[filtered_df['land_category'] == category_filter]
            
            # 테이블 표시
            display_columns = ['created_at', 'address', 'land_category', 'area', 'zone_type']
            st.dataframe(
                filtered_df[display_columns].rename(columns={
                    'created_at': '분석일시',
                    'address': '주소',
                    'land_category': '지목',
                    'area': '면적(㎡)',
                    'zone_type': '용도지역'
                }),
                use_container_width=True
            )
            
            # 상세 보기
            if st.button("선택한 분석 결과 다시 보기"):
                selected_idx = st.selectbox("분석 결과 선택", range(len(filtered_df)))
                if selected_idx is not None:
                    selected_record = filtered_df.iloc[selected_idx]
                    st.json(selected_record['analysis_result'])
        
        else:
            st.info("분석 이력이 없습니다.")
    
    with tab2:
        st.markdown("### 💬 AI 상담 이력")
        
        chat_history = managers['db'].get_user_chat_history(user.user_id, limit=100)
        
        if chat_history:
            for chat in chat_history[:20]:  # 최근 20개만 표시
                with st.expander(f"💭 {chat['user_message'][:50]}... ({chat['created_at'][:10]})"):
                    st.markdown(f"**질문**: {chat['user_message']}")
                    st.markdown(f"**답변**: {chat['ai_response']}")
                    st.caption(f"시간: {chat['created_at']}")
        else:
            st.info("상담 이력이 없습니다.")
    
    with tab3:
        st.markdown("### 📊 사용 통계")
        
        analytics = managers['db'].get_analytics_data(user.user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 분석 건수", analytics['land_analyses'])
        with col2:
            st.metric("총 상담 횟수", analytics['chat_messages'])
        with col3:
            st.metric("등록 고객 수", analytics['customers'])
        
        # 월별 사용량 차트 (모의 데이터)
        st.markdown("#### 📈 월별 사용량")
        
        months = pd.date_range(start='2024-01', end='2024-10', freq='M')
        usage_data = {
            '분석': [5, 8, 12, 15, 10, 18, 22, 25, 20, 30],
            '상담': [15, 20, 25, 30, 28, 35, 40, 45, 38, 50]
        }
        
        chart_df = pd.DataFrame(usage_data, index=months)
        st.line_chart(chart_df)

if __name__ == "__main__":
    main()