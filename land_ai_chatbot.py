"""
토지 전문 AI 컨설팅 챗봇
Land Consulting AI Chatbot powered by Claude
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class LandConsultingBot:
    """토지 전문 AI 컨설팅 챗봇"""
    
    # 시스템 프롬프트 (전문가 페르소나)
    SYSTEM_PROMPT = """당신은 20년 경력의 토지 전문 부동산 컨설턴트입니다.

# 전문 분야
- 농지, 임야, 대지 등 모든 지목의 토지 거래
- 개발행위허가, 용도변경, 농지전용, 산지전용
- 토지 투자 전략 및 리스크 관리
- 부동산 관련 세금 (취득세, 양도소득세, 재산세)
- 토지 개발 및 사업성 분석

# 법률 지식
- 국토의 계획 및 이용에 관한 법률
- 농지법, 산지관리법
- 건축법, 주택법
- 부동산 거래신고 등에 관한 법률

# 상담 원칙
1. **정확성**: 불확실한 정보는 추측하지 않고 확인이 필요함을 명확히 전달
2. **리스크 고지**: 투자 리스크를 반드시 설명
3. **법률 준수**: 탈법 또는 불법 행위는 절대 조언하지 않음
4. **실무 중심**: 이론보다 실제 거래 경험을 바탕으로 조언
5. **고객 맞춤**: 고객의 투자 목적, 예산, 성향을 고려한 상담

# 상담 스타일
- 전문가답게 정확하되, 고객이 이해하기 쉽게 설명
- 복잡한 법률 용어는 쉬운 말로 풀어서 설명
- 실제 사례를 들어 구체적으로 설명
- 단계별로 명확하게 안내

# 제한사항
- 특정 토지의 매수/매도를 강요하지 않음
- 가격 상승을 보장하지 않음
- 최종 의사결정은 고객의 몫임을 강조
- 복잡한 법률 문제는 변호사 상담 권유
- 세무 관련 복잡한 사안은 세무사 상담 권유
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        챗봇 초기화
        
        Args:
            api_key: Claude API 키 (실제 운영 시 필요)
        """
        self.api_key = api_key
        self.conversation_history: List[Dict] = []
        self.land_database = []  # 분석된 토지 정보 저장
    
    def add_land_context(self, land_report: Dict):
        """
        분석된 토지 정보를 챗봇 컨텍스트에 추가
        
        Args:
            land_report: LandAnalyzer가 생성한 종합 리포트
        """
        self.land_database.append(land_report)
    
    def _create_land_context_message(self) -> str:
        """현재 참조 가능한 토지 정보를 컨텍스트로 생성"""
        if not self.land_database:
            return ""
        
        context = "\n\n# 현재 분석 가능한 토지 정보\n"
        for idx, land in enumerate(self.land_database, 1):
            info = land["기본정보"]
            price = land["시장가격_분석"]
            dev = land["개발가능성"]
            
            context += f"""
## 토지 #{idx}: {info['주소']}
- 지목: {info['지목']} / 면적: {info['면적_평']}평
- 용도지역: {info['용도지역']}
- 예상 시세: {price['예상_총액_억원']}억원
- 개발가능성: {dev['개발가능성_등급']}
"""
        return context
    
    def chat(self, user_message: str) -> str:
        """
        사용자 메시지에 대한 응답 생성
        
        Args:
            user_message: 사용자의 질문/메시지
            
        Returns:
            AI 응답
        """
        # 대화 기록에 추가
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 실제 구현에서는 Claude API 호출
        # 여기서는 시뮬레이션
        response = self._generate_response(user_message)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, user_message: str) -> str:
        """
        실제로는 Claude API를 호출하지만, 
        여기서는 규칙 기반 데모 응답 생성
        """
        msg_lower = user_message.lower()
        
        # 토지 정보 컨텍스트
        land_context = self._create_land_context_message()
        
        # 키워드 기반 응답 (실제로는 Claude API 사용)
        if "농지" in user_message or "전용" in user_message:
            return f"""네, 농지 전용에 대해 말씀드리겠습니다.

**농지전용이란?**
농지를 농업 생산 이외의 목적(주택, 공장, 상가 등)으로 사용하기 위해 용도를 변경하는 것입니다.

**농지전용 절차:**
1. 농지전용허가 신청 (시/군/구청)
2. 농지전용부담금 납부 (공시지가의 30%)
3. 허가 후 2년 이내 목적사업 착수

**주요 체크사항:**
- 농지전용이 불가능한 농업진흥지역인지 확인 필수
- 농지전용부담금이 상당하므로 투자 계획에 반영
- 전용 후 실제 목적사업 미착수 시 이행강제금 부과

**실무 팁:**
농지 매입 전에 반드시 해당 지자체에 전용 가능 여부를 사전 문의하세요. 
같은 농지라도 위치에 따라 전용 가능 여부가 다릅니다.

{land_context}

추가로 궁금하신 점이 있으시면 말씀해 주세요."""

        elif "임야" in user_message or "산지" in user_message:
            return """임야 투자에 관심이 있으시군요.

**임야의 특징:**
- 장점: 가격이 상대적으로 저렴, 장기 보유 시 가치 상승 가능
- 단점: 개발 제한이 많고, 산지전용 비용이 높음

**산지전용 관련:**
- 대체산림자원조성비: ㎡당 수만원 (지역에 따라 다름)
- 보전산지는 전용이 매우 어려움
- 준보전산지도 까다로운 심사 필요

**투자 시 주의사항:**
1. 접근성: 차량 진입이 가능한지 확인
2. 경사도: 너무 급경사면 활용도 저하
3. 용도지역: 관리지역 내 임야가 상대적으로 유리
4. 개발계획: 인근 도로 개설, 택지개발 등 확인

임야는 저렴하지만 활용하기까지 시간과 비용이 많이 듭니다.
장기 관점에서 접근하시는 것을 권장합니다."""

        elif "세금" in user_message or "취득세" in user_message or "양도세" in user_message:
            return """토지 관련 세금에 대해 설명드리겠습니다.

**1. 취득 단계**
- 취득세: 토지 취득가액의 4% (원칙)
  * 농지: 3% (자경 목적)
  * 주거용 토지: 1~3%

**2. 보유 단계**
- 재산세: 공시지가 기준 0.2~0.5%
- 종합부동산세: 일정 금액 초과 시 추가 과세

**3. 양도 단계**
- 양도소득세: 양도차익에 대해 6~45% (누진세율)
  * 기본세율: 6~45%
  * 비사업용 토지: 최대 60% (중과)
  * 1년 미만 보유: 70%
  * 2년 미만 보유: 60%

**절세 전략:**
- 장기 보유: 2년 이상 보유 시 일반세율 적용
- 사업용 토지: 실제 사업에 활용하면 중과 배제
- 자경 농지: 8년 이상 자경 시 양도세 감면

⚠️ 세금은 개인 상황에 따라 크게 달라지므로,
구체적인 절세 전략은 세무사와 상담하시길 권장합니다."""

        elif "맹지" in user_message or "도로" in user_message:
            return """도로와 맹지 문제는 토지 투자에서 가장 중요한 체크포인트입니다!

**맹지(盲地)란?**
도로에 접하지 않아 차량 진입이 불가능한 토지를 말합니다.

**건축법상 도로 기준:**
- 폭 4m 이상의 도로에 2m 이상 접해야 건축 가능
- 단, 소규모 건축물은 완화 규정 있음

**맹지 해결 방법:**
1. **통행권 확보**: 인접 토지 소유자와 협의
2. **주위토지통행권**: 법적으로 통행권 확보 (비용 발생)
3. **진입로 직접 개설**: 도로까지 토지 매입

**투자 시 주의사항:**
- 지적도상 도로 접함 확인
- 현장 방문하여 실제 차량 진입 가능 여부 확인
- 도로 폭 측정 (줄자 지참)
- 인근 토지 소유자 관계 파악

💡 **실무 팁**: 맹지는 일반 시세의 30~50% 저렴하지만,
진입로 확보 비용을 고려하면 실익이 없을 수 있습니다.
반드시 전문가와 함께 현장 실사하세요!"""

        elif "가격" in user_message or "시세" in user_message:
            response = """토지 가격 산정에 대해 말씀드리겠습니다.

**토지 가격의 기준:**
1. **공시지가** (정부 고시)
   - 매년 1월 1일 기준으로 조사
   - 실제 시세의 70~80% 수준

2. **실거래가** (시장 가격)
   - 공시지가의 1.2~2.0배
   - 지역, 용도, 입지에 따라 편차 큼

**가격에 영향을 주는 요소:**
- 용도지역 (상업 > 주거 > 녹지)
- 교통 접근성 (역세권, 도로 인접)
- 개발 계획 (택지, 도로, 철도 등)
- 토지 형태 (정형지 선호)
- 도로 접함 여부 (맹지는 큰 폭 하락)

**가격 조사 방법:**
1. 국토교통부 실거래가 공개시스템 확인
2. 부동산114, 네이버 부동산 시세 조회
3. 인근 공인중개사 3곳 이상 문의
4. 유사 토지 최근 거래 사례 비교
"""
            
            if land_context:
                response += f"\n{land_context}\n\n위 토지들의 가격 분석 결과를 참고하세요."
            
            return response

        elif "인사" in msg_lower or "안녕" in user_message or "처음" in user_message:
            return """안녕하세요! 토지 전문 부동산 컨설턴트입니다. 😊

20년간 수천 건의 토지 거래를 중개하고 상담해온 경험을 바탕으로
고객님의 토지 투자를 도와드리겠습니다.

**상담 가능한 분야:**
✅ 토지 매입 상담 (농지, 임야, 대지 등)
✅ 개발 가능성 분석
✅ 용도변경, 농지전용, 산지전용
✅ 투자 수익률 분석
✅ 세금 및 법률 기본 상담
✅ 리스크 관리

궁금하신 점을 편하게 질문해 주세요!
예: "역세권 토지 투자 어떤가요?", "농지 전용 절차가 궁금해요" 등"""

        else:
            # 기본 응답
            return f"""질문 감사합니다: "{user_message}"

토지 투자는 매우 전문적인 영역이기 때문에,
구체적인 상황을 알려주시면 더 정확한 상담이 가능합니다.

**추가로 알려주시면 좋은 정보:**
- 투자 목적 (단기 차익 / 장기 보유 / 개발)
- 예산 규모
- 선호하는 지역
- 선호하는 지목 (농지, 임야, 대지 등)
- 위험 성향 (공격적 / 보통 / 보수적)

{land_context if land_context else ""}

더 구체적으로 질문해 주시면 맞춤형 상담을 해드리겠습니다!"""
    
    def get_conversation_summary(self) -> Dict:
        """대화 요약 정보 반환"""
        return {
            "총_대화수": len(self.conversation_history),
            "상담_시작": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "최근_대화": self.conversation_history[-1]["timestamp"] if self.conversation_history else None,
            "참조_토지수": len(self.land_database),
        }
    
    def export_conversation(self, filepath: str):
        """대화 내역 저장"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": self.get_conversation_summary(),
                "history": self.conversation_history,
            }, f, ensure_ascii=False, indent=2)


class SmartDocumentAnalyzer:
    """스마트 계약서/서류 분석기"""
    
    @staticmethod
    def analyze_contract(contract_text: str) -> Dict:
        """
        계약서 분석 (실제로는 Claude API 활용)
        
        Args:
            contract_text: 계약서 전문
            
        Returns:
            분석 결과
        """
        # 실제 구현에서는 Claude API로 계약서 분석
        # 여기서는 기본 체크리스트 반환
        
        checklist = {
            "주요조항_확인": [
                {"항목": "매매대금", "확인": "✅", "주의사항": "총액, 계약금, 중도금, 잔금 비율 확인"},
                {"항목": "소유권이전시기", "확인": "⚠️", "주의사항": "잔금일과 동시 이전 원칙"},
                {"항목": "인도일자", "확인": "✅", "주의사항": "실제 인도 가능 날짜 확인"},
                {"항목": "공과금부담", "확인": "✅", "주의사항": "미납 세금 확인 필수"},
                {"항목": "하자담보책임", "확인": "⚠️", "주의사항": "토지 경계, 면적 오차 책임 명시"},
            ],
            "위험요소": [
                "소유권이전 시기가 명확하지 않음 - 구체적 날짜 명시 필요",
                "토지 면적 차이 발생 시 처리방법 미기재",
                "중개보수 부담 주체 불명확",
            ],
            "추가확인사항": [
                "등기부등본상 권리관계 확인 (근저당, 가압류 등)",
                "토지이용계획확인원 필수 확인",
                "실제 측량 면적과 등기부 면적 대조",
                "미납 세금 확인 (재산세, 종부세 등)",
            ],
            "종합의견": "전반적으로 표준 계약서 양식을 따르고 있으나, 일부 조항의 구체화가 필요합니다. 특히 소유권이전 시기와 면적 차이 발생 시 처리 방법을 명확히 하시기 바랍니다.",
        }
        
        return checklist


# 테스트 실행
if __name__ == "__main__":
    print("=" * 80)
    print("토지 전문 AI 컨설팅 챗봇 시뮬레이션")
    print("=" * 80)
    
    # 챗봇 초기화
    bot = LandConsultingBot()
    
    # 샘플 대화
    conversations = [
        "안녕하세요, 토지 투자를 처음 해보려고 합니다.",
        "농지를 사서 집을 지으려면 어떻게 해야 하나요?",
        "농지전용 비용이 얼마나 드나요?",
        "임야 투자는 어떤가요?",
        "맹지는 왜 문제인가요?",
    ]
    
    for user_msg in conversations:
        print(f"\n👤 고객: {user_msg}")
        response = bot.chat(user_msg)
        print(f"\n🤖 AI 컨설턴트:\n{response}")
        print("-" * 80)
    
    # 대화 요약
    print("\n" + "=" * 80)
    print("상담 요약")
    print("=" * 80)
    print(json.dumps(bot.get_conversation_summary(), ensure_ascii=False, indent=2))
