"""
토지 전문 부동산 AI 시스템 - 핵심 분석 엔진
Land Analysis AI System - Core Engine
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random


@dataclass
class LandInfo:
    """토지 기본 정보"""
    address: str
    land_category: str  # 지목: 대지, 전, 답, 임야 등
    area: float  # 면적 (평방미터)
    official_price: float  # 공시지가 (원/㎡)
    zone_type: str  # 용도지역
    district: str  # 용도지구
    road_contact: bool  # 도로 접함 여부
    nearest_station_km: float  # 최근접 역까지 거리
    
    def area_in_pyeong(self) -> float:
        """평수 변환"""
        return round(self.area * 0.3025, 2)
    
    def total_official_value(self) -> int:
        """총 공시지가"""
        return int(self.area * self.official_price)


class LandAnalyzer:
    """토지 종합 분석기"""
    
    # 용도지역별 건폐율/용적률 (일반적 기준)
    ZONE_REGULATIONS = {
        "제1종전용주거지역": {"building_coverage": 50, "floor_area_ratio": 100},
        "제2종전용주거지역": {"building_coverage": 50, "floor_area_ratio": 150},
        "제1종일반주거지역": {"building_coverage": 60, "floor_area_ratio": 200},
        "제2종일반주거지역": {"building_coverage": 60, "floor_area_ratio": 250},
        "제3종일반주거지역": {"building_coverage": 50, "floor_area_ratio": 300},
        "준주거지역": {"building_coverage": 70, "floor_area_ratio": 500},
        "중심상업지역": {"building_coverage": 90, "floor_area_ratio": 1500},
        "일반상업지역": {"building_coverage": 80, "floor_area_ratio": 1300},
        "근린상업지역": {"building_coverage": 70, "floor_area_ratio": 900},
        "일반공업지역": {"building_coverage": 70, "floor_area_ratio": 350},
        "준공업지역": {"building_coverage": 70, "floor_area_ratio": 400},
        "자연녹지지역": {"building_coverage": 20, "floor_area_ratio": 100},
        "생산녹지지역": {"building_coverage": 20, "floor_area_ratio": 100},
        "보전녹지지역": {"building_coverage": 20, "floor_area_ratio": 80},
    }
    
    def __init__(self, land_info: LandInfo):
        self.land = land_info
    
    def get_building_regulations(self) -> Dict:
        """건축 규제 정보 조회"""
        regulations = self.ZONE_REGULATIONS.get(
            self.land.zone_type, 
            {"building_coverage": 60, "floor_area_ratio": 200}
        )
        
        return {
            "용도지역": self.land.zone_type,
            "건폐율": f"{regulations['building_coverage']}%",
            "용적률": f"{regulations['floor_area_ratio']}%",
            "건축가능면적_m2": round(self.land.area * regulations['building_coverage'] / 100, 2),
            "건축가능면적_평": round(self.land.area * 0.3025 * regulations['building_coverage'] / 100, 2),
            "최대연면적_m2": round(self.land.area * regulations['floor_area_ratio'] / 100, 2),
            "최대연면적_평": round(self.land.area * 0.3025 * regulations['floor_area_ratio'] / 100, 2),
        }
    
    def analyze_development_potential(self) -> Dict:
        """개발 가능성 분석"""
        score = 0
        factors = []
        
        # 1. 면적 평가 (20점)
        area_pyeong = self.land.area_in_pyeong()
        if area_pyeong >= 300:
            score += 20
            factors.append("대규모 개발 가능 (300평 이상)")
        elif area_pyeong >= 100:
            score += 15
            factors.append("중규모 개발 가능 (100평 이상)")
        elif area_pyeong >= 50:
            score += 10
            factors.append("소규모 개발 가능 (50평 이상)")
        else:
            score += 5
            factors.append("협소지 (50평 미만)")
        
        # 2. 용도지역 평가 (30점)
        if "상업" in self.land.zone_type:
            score += 30
            factors.append("상업지역 - 수익성 우수")
        elif "주거" in self.land.zone_type:
            score += 25
            factors.append("주거지역 - 안정적 수요")
        elif "공업" in self.land.zone_type:
            score += 20
            factors.append("공업지역 - 임대/매각 용이")
        else:
            score += 10
            factors.append("녹지/기타지역 - 개발 제한")
        
        # 3. 도로 접함 여부 (20점)
        if self.land.road_contact:
            score += 20
            factors.append("도로 접함 - 건축 가능")
        else:
            score += 5
            factors.append("맹지 가능성 - 진입로 확인 필요")
        
        # 4. 접근성 평가 (30점)
        if self.land.nearest_station_km <= 0.5:
            score += 30
            factors.append("역세권 (500m 이내) - 최우수 입지")
        elif self.land.nearest_station_km <= 1.0:
            score += 25
            factors.append("역 인접 (1km 이내) - 우수 입지")
        elif self.land.nearest_station_km <= 2.0:
            score += 15
            factors.append("역 도보권 (2km 이내)")
        else:
            score += 5
            factors.append("역 거리 다소 멀음")
        
        # 등급 결정
        if score >= 85:
            grade = "S (최우수)"
        elif score >= 70:
            grade = "A (우수)"
        elif score >= 55:
            grade = "B (양호)"
        elif score >= 40:
            grade = "C (보통)"
        else:
            grade = "D (신중검토)"
        
        return {
            "개발가능성_점수": score,
            "개발가능성_등급": grade,
            "주요_요인": factors,
        }
    
    def estimate_market_price(self) -> Dict:
        """시장 예상 가격 산정 (공시지가 기반)"""
        # 일반적으로 시세는 공시지가의 1.2~2.0배
        # 용도지역과 입지에 따라 승수 조정
        
        multiplier = 1.5  # 기본 승수
        
        # 용도지역별 조정
        if "상업" in self.land.zone_type:
            multiplier = 1.8
        elif "준주거" in self.land.zone_type:
            multiplier = 1.7
        elif "주거" in self.land.zone_type:
            multiplier = 1.6
        elif "녹지" in self.land.zone_type:
            multiplier = 1.3
        
        # 역세권 추가 가산
        if self.land.nearest_station_km <= 0.5:
            multiplier += 0.3
        elif self.land.nearest_station_km <= 1.0:
            multiplier += 0.2
        
        # 도로 접함 가산
        if self.land.road_contact:
            multiplier += 0.1
        
        estimated_unit_price = int(self.land.official_price * multiplier)
        estimated_total_price = int(self.land.area * estimated_unit_price)
        
        return {
            "예상_단가_원_m2": estimated_unit_price,
            "예상_단가_만원_평": int(estimated_unit_price * 0.3025 / 10000),
            "예상_총액_원": estimated_total_price,
            "예상_총액_억원": round(estimated_total_price / 100000000, 2),
            "공시지가_대비_배율": round(multiplier, 2),
            "가격_범위_하단_억원": round(estimated_total_price * 0.9 / 100000000, 2),
            "가격_범위_상단_억원": round(estimated_total_price * 1.1 / 100000000, 2),
        }
    
    def calculate_investment_return(self, purchase_price: float, hold_years: int = 5) -> Dict:
        """투자 수익률 분석"""
        # 연평균 상승률 가정 (보수적)
        annual_appreciation = 0.05  # 5%
        
        # 보유세 (재산세) 가정: 공시지가의 0.2~0.5%
        annual_tax_rate = 0.003
        annual_tax = self.land.total_official_value() * annual_tax_rate
        
        # 미래 가치 계산
        future_value = purchase_price * (1 + annual_appreciation) ** hold_years
        total_tax_paid = annual_tax * hold_years
        
        # 양도소득세 (간이 계산: 양도차익의 약 30%)
        capital_gain = future_value - purchase_price
        capital_gain_tax = capital_gain * 0.3 if capital_gain > 0 else 0
        
        # 순수익
        net_profit = capital_gain - total_tax_paid - capital_gain_tax
        roi = (net_profit / purchase_price * 100) if purchase_price > 0 else 0
        
        return {
            "매입가_억원": round(purchase_price / 100000000, 2),
            "보유기간_년": hold_years,
            "예상_매각가_억원": round(future_value / 100000000, 2),
            "양도차익_억원": round(capital_gain / 100000000, 2),
            "총_보유세_만원": round(total_tax_paid / 10000, 0),
            "양도소득세_억원": round(capital_gain_tax / 100000000, 2),
            "순수익_억원": round(net_profit / 100000000, 2),
            "투자수익률_퍼센트": round(roi, 2),
            "연평균수익률_퍼센트": round(roi / hold_years, 2),
        }
    
    def check_risks(self) -> List[Dict]:
        """리스크 체크"""
        risks = []
        
        # 1. 맹지 리스크
        if not self.land.road_contact:
            risks.append({
                "리스크_유형": "진입로 확인 필요",
                "심각도": "상",
                "설명": "도로 접함 정보가 없습니다. 맹지일 경우 건축이 불가능하거나 진입로 확보 비용이 발생합니다.",
                "대응방안": "지적도 및 현장 확인, 통행권 확보 여부 확인"
            })
        
        # 2. 녹지지역 개발 제한
        if "녹지" in self.land.zone_type:
            risks.append({
                "리스크_유형": "개발행위 제한",
                "심각도": "상",
                "설명": "녹지지역은 건폐율/용적률이 매우 낮고 개발행위허가가 까다롭습니다.",
                "대응방안": "용도변경 가능성 확인, 지구단위계획 수립 여부 조사"
            })
        
        # 3. 소규모 토지
        if self.land.area_in_pyeong() < 50:
            risks.append({
                "리스크_유형": "협소지 활용 제한",
                "심각도": "중",
                "설명": "50평 미만 소규모 토지는 활용도가 제한적일 수 있습니다.",
                "대응방안": "인접 토지 매입 검토, 소형 건축물 계획"
            })
        
        # 4. 역세권 외 입지
        if self.land.nearest_station_km > 2.0:
            risks.append({
                "리스크_유형": "접근성 부족",
                "심각도": "중",
                "설명": "역과 거리가 멀어 대중교통 접근성이 떨어집니다.",
                "대응방안": "버스노선 확인, 자동차 이용 전제, 향후 교통개선계획 조사"
            })
        
        # 5. 농지/임야 전용 이슈
        if self.land.land_category in ["전", "답", "과수원"]:
            risks.append({
                "리스크_유형": "농지전용 필요",
                "심각도": "상",
                "설명": "농지를 다른 용도로 사용하려면 농지전용허가가 필요합니다.",
                "대응방안": "농지전용부담금 확인 (공시지가의 30%), 전용 가능 여부 사전 확인"
            })
        
        if self.land.land_category == "임야":
            risks.append({
                "리스크_유형": "산지전용 필요",
                "심각도": "상",
                "설명": "임야를 개발하려면 산지전용허가가 필요하며, 대체산림자원조성비가 발생합니다.",
                "대응방안": "산지전용 가능 여부 확인, 대체비용 산정 (㎡당 수만원)"
            })
        
        if not risks:
            risks.append({
                "리스크_유형": "없음",
                "심각도": "낮음",
                "설명": "현재 식별된 주요 리스크가 없습니다.",
                "대응방안": "정밀 실사 진행 권장"
            })
        
        return risks
    
    def generate_comprehensive_report(self) -> Dict:
        """종합 분석 리포트 생성"""
        return {
            "기본정보": {
                "주소": self.land.address,
                "지목": self.land.land_category,
                "면적_m2": self.land.area,
                "면적_평": self.land.area_in_pyeong(),
                "공시지가_원_m2": self.land.official_price,
                "총_공시지가_원": self.land.total_official_value(),
                "용도지역": self.land.zone_type,
                "용도지구": self.land.district,
            },
            "건축규제": self.get_building_regulations(),
            "개발가능성": self.analyze_development_potential(),
            "시장가격_분석": self.estimate_market_price(),
            "리스크_분석": self.check_risks(),
            "생성일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


class LandMatcher:
    """고객-토지 매칭 시스템"""
    
    def __init__(self):
        self.customer_profiles = []
    
    def create_customer_profile(
        self,
        name: str,
        budget_min: float,
        budget_max: float,
        investment_purpose: str,  # "단기차익", "중장기보유", "개발사업"
        risk_tolerance: str,  # "공격적", "보통", "보수적"
        preferred_zones: List[str],
        preferred_categories: List[str],
    ) -> Dict:
        """고객 프로필 생성"""
        profile = {
            "고객명": name,
            "예산_최소_억원": budget_min,
            "예산_최대_억원": budget_max,
            "투자목적": investment_purpose,
            "위험성향": risk_tolerance,
            "선호_용도지역": preferred_zones,
            "선호_지목": preferred_categories,
            "프로필_생성일": datetime.now().strftime("%Y-%m-%d"),
        }
        self.customer_profiles.append(profile)
        return profile
    
    def calculate_matching_score(
        self, 
        customer_profile: Dict, 
        land_analysis: Dict
    ) -> Tuple[float, List[str]]:
        """매칭 점수 계산"""
        score = 0
        reasons = []
        
        # 1. 예산 적합도 (30점)
        price = land_analysis["시장가격_분석"]["예상_총액_억원"]
        budget_min = customer_profile["예산_최소_억원"]
        budget_max = customer_profile["예산_최대_억원"]
        
        if budget_min <= price <= budget_max:
            score += 30
            reasons.append(f"예산 범위 적합 ({price}억원)")
        elif price < budget_min:
            score += 20
            reasons.append(f"예산보다 저렴 ({price}억원)")
        else:
            score += 5
            reasons.append(f"예산 초과 주의 ({price}억원)")
        
        # 2. 개발가능성 (25점)
        dev_score = land_analysis["개발가능성"]["개발가능성_점수"]
        score += dev_score * 0.25
        reasons.append(f"개발가능성: {land_analysis['개발가능성']['개발가능성_등급']}")
        
        # 3. 투자목적 적합도 (25점)
        purpose = customer_profile["투자목적"]
        zone = land_analysis["기본정보"]["용도지역"]
        
        if purpose == "단기차익":
            if "상업" in zone or "준주거" in zone:
                score += 25
                reasons.append("단기차익에 유리한 지역")
            else:
                score += 10
        elif purpose == "중장기보유":
            if "주거" in zone or "녹지" in zone:
                score += 25
                reasons.append("안정적 보유에 적합")
            else:
                score += 15
        elif purpose == "개발사업":
            if dev_score >= 70:
                score += 25
                reasons.append("개발사업 추진 가능")
            else:
                score += 5
        
        # 4. 리스크 수준 (20점)
        risk_level = customer_profile["위험성향"]
        risk_count = len([r for r in land_analysis["리스크_분석"] if r["심각도"] == "상"])
        
        if risk_level == "공격적":
            score += 20 - (risk_count * 2)
            reasons.append(f"리스크 요인 {risk_count}건")
        elif risk_level == "보통":
            score += 20 - (risk_count * 5)
            if risk_count <= 1:
                reasons.append("적정 리스크 수준")
        else:  # 보수적
            score += 20 - (risk_count * 10)
            if risk_count == 0:
                reasons.append("안정적 투자처")
        
        return round(score, 1), reasons
    
    def recommend_lands(
        self, 
        customer_name: str, 
        available_lands: List[Dict]
    ) -> List[Dict]:
        """토지 추천"""
        # 고객 프로필 찾기
        profile = next(
            (p for p in self.customer_profiles if p["고객명"] == customer_name), 
            None
        )
        if not profile:
            return []
        
        recommendations = []
        for land_report in available_lands:
            score, reasons = self.calculate_matching_score(profile, land_report)
            
            recommendations.append({
                "토지주소": land_report["기본정보"]["주소"],
                "매칭점수": score,
                "매칭등급": self._get_matching_grade(score),
                "추천이유": reasons,
                "예상가격_억원": land_report["시장가격_분석"]["예상_총액_억원"],
                "개발가능성": land_report["개발가능성"]["개발가능성_등급"],
            })
        
        # 점수 순으로 정렬
        recommendations.sort(key=lambda x: x["매칭점수"], reverse=True)
        return recommendations
    
    @staticmethod
    def _get_matching_grade(score: float) -> str:
        """매칭 등급 결정"""
        if score >= 80:
            return "⭐⭐⭐ 강력추천"
        elif score >= 65:
            return "⭐⭐ 추천"
        elif score >= 50:
            return "⭐ 검토가능"
        else:
            return "부적합"


# 테스트 실행 코드
if __name__ == "__main__":
    # 샘플 토지 데이터 생성
    sample_land = LandInfo(
        address="경기도 성남시 분당구 정자동 123-45",
        land_category="대지",
        area=500.0,  # 500㎡ (약 151평)
        official_price=3000000,  # ㎡당 300만원
        zone_type="제2종일반주거지역",
        district="일반",
        road_contact=True,
        nearest_station_km=0.8,
    )
    
    # 분석 수행
    analyzer = LandAnalyzer(sample_land)
    report = analyzer.generate_comprehensive_report()
    
    # 결과 출력
    print("=" * 80)
    print("토지 종합 분석 리포트")
    print("=" * 80)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    # 투자 수익률 분석
    print("\n" + "=" * 80)
    print("투자 수익률 분석 (매입가 20억원 가정)")
    print("=" * 80)
    investment = analyzer.calculate_investment_return(
        purchase_price=2000000000,  # 20억원
        hold_years=5
    )
    print(json.dumps(investment, ensure_ascii=False, indent=2))
