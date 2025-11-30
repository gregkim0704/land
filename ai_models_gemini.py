"""
AI 모델 통합 시스템 - Gemini & Claude 지원
AI Models Integration System with Gemini & Claude Support
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np
import pandas as pd
from dataclasses import dataclass

# AI/ML 라이브러리
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_absolute_error, r2_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


@dataclass
class PredictionResult:
    """예측 결과"""
    predicted_price: float
    confidence_score: float
    price_range_min: float
    price_range_max: float
    factors: List[str]
    model_version: str


class UnifiedAIManager:
    """통합 AI 관리자 (Gemini & Claude)"""
    
    def __init__(self, prefer_gemini: bool = True):
        """
        Args:
            prefer_gemini: True면 기본적으로 Gemini 사용 (비용 효율적)
        """
        self.prefer_gemini = prefer_gemini
        self.setup_logging()
        
        # Gemini 초기화
        self.gemini_model = None
        self.gemini_available = False
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
                self.logger.info("✅ Gemini AI initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Gemini AI: {e}")
        
        # Claude 초기화
        self.claude_client = None
        self.claude_available = False
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if claude_key and ANTHROPIC_AVAILABLE:
            try:
                self.claude_client = anthropic.Anthropic(api_key=claude_key)
                self.claude_available = True
                self.logger.info("✅ Claude AI initialized successfully")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize Claude AI: {e}")
        
        # 사용 가능한 AI 확인
        if not self.gemini_available and not self.claude_available:
            self.logger.warning("⚠️ No AI service available - using mock responses")
        
        # 활성 프로바이더 결정
        if prefer_gemini and self.gemini_available:
            self.active_provider = "gemini"
        elif self.claude_available:
            self.active_provider = "claude"
        elif self.gemini_available:
            self.active_provider = "gemini"
        else:
            self.active_provider = "mock"
        
        self.logger.info(f"🎯 Active AI Provider: {self.active_provider.upper()}")
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_land_with_ai(self, land_data: Dict, market_data: Dict = None, 
                            use_premium: bool = False) -> Dict:
        """
        AI를 활용한 토지 분석
        
        Args:
            land_data: 토지 정보
            market_data: 시장 데이터
            use_premium: True면 Claude 사용 (더 정확), False면 Gemini 우선
        """
        prompt = self._create_analysis_prompt(land_data, market_data)
        
        # 프리미엄 요청이고 Claude가 사용 가능하면 Claude 사용
        if use_premium and self.claude_available:
            return self._analyze_with_claude(prompt, land_data)
        
        # 기본적으로 Gemini 사용 (비용 효율적)
        if self.gemini_available:
            return self._analyze_with_gemini(prompt, land_data)
        
        # Gemini가 없으면 Claude 사용
        if self.claude_available:
            return self._analyze_with_claude(prompt, land_data)
        
        # 둘 다 없으면 모의 응답
        return self._get_mock_ai_analysis(land_data)
    
    def _analyze_with_gemini(self, prompt: str, land_data: Dict) -> Dict:
        """Gemini로 분석"""
        try:
            response = self.gemini_model.generate_content(prompt)
            ai_response = response.text
            self.logger.info("✅ Gemini analysis completed")
            return self._parse_ai_response(ai_response)
        except Exception as e:
            self.logger.error(f"❌ Gemini analysis failed: {e}")
            return self._get_mock_ai_analysis(land_data)
    
    def _analyze_with_claude(self, prompt: str, land_data: Dict) -> Dict:
        """Claude로 분석"""
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            ai_response = response.content[0].text
            self.logger.info("✅ Claude analysis completed")
            return self._parse_ai_response(ai_response)
        except Exception as e:
            self.logger.error(f"❌ Claude analysis failed: {e}")
            return self._get_mock_ai_analysis(land_data)
    
    def chat_consultation(self, user_message: str, context: Dict = None, 
                         use_premium: bool = False) -> str:
        """
        AI 상담 채팅
        
        Args:
            user_message: 사용자 질문
            context: 추가 컨텍스트
            use_premium: True면 Claude 사용, False면 Gemini 우선
        """
        system_prompt = """당신은 20년 경력의 토지 전문 부동산 컨설턴트입니다.

전문 분야:
- 농지, 임야, 대지 등 모든 지목의 토지 거래
- 개발행위허가, 용도변경, 농지전용, 산지전용
- 토지 투자 전략 및 리스크 관리
- 부동산 관련 세금 상담

상담 원칙:
1. 정확하고 실무적인 조언 제공
2. 리스크를 명확히 고지
3. 법률 준수 강조
4. 고객 맞춤형 상담
5. 이해하기 쉬운 설명

한국어로 전문적이면서도 친근하게 답변해주세요."""

        full_prompt = f"{system_prompt}\n\n사용자 질문: {user_message}"
        
        # 프리미엄 요청이고 Claude가 사용 가능하면 Claude 사용
        if use_premium and self.claude_available:
            return self._chat_with_claude(full_prompt, system_prompt, user_message)
        
        # 기본적으로 Gemini 사용
        if self.gemini_available:
            return self._chat_with_gemini(full_prompt)
        
        # Gemini가 없으면 Claude 사용
        if self.claude_available:
            return self._chat_with_claude(full_prompt, system_prompt, user_message)
        
        # 둘 다 없으면 모의 응답
        return self._get_mock_chat_response(user_message)
    
    def _chat_with_gemini(self, prompt: str) -> str:
        """Gemini로 채팅"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"❌ Gemini chat failed: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def _chat_with_claude(self, full_prompt: str, system_prompt: str, user_message: str) -> str:
        """Claude로 채팅"""
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            return response.content[0].text
        except Exception as e:
            self.logger.error(f"❌ Claude chat failed: {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def analyze_contract(self, contract_text: str, use_premium: bool = False) -> Dict:
        """
        계약서 분석
        
        Args:
            contract_text: 계약서 내용
            use_premium: True면 Claude 사용 (더 정확)
        """
        prompt = f"""다음 부동산 계약서를 분석하여 주요 조항과 리스크를 식별해주세요:

계약서 내용:
{contract_text}

분석 항목:
1. 주요 조항 확인 (매매가격, 잔금일, 특약사항 등)
2. 위험 요소 식별
3. 추가 확인이 필요한 사항
4. 종합 의견

JSON 형식으로 답변해주세요."""

        # 프리미엄 요청이고 Claude가 사용 가능하면 Claude 사용
        if use_premium and self.claude_available:
            return self._analyze_contract_with_claude(prompt)
        
        # 기본적으로 Gemini 사용
        if self.gemini_available:
            return self._analyze_contract_with_gemini(prompt)
        
        # Gemini가 없으면 Claude 사용
        if self.claude_available:
            return self._analyze_contract_with_claude(prompt)
        
        # 둘 다 없으면 모의 응답
        return self._get_mock_contract_analysis()
    
    def _analyze_contract_with_gemini(self, prompt: str) -> Dict:
        """Gemini로 계약서 분석"""
        try:
            response = self.gemini_model.generate_content(prompt)
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return self._structure_contract_response(response.text)
        except Exception as e:
            self.logger.error(f"❌ Gemini contract analysis failed: {e}")
            return self._get_mock_contract_analysis()
    
    def _analyze_contract_with_claude(self, prompt: str) -> Dict:
        """Claude로 계약서 분석"""
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            try:
                return json.loads(response.content[0].text)
            except json.JSONDecodeError:
                return self._structure_contract_response(response.content[0].text)
        except Exception as e:
            self.logger.error(f"❌ Claude contract analysis failed: {e}")
            return self._get_mock_contract_analysis()
    
    def _create_analysis_prompt(self, land_data: Dict, market_data: Dict = None) -> str:
        """분석 프롬프트 생성"""
        prompt = f"""토지 전문가로서 다음 토지를 분석해주세요:

토지 정보:
- 주소: {land_data.get('address', '')}
- 지목: {land_data.get('land_category', '')}
- 면적: {land_data.get('area', 0)}㎡
- 공시지가: {land_data.get('official_price', 0):,}원/㎡
- 용도지역: {land_data.get('zone_type', '')}

분석 요청사항:
1. 개발 가능성 평가 (점수와 등급)
2. 투자 리스크 분석
3. 예상 시장가격 범위
4. 투자 추천도

JSON 형식으로 구조화된 분석 결과를 제공해주세요."""
        
        if market_data:
            prompt += f"\n\n시장 데이터:\n{json.dumps(market_data, ensure_ascii=False, indent=2)}"
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict:
        """AI 응답 파싱"""
        try:
            # JSON 추출 시도
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # JSON 파싱 실패 시 기본 구조 반환
        return {
            "개발가능성": {"점수": 75, "등급": "B"},
            "리스크": ["현장 확인 필요"],
            "예상가격": {"최소": 0, "최대": 0},
            "추천도": "보통",
            "ai_response": response
        }
    
    def _structure_contract_response(self, response: str) -> Dict:
        """계약서 응답 구조화"""
        return {
            "주요조항_확인": [
                {"항목": "매매가격", "확인": "✓", "주의사항": "시세 대비 적정성 확인 필요"}
            ],
            "위험요소": ["계약서 전문 검토 권장"],
            "추가확인사항": ["법무사 검토 필요"],
            "종합의견": response[:500] + "..." if len(response) > 500 else response
        }
    
    def _get_mock_ai_analysis(self, land_data: Dict) -> Dict:
        """모의 AI 분석 결과"""
        return {
            "개발가능성": {
                "점수": 78,
                "등급": "B+",
                "주요요인": ["교통 접근성 양호", "용도지역 적합"]
            },
            "리스크분석": [
                {"유형": "법적 리스크", "수준": "낮음", "설명": "일반적인 개발 절차 필요"},
                {"유형": "시장 리스크", "수준": "보통", "설명": "시장 변동성 고려 필요"}
            ],
            "예상가격": {
                "최소": land_data.get('official_price', 0) * 1.8,
                "최대": land_data.get('official_price', 0) * 2.5,
                "추정": land_data.get('official_price', 0) * 2.1
            },
            "투자추천": "보통 - 안정적 투자처"
        }
    
    def _get_mock_chat_response(self, user_message: str) -> str:
        """모의 채팅 응답"""
        responses = {
            "농지": "농지 투자는 농지법에 따른 제약이 있습니다. 농지전용 가능성을 먼저 확인하시고, 전용부담금도 고려하셔야 합니다.",
            "임야": "임야는 산지관리법의 적용을 받습니다. 산지전용허가 가능 여부와 경사도, 접도 조건을 꼼꼼히 확인하세요.",
            "세금": "토지 취득 시 취득세가 부과되며, 보유 시 재산세, 매각 시 양도소득세가 발생할 수 있습니다. 세무사 상담을 권합니다.",
            "맹지": "맹지는 도로에 접하지 않은 토지로, 통행권 확보가 중요합니다. 주변 토지 소유자와의 협의나 법적 절차가 필요할 수 있습니다."
        }
        
        for keyword, response in responses.items():
            if keyword in user_message:
                return response
        
        return "토지 투자는 다양한 요소를 종합적으로 고려해야 합니다. 구체적인 질문을 해주시면 더 정확한 답변을 드릴 수 있습니다."
    
    def _get_mock_contract_analysis(self) -> Dict:
        """모의 계약서 분석"""
        return {
            "주요조항_확인": [
                {"항목": "매매가격", "확인": "✓", "주의사항": "시세 대비 적정성 확인"},
                {"항목": "잔금일", "확인": "✓", "주의사항": "대출 승인 기간 고려"},
                {"항목": "특약사항", "확인": "△", "주의사항": "세부 조건 명확화 필요"}
            ],
            "위험요소": [
                "토지이용계획 변경 가능성",
                "개발행위허가 취득 불확실성",
                "접도 조건 미확인"
            ],
            "추가확인사항": [
                "토지이용계획확인원 발급",
                "지적도 및 측량 결과 확인",
                "주변 개발 계획 조사"
            ],
            "종합의견": "전반적으로 표준적인 계약서이나, 토지 특성상 개발 관련 조건을 더 명확히 할 필요가 있습니다."
        }
    
    def get_provider_info(self) -> Dict:
        """현재 AI 프로바이더 정보"""
        return {
            "active_provider": self.active_provider,
            "gemini_available": self.gemini_available,
            "claude_available": self.claude_available,
            "prefer_gemini": self.prefer_gemini
        }


# 하위 호환성을 위한 별칭
ClaudeAIManager = UnifiedAIManager
AIManager = UnifiedAIManager


class LandPricePredictor:
    """토지 가격 예측 모델"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.setup_logging()
        
        if SKLEARN_AVAILABLE:
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        else:
            self.logger.warning("Scikit-learn not available - using simple prediction")
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def prepare_features(self, land_data: Dict, market_data: Dict = None) -> np.ndarray:
        """특성 준비"""
        features = []
        
        # 기본 특성
        features.extend([
            land_data.get('area', 0),
            land_data.get('official_price', 0),
            land_data.get('nearest_station_km', 5.0),
            1 if land_data.get('road_contact', False) else 0
        ])
        
        # 용도지역 인코딩
        zone_encoding = {
            '제1종전용주거지역': 1, '제2종전용주거지역': 2,
            '제1종일반주거지역': 3, '제2종일반주거지역': 4, '제3종일반주거지역': 5,
            '준주거지역': 6, '중심상업지역': 10, '일반상업지역': 9, '근린상업지역': 8,
            '일반공업지역': 7, '준공업지역': 7, '자연녹지지역': 2
        }
        features.append(zone_encoding.get(land_data.get('zone_type', ''), 3))
        
        # 지목 인코딩
        category_encoding = {
            '대지': 5, '전': 3, '답': 3, '과수원': 4, '임야': 2,
            '목장용지': 3, '공장용지': 6, '학교용지': 4
        }
        features.append(category_encoding.get(land_data.get('land_category', ''), 3))
        
        return np.array(features).reshape(1, -1)
    
    def predict_price(self, land_data: Dict, market_data: Dict = None) -> PredictionResult:
        """가격 예측"""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._simple_price_prediction(land_data)
        
        features = self.prepare_features(land_data, market_data)
        features_scaled = self.scaler.transform(features)
        
        # 예측
        predicted_price = self.model.predict(features_scaled)[0]
        
        # 신뢰도 계산
        confidence = min(0.95, max(0.6, self._calculate_confidence(land_data)))
        
        # 가격 범위 계산
        margin = predicted_price * (1 - confidence) * 0.5
        price_min = predicted_price - margin
        price_max = predicted_price + margin
        
        return PredictionResult(
            predicted_price=predicted_price,
            confidence_score=confidence,
            price_range_min=price_min,
            price_range_max=price_max,
            factors=self._get_prediction_factors(land_data),
            model_version="v1.0"
        )
    
    def _simple_price_prediction(self, land_data: Dict) -> PredictionResult:
        """간단한 가격 예측"""
        official_price = land_data.get('official_price', 0)
        area = land_data.get('area', 0)
        
        # 공시지가 기반 추정
        multiplier = 2.0
        
        # 용도지역별 조정
        zone_multipliers = {
            '중심상업지역': 3.5, '일반상업지역': 3.0, '근린상업지역': 2.8,
            '준주거지역': 2.5, '제3종일반주거지역': 2.3, '제2종일반주거지역': 2.1,
            '제1종일반주거지역': 1.9, '제2종전용주거지역': 1.8, '제1종전용주거지역': 1.7
        }
        
        zone_type = land_data.get('zone_type', '')
        multiplier = zone_multipliers.get(zone_type, multiplier)
        
        # 접도 조건 조정
        if not land_data.get('road_contact', True):
            multiplier *= 0.7
        
        # 역세권 조정
        station_km = land_data.get('nearest_station_km', 5.0)
        if station_km <= 0.5:
            multiplier *= 1.3
        elif station_km <= 1.0:
            multiplier *= 1.2
        elif station_km <= 2.0:
            multiplier *= 1.1
        
        predicted_price = official_price * area * multiplier
        
        return PredictionResult(
            predicted_price=predicted_price,
            confidence_score=0.75,
            price_range_min=predicted_price * 0.85,
            price_range_max=predicted_price * 1.15,
            factors=[
                f"공시지가 기준 {multiplier:.1f}배 적용",
                f"용도지역: {zone_type}",
                f"역세권: {station_km}km"
            ],
            model_version="simple_v1.0"
        )
    
    def _calculate_confidence(self, land_data: Dict) -> float:
        """신뢰도 계산"""
        confidence = 0.8
        required_fields = ['address', 'area', 'official_price', 'zone_type']
        completeness = sum(1 for field in required_fields if land_data.get(field)) / len(required_fields)
        confidence *= completeness
        return confidence
    
    def _get_prediction_factors(self, land_data: Dict) -> List[str]:
        """예측 요인 설명"""
        factors = []
        
        if land_data.get('road_contact'):
            factors.append("도로 접함 - 접근성 양호")
        else:
            factors.append("맹지 - 접근성 제약")
        
        station_km = land_data.get('nearest_station_km', 5.0)
        if station_km <= 1.0:
            factors.append("역세권 - 교통 편리")
        
        zone_type = land_data.get('zone_type', '')
        if '상업' in zone_type:
            factors.append("상업지역 - 개발 가치 높음")
        elif '주거' in zone_type:
            factors.append("주거지역 - 안정적 수요")
        
        return factors
