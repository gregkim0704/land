"""
토지 전문 AI 시스템 - 웹 인터페이스
Streamlit 기반 대시보드
"""

import streamlit as st
import json
from datetime import datetime
from land_ai_core import LandInfo, LandAnalyzer, LandMatcher
from land_ai_chatbot import LandConsultingBot, SmartDocumentAnalyzer

# 페이지 설정
st.set_page_config(
    page_title="토지전문 AI 컨설팅 시스템",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = LandConsultingBot()
if 'analyzed_lands' not in st.session_state:
    st.session_state.analyzed_lands = []
if 'matcher' not in st.session_state:
    st.session_state.matcher = LandMatcher()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 사이드바 - 메뉴
st.sidebar.title("🏞️ 토지 AI 시스템")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "메뉴 선택",
    ["🏠 홈", "🔍 토지 분석", "💬 AI 상담", "🎯 고객 매칭", "📄 계약서 분석", "📊 시장 리포트"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**개발**: 토지전문 AI 시스템  
**버전**: 1.0.0 MVP  
**업데이트**: 2025-10-23
""")


# === 홈 화면 ===
if menu == "🏠 홈":
    st.title("🏞️ 토지전문 부동산 AI 컨설팅 시스템")
    st.markdown("### AI 기술로 토지 투자를 스마트하게! 💡")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("분석된 토지", f"{len(st.session_state.analyzed_lands)}건")
    with col2:
        st.metric("AI 상담 횟수", f"{len(st.session_state.chat_history)}회")
    with col3:
        st.metric("등록 고객", f"{len(st.session_state.matcher.customer_profiles)}명")
    
    st.markdown("---")
    
    # 주요 기능 소개
    st.markdown("## 🎯 주요 기능")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔍 토지 종합 분석
        - 건축 규제 자동 조회
        - 개발 가능성 점수 산출
        - 시장 가격 예측
        - 투자 수익률 분석
        - 리스크 체크리스트
        
        ### 💬 24시간 AI 컨설팅
        - 토지 투자 기본 상담
        - 법규 및 절차 안내
        - 세금 관련 조언
        - 실시간 질의응답
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 스마트 매칭 시스템
        - 고객 투자 성향 분석
        - 최적 토지 추천
        - 맞춤형 포트폴리오 제안
        
        ### 📄 스마트 문서 분석
        - 계약서 리스크 검토
        - 주요 조항 자동 추출
        - 법적 이슈 사전 경고
        
        ### 📊 시장 동향 분석
        - 지역별 거래 동향
        - 가격 트렌드 분석
        - 투자 유망 지역 식별
        """)
    
    st.markdown("---")
    
    # 시작하기 가이드
    st.markdown("## 🚀 시작하기")
    st.info("""
    1. **토지 분석** 메뉴에서 분석하고 싶은 토지 정보를 입력하세요.
    2. **AI 상담** 메뉴에서 토지 투자 관련 궁금한 점을 질문하세요.
    3. **고객 매칭** 메뉴에서 투자자 프로필에 맞는 토지를 추천받으세요.
    """)


# === 토지 분석 ===
elif menu == "🔍 토지 분석":
    st.title("🔍 토지 종합 분석")
    st.markdown("토지 정보를 입력하면 AI가 종합적으로 분석해드립니다.")
    
    # 입력 폼
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
        
        submitted = st.form_submit_button("🔍 분석 시작", use_container_width=True)
    
    if submitted:
        with st.spinner("AI가 토지를 분석하고 있습니다..."):
            # 토지 정보 생성
            land = LandInfo(
                address=address,
                land_category=land_category,
                area=area,
                official_price=official_price,
                zone_type=zone_type,
                district=district,
                road_contact=road_contact,
                nearest_station_km=nearest_station_km,
            )
            
            # 분석 수행
            analyzer = LandAnalyzer(land)
            report = analyzer.generate_comprehensive_report()
            
            # 세션에 저장
            st.session_state.analyzed_lands.append(report)
            st.session_state.chatbot.add_land_context(report)
            
            st.success("✅ 분석이 완료되었습니다!")
        
        # 결과 표시
        st.markdown("---")
        st.markdown("## 📊 분석 결과")
        
        # 탭으로 구성
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📌 기본정보", "🏗️ 건축규제", "📈 개발가능성", "💰 가격분석", "⚠️ 리스크"
        ])
        
        with tab1:
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
        
        with tab2:
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
        
        with tab3:
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
        
        with tab4:
            st.markdown("### 💰 시장 가격 분석")
            price = report["시장가격_분석"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("예상 단가", f"{price['예상_단가_만원_평']}만원/평")
            with col2:
                st.metric("예상 총액", f"{price['예상_총액_억원']}억원")
            with col3:
                st.metric("공시지가 배율", f"{price['공시지가_대비_배율']}배")
            
            st.info(f"""
            💰 **예상 가격 범위**  
            {price['가격_범위_하단_억원']}억원 ~ {price['가격_범위_상단_억원']}억원
            
            *(공시지가 대비 약 {price['공시지가_대비_배율']}배 수준)*
            """)
            
            # 투자 수익률 계산
            st.markdown("#### 📊 투자 수익률 시뮬레이션")
            
            purchase_price = st.slider(
                "매입가 설정 (억원)",
                min_value=float(price['가격_범위_하단_억원']),
                max_value=float(price['가격_범위_상단_억원'] * 1.2),
                value=float(price['예상_총액_억원']),
                step=0.1
            )
            
            hold_years = st.slider("보유 기간 (년)", 1, 10, 5)
            
            roi = analyzer.calculate_investment_return(
                purchase_price * 100000000,
                hold_years
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("예상 매각가", f"{roi['예상_매각가_억원']}억원")
            with col2:
                st.metric("순수익", f"{roi['순수익_억원']}억원")
            with col3:
                st.metric("연평균 수익률", f"{roi['연평균수익률_퍼센트']}%")
        
        with tab5:
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
        
        # 리포트 다운로드
        st.markdown("---")
        st.markdown("### 📥 리포트 다운로드")
        
        col1, col2 = st.columns(2)
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
            text_report = f"""
토지 종합 분석 리포트
생성일시: {report['생성일시']}
주소: {report['기본정보']['주소']}
개발가능성: {report['개발가능성']['개발가능성_등급']}
예상 시세: {report['시장가격_분석']['예상_총액_억원']}억원
            """
            st.download_button(
                label="📝 텍스트 다운로드",
                data=text_report,
                file_name=f"land_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )


# === AI 상담 ===
elif menu == "💬 AI 상담":
    st.title("💬 AI 토지 컨설팅")
    st.markdown("토지 투자 관련 궁금한 점을 AI 전문가에게 물어보세요!")
    
    # 채팅 히스토리 표시
    st.markdown("### 💬 상담 내역")
    
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.chatbot.conversation_history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(msg["content"])
    
    # 입력 창
    user_input = st.chat_input("질문을 입력하세요... (예: 농지 투자 어떤가요?)")
    
    if user_input:
        # 사용자 메시지 표시
        with st.chat_message("user"):
            st.write(user_input)
        
        # AI 응답 생성
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI가 답변을 생성하고 있습니다..."):
                response = st.session_state.chatbot.chat(user_input)
                st.write(response)
        
        st.session_state.chat_history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })
    
    # 사이드 정보
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 추천 질문")
    st.sidebar.markdown("""
    - 농지 투자 어떤가요?
    - 임야 개발이 가능한가요?
    - 맹지는 왜 문제인가요?
    - 토지 세금은 얼마나 나오나요?
    - 역세권 토지 추천해주세요
    - 농지전용 절차가 궁금해요
    """)


# === 고객 매칭 ===
elif menu == "🎯 고객 매칭":
    st.title("🎯 스마트 고객-토지 매칭")
    st.markdown("투자자의 프로필에 맞는 최적의 토지를 AI가 추천합니다.")
    
    # 탭 구성
    tab1, tab2 = st.tabs(["👤 고객 등록", "🎯 토지 추천"])
    
    with tab1:
        st.markdown("### 👤 고객 프로필 등록")
        
        with st.form("customer_profile_form"):
            name = st.text_input("고객명", "김투자")
            
            col1, col2 = st.columns(2)
            with col1:
                budget_min = st.number_input("최소 예산 (억원)", 1, 100, 5)
                budget_max = st.number_input("최대 예산 (억원)", 1, 100, 20)
            with col2:
                investment_purpose = st.selectbox(
                    "투자 목적",
                    ["단기차익", "중장기보유", "개발사업"]
                )
                risk_tolerance = st.selectbox(
                    "위험 성향",
                    ["공격적", "보통", "보수적"]
                )
            
            preferred_zones = st.multiselect(
                "선호 용도지역",
                ["주거지역", "상업지역", "공업지역", "녹지지역"],
                ["주거지역", "상업지역"]
            )
            
            preferred_categories = st.multiselect(
                "선호 지목",
                ["대지", "전", "답", "과수원", "임야", "목장용지"],
                ["대지"]
            )
            
            submitted = st.form_submit_button("✅ 등록하기")
            
            if submitted:
                profile = st.session_state.matcher.create_customer_profile(
                    name=name,
                    budget_min=budget_min,
                    budget_max=budget_max,
                    investment_purpose=investment_purpose,
                    risk_tolerance=risk_tolerance,
                    preferred_zones=preferred_zones,
                    preferred_categories=preferred_categories,
                )
                st.success(f"✅ {name}님의 프로필이 등록되었습니다!")
                st.json(profile)
    
    with tab2:
        st.markdown("### 🎯 맞춤형 토지 추천")
        
        if not st.session_state.matcher.customer_profiles:
            st.warning("먼저 고객 프로필을 등록해주세요.")
        elif not st.session_state.analyzed_lands:
            st.warning("먼저 토지 분석을 진행해주세요.")
        else:
            customer_names = [p["고객명"] for p in st.session_state.matcher.customer_profiles]
            selected_customer = st.selectbox("고객 선택", customer_names)
            
            if st.button("🎯 추천 받기", use_container_width=True):
                with st.spinner("AI가 최적의 토지를 찾고 있습니다..."):
                    recommendations = st.session_state.matcher.recommend_lands(
                        selected_customer,
                        st.session_state.analyzed_lands
                    )
                
                st.markdown("### 📋 추천 결과")
                
                for idx, rec in enumerate(recommendations, 1):
                    with st.expander(f"#{idx} {rec['매칭등급']} - {rec['토지주소']}", expanded=(idx==1)):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("매칭 점수", f"{rec['매칭점수']}점")
                        with col2:
                            st.metric("예상 가격", f"{rec['예상가격_억원']}억원")
                        with col3:
                            st.metric("개발가능성", rec['개발가능성'])
                        
                        st.markdown("#### 💡 추천 이유")
                        for reason in rec['추천이유']:
                            st.write(f"• {reason}")


# === 계약서 분석 ===
elif menu == "📄 계약서 분석":
    st.title("📄 스마트 계약서 분석")
    st.markdown("계약서를 업로드하면 AI가 주요 조항과 리스크를 분석합니다.")
    
    st.info("💡 이 기능은 참고용이며, 중요한 계약은 반드시 법률 전문가와 상담하세요.")
    
    # 샘플 계약서 텍스트 입력
    contract_text = st.text_area(
        "계약서 내용을 붙여넣으세요",
        height=300,
        placeholder="계약서 전문을 여기에 입력하거나 붙여넣으세요..."
    )
    
    if st.button("🔍 계약서 분석하기", use_container_width=True):
        if not contract_text:
            st.warning("계약서 내용을 입력해주세요.")
        else:
            with st.spinner("AI가 계약서를 분석하고 있습니다..."):
                analyzer = SmartDocumentAnalyzer()
                result = analyzer.analyze_contract(contract_text)
            
            st.success("✅ 분석이 완료되었습니다!")
            
            # 탭으로 결과 표시
            tab1, tab2, tab3, tab4 = st.tabs([
                "✅ 주요 조항", "⚠️ 위험 요소", "📋 추가 확인사항", "📝 종합 의견"
            ])
            
            with tab1:
                st.markdown("### ✅ 주요 조항 확인")
                for item in result["주요조항_확인"]:
                    with st.expander(f"{item['확인']} {item['항목']}"):
                        st.write(f"**주의사항**: {item['주의사항']}")
            
            with tab2:
                st.markdown("### ⚠️ 위험 요소")
                for risk in result["위험요소"]:
                    st.warning(risk)
            
            with tab3:
                st.markdown("### 📋 추가 확인사항")
                for check in result["추가확인사항"]:
                    st.info(check)
            
            with tab4:
                st.markdown("### 📝 종합 의견")
                st.info(result["종합의견"])


# === 시장 리포트 ===
elif menu == "📊 시장 리포트":
    st.title("📊 토지 시장 동향 리포트")
    st.markdown("최신 토지 시장 트렌드와 투자 인사이트를 제공합니다.")
    
    st.info("🚧 이 기능은 개발 중입니다. 실제 데이터 연동 후 제공될 예정입니다.")
    
    # 임시 데모 데이터
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("전국 평균 공시지가", "15.2만원/평", "+3.5%")
    with col2:
        st.metric("이번 달 거래량", "1,234건", "+12.3%")
    with col3:
        st.metric("유망 투자 지역", "경기 남부", "")
    
    st.markdown("### 📈 가격 트렌드 (예시)")
    st.line_chart({
        "2024-01": 100,
        "2024-02": 102,
        "2024-03": 105,
        "2024-04": 103,
        "2024-05": 107,
        "2024-06": 110,
    })
    
    st.markdown("### 🗺️ 지역별 평균 가격 (만원/평)")
    st.bar_chart({
        "강남구": 5000,
        "서초구": 4500,
        "송파구": 3800,
        "분당구": 3200,
        "수지구": 2800,
    })
    
    st.markdown("### 💡 이번 달 투자 인사이트")
    st.success("""
    ✅ **GTX 노선 주변 토지 주목**  
    GTX-A 노선 개통이 임박하면서 역세권 토지 가격이 상승 중입니다.
    
    ✅ **3기 신도시 주변 선투자 기회**  
    남양주, 하남, 인천계양 등 3기 신도시 주변 토지가 주목받고 있습니다.
    
    ⚠️ **녹지지역 규제 강화 주의**  
    최근 개발제한구역 해제가 어려워지고 있어 신중한 접근이 필요합니다.
    """)
