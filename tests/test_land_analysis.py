"""
토지 분석 시스템 테스트
"""

import pytest
from land_ai_core import LandInfo, LandAnalyzer


class TestLandAnalysis:
    """토지 분석 테스트"""
    
    @pytest.fixture
    def sample_land(self):
        """테스트용 토지 정보"""
        return LandInfo(
            address="경기도 성남시 분당구 정자동 123-45",
            land_category="대지",
            area=500.0,
            official_price=3000000,
            zone_type="제2종일반주거지역",
            district="일반",
            road_contact=True,
            nearest_station_km=0.8
        )
    
    def test_land_info_creation(self, sample_land):
        """토지 정보 생성 테스트"""
        assert sample_land.address == "경기도 성남시 분당구 정자동 123-45"
        assert sample_land.area == 500.0
        assert sample_land.area_in_pyeong() == pytest.approx(151.25, rel=1e-2)
        assert sample_land.total_official_value() == 1500000000
    
    def test_land_analyzer(self, sample_land):
        """토지 분석기 테스트"""
        analyzer = LandAnalyzer(sample_land)
        
        # 건축 규제 분석
        regulations = analyzer.analyze_building_regulations()
        assert "건폐율" in regulations
        assert "용적률" in regulations
        assert regulations["건폐율"] == "60%"
        assert regulations["용적률"] == "250%"
    
    def test_development_potential(self, sample_land):
        """개발 가능성 분석 테스트"""
        analyzer = LandAnalyzer(sample_land)
        potential = analyzer.analyze_development_potential()
        
        assert "개발가능성_점수" in potential
        assert "개발가능성_등급" in potential
        assert 0 <= potential["개발가능성_점수"] <= 100
        assert potential["개발가능성_등급"] in ["S", "A", "B", "C", "D"]
    
    def test_price_analysis(self, sample_land):
        """가격 분석 테스트"""
        analyzer = LandAnalyzer(sample_land)
        price_analysis = analyzer.analyze_market_price()
        
        assert "예상_단가_만원_평" in price_analysis
        assert "예상_총액_억원" in price_analysis
        assert price_analysis["예상_단가_만원_평"] > 0
        assert price_analysis["예상_총액_억원"] > 0
    
    def test_risk_analysis(self, sample_land):
        """리스크 분석 테스트"""
        analyzer = LandAnalyzer(sample_land)
        risks = analyzer.analyze_risks()
        
        assert isinstance(risks, list)
        for risk in risks:
            assert "리스크_유형" in risk
            assert "심각도" in risk
            assert "설명" in risk
            assert "대응방안" in risk
            assert risk["심각도"] in ["상", "중", "낮음"]
    
    def test_comprehensive_report(self, sample_land):
        """종합 리포트 테스트"""
        analyzer = LandAnalyzer(sample_land)
        report = analyzer.generate_comprehensive_report()
        
        # 필수 섹션 확인
        required_sections = [
            "기본정보", "건축규제", "개발가능성", 
            "시장가격_분석", "리스크_분석", "생성일시"
        ]
        
        for section in required_sections:
            assert section in report
    
    def test_investment_return_calculation(self, sample_land):
        """투자 수익률 계산 테스트"""
        analyzer = LandAnalyzer(sample_land)
        
        purchase_price = 2000000000  # 20억원
        hold_years = 5
        
        roi = analyzer.calculate_investment_return(purchase_price, hold_years)
        
        assert "예상_매각가_억원" in roi
        assert "순수익_억원" in roi
        assert "연평균수익률_퍼센트" in roi
        assert roi["예상_매각가_억원"] > 0
        assert roi["연평균수익률_퍼센트"] >= 0