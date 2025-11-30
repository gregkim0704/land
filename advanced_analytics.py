"""
고급 분석 및 리포팅 시스템
Advanced Analytics and Reporting System
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import logging
from dataclasses import dataclass
from io import BytesIO
import base64

# PDF 생성용
try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


@dataclass
class AnalyticsResult:
    """분석 결과"""
    analysis_type: str
    data: Dict
    charts: List[Dict]
    insights: List[str]
    recommendations: List[str]
    created_at: datetime


class MarketAnalyzer:
    """시장 분석기"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def analyze_price_trends(self, transaction_data: List[Dict], period_months: int = 12) -> AnalyticsResult:
        """가격 트렌드 분석"""
        if not transaction_data:
            return self._create_mock_trend_analysis()
        
        # 데이터프레임 생성
        df = pd.DataFrame(transaction_data)
        df['deal_date'] = pd.to_datetime(df['deal_year'].astype(str) + '-' + 
                                       df['deal_month'].astype(str).str.zfill(2) + '-01')
        df['price_per_sqm'] = df['deal_amount'] * 10000 / df['area']  # 원/㎡
        
        # 월별 집계
        monthly_stats = df.groupby(df['deal_date'].dt.to_period('M')).agg({
            'deal_amount': ['mean', 'count', 'sum'],
            'price_per_sqm': ['mean', 'median', 'std'],
            'area': 'mean'
        }).round(2)
        
        # 트렌드 계산
        trend_data = self._calculate_price_trend(monthly_stats)
        
        # 차트 생성
        charts = [
            self._create_price_trend_chart(monthly_stats),
            self._create_volume_chart(monthly_stats),
            self._create_price_distribution_chart(df)
        ]
        
        # 인사이트 생성
        insights = self._generate_trend_insights(trend_data, monthly_stats)
        
        # 추천사항
        recommendations = self._generate_trend_recommendations(trend_data)
        
        return AnalyticsResult(
            analysis_type="price_trends",
            data=trend_data,
            charts=charts,
            insights=insights,
            recommendations=recommendations,
            created_at=datetime.now()
        )
    
    def analyze_regional_comparison(self, regions_data: Dict[str, List[Dict]]) -> AnalyticsResult:
        """지역별 비교 분석"""
        comparison_data = {}
        
        for region, transactions in regions_data.items():
            if transactions:
                df = pd.DataFrame(transactions)
                df['price_per_sqm'] = df['deal_amount'] * 10000 / df['area']
                
                comparison_data[region] = {
                    'avg_price_per_sqm': df['price_per_sqm'].mean(),
                    'median_price_per_sqm': df['price_per_sqm'].median(),
                    'transaction_count': len(df),
                    'total_volume': df['deal_amount'].sum(),
                    'avg_area': df['area'].mean(),
                    'price_volatility': df['price_per_sqm'].std() / df['price_per_sqm'].mean()
                }
        
        # 차트 생성
        charts = [
            self._create_regional_comparison_chart(comparison_data),
            self._create_regional_volume_chart(comparison_data)
        ]
        
        # 인사이트 생성
        insights = self._generate_regional_insights(comparison_data)
        
        return AnalyticsResult(
            analysis_type="regional_comparison",
            data=comparison_data,
            charts=charts,
            insights=insights,
            recommendations=self._generate_regional_recommendations(comparison_data),
            created_at=datetime.now()
        )
    
    def analyze_investment_opportunity(self, land_data: Dict, market_context: Dict) -> AnalyticsResult:
        """투자 기회 분석"""
        # 투자 점수 계산
        investment_score = self._calculate_investment_score(land_data, market_context)
        
        # 리스크 분석
        risk_analysis = self._analyze_investment_risks(land_data, market_context)
        
        # 수익률 시뮬레이션
        roi_simulation = self._simulate_roi_scenarios(land_data, market_context)
        
        # 차트 생성
        charts = [
            self._create_investment_radar_chart(investment_score),
            self._create_roi_simulation_chart(roi_simulation),
            self._create_risk_assessment_chart(risk_analysis)
        ]
        
        analysis_data = {
            'investment_score': investment_score,
            'risk_analysis': risk_analysis,
            'roi_simulation': roi_simulation,
            'recommendation': self._get_investment_recommendation(investment_score, risk_analysis)
        }
        
        return AnalyticsResult(
            analysis_type="investment_opportunity",
            data=analysis_data,
            charts=charts,
            insights=self._generate_investment_insights(analysis_data),
            recommendations=self._generate_investment_recommendations(analysis_data),
            created_at=datetime.now()
        )
    
    def _calculate_price_trend(self, monthly_stats: pd.DataFrame) -> Dict:
        """가격 트렌드 계산"""
        if len(monthly_stats) < 2:
            return {'trend': 'insufficient_data'}
        
        prices = monthly_stats[('price_per_sqm', 'mean')].values
        
        # 선형 회귀로 트렌드 계산
        x = np.arange(len(prices))
        slope, intercept = np.polyfit(x, prices, 1)
        
        # 변화율 계산
        recent_price = prices[-1]
        previous_price = prices[-2] if len(prices) > 1 else prices[-1]
        change_rate = ((recent_price - previous_price) / previous_price * 100) if previous_price > 0 else 0
        
        return {
            'trend_slope': slope,
            'trend_direction': 'up' if slope > 0 else 'down' if slope < 0 else 'stable',
            'monthly_change_rate': change_rate,
            'volatility': np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0,
            'current_price': recent_price
        }
    
    def _calculate_investment_score(self, land_data: Dict, market_context: Dict) -> Dict:
        """투자 점수 계산"""
        scores = {}
        
        # 위치 점수 (0-100)
        location_score = 70  # 기본 점수
        if land_data.get('nearest_station_km', 5) <= 1.0:
            location_score += 20
        elif land_data.get('nearest_station_km', 5) <= 2.0:
            location_score += 10
        
        if land_data.get('road_contact', False):
            location_score += 10
        
        scores['location'] = min(100, location_score)
        
        # 개발 가능성 점수
        development_score = 60
        zone_type = land_data.get('zone_type', '')
        if '상업' in zone_type:
            development_score += 30
        elif '주거' in zone_type:
            development_score += 20
        elif '공업' in zone_type:
            development_score += 15
        
        scores['development'] = min(100, development_score)
        
        # 시장 점수
        market_score = 70
        if market_context.get('trend_direction') == 'up':
            market_score += 20
        elif market_context.get('trend_direction') == 'stable':
            market_score += 10
        
        scores['market'] = min(100, market_score)
        
        # 유동성 점수
        liquidity_score = 50
        if land_data.get('land_category') == '대지':
            liquidity_score += 30
        elif land_data.get('land_category') in ['전', '답']:
            liquidity_score += 20
        
        scores['liquidity'] = min(100, liquidity_score)
        
        # 종합 점수
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _analyze_investment_risks(self, land_data: Dict, market_context: Dict) -> Dict:
        """투자 리스크 분석"""
        risks = {
            'legal_risk': {'level': 'low', 'factors': []},
            'market_risk': {'level': 'medium', 'factors': []},
            'liquidity_risk': {'level': 'medium', 'factors': []},
            'development_risk': {'level': 'low', 'factors': []}
        }
        
        # 법적 리스크
        if land_data.get('land_category') in ['전', '답']:
            risks['legal_risk']['level'] = 'high'
            risks['legal_risk']['factors'].append('농지전용 절차 필요')
        
        if land_data.get('land_category') == '임야':
            risks['legal_risk']['level'] = 'high'
            risks['legal_risk']['factors'].append('산지전용 절차 필요')
        
        # 시장 리스크
        volatility = market_context.get('volatility', 0)
        if volatility > 0.3:
            risks['market_risk']['level'] = 'high'
            risks['market_risk']['factors'].append('높은 가격 변동성')
        
        # 유동성 리스크
        if not land_data.get('road_contact', True):
            risks['liquidity_risk']['level'] = 'high'
            risks['liquidity_risk']['factors'].append('맹지로 인한 거래 제약')
        
        return risks
    
    def _simulate_roi_scenarios(self, land_data: Dict, market_context: Dict) -> Dict:
        """수익률 시나리오 시뮬레이션"""
        purchase_price = land_data.get('area', 0) * land_data.get('official_price', 0) * 2.0
        
        scenarios = {}
        
        # 낙관적 시나리오 (연 10% 상승)
        scenarios['optimistic'] = self._calculate_roi_scenario(purchase_price, 0.10, [1, 3, 5, 10])
        
        # 보통 시나리오 (연 5% 상승)
        scenarios['normal'] = self._calculate_roi_scenario(purchase_price, 0.05, [1, 3, 5, 10])
        
        # 비관적 시나리오 (연 2% 상승)
        scenarios['pessimistic'] = self._calculate_roi_scenario(purchase_price, 0.02, [1, 3, 5, 10])
        
        return scenarios
    
    def _calculate_roi_scenario(self, purchase_price: float, annual_growth: float, years: List[int]) -> Dict:
        """ROI 시나리오 계산"""
        results = {}
        
        for year in years:
            future_value = purchase_price * ((1 + annual_growth) ** year)
            total_return = future_value - purchase_price
            annual_roi = ((future_value / purchase_price) ** (1/year) - 1) * 100
            
            results[f'year_{year}'] = {
                'future_value': future_value,
                'total_return': total_return,
                'annual_roi': annual_roi
            }
        
        return results
    
    def _create_price_trend_chart(self, monthly_stats: pd.DataFrame) -> Dict:
        """가격 트렌드 차트 생성"""
        fig = go.Figure()
        
        dates = [str(period) for period in monthly_stats.index]
        prices = monthly_stats[('price_per_sqm', 'mean')].values
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name='평균 단가',
            line=dict(color='blue', width=3)
        ))
        
        fig.update_layout(
            title='월별 가격 트렌드',
            xaxis_title='기간',
            yaxis_title='단가 (원/㎡)',
            hovermode='x unified'
        )
        
        return {
            'type': 'price_trend',
            'title': '월별 가격 트렌드',
            'figure': fig.to_json()
        }
    
    def _create_investment_radar_chart(self, investment_score: Dict) -> Dict:
        """투자 점수 레이더 차트"""
        categories = ['위치', '개발가능성', '시장상황', '유동성']
        values = [
            investment_score['location'],
            investment_score['development'],
            investment_score['market'],
            investment_score['liquidity']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='투자 점수'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title='투자 점수 분석'
        )
        
        return {
            'type': 'investment_radar',
            'title': '투자 점수 분석',
            'figure': fig.to_json()
        }
    
    def _generate_trend_insights(self, trend_data: Dict, monthly_stats: pd.DataFrame) -> List[str]:
        """트렌드 인사이트 생성"""
        insights = []
        
        if trend_data.get('trend_direction') == 'up':
            insights.append(f"📈 가격이 상승 추세입니다. (월평균 {trend_data.get('monthly_change_rate', 0):.1f}% 상승)")
        elif trend_data.get('trend_direction') == 'down':
            insights.append(f"📉 가격이 하락 추세입니다. (월평균 {abs(trend_data.get('monthly_change_rate', 0)):.1f}% 하락)")
        else:
            insights.append("📊 가격이 안정적인 상태입니다.")
        
        volatility = trend_data.get('volatility', 0)
        if volatility > 0.2:
            insights.append("⚠️ 가격 변동성이 높아 투자 시 주의가 필요합니다.")
        elif volatility < 0.1:
            insights.append("✅ 가격 변동성이 낮아 안정적인 투자처입니다.")
        
        return insights
    
    def _create_mock_trend_analysis(self) -> AnalyticsResult:
        """모의 트렌드 분석"""
        mock_data = {
            'trend_direction': 'up',
            'monthly_change_rate': 2.3,
            'volatility': 0.15,
            'current_price': 2800000
        }
        
        return AnalyticsResult(
            analysis_type="price_trends",
            data=mock_data,
            charts=[],
            insights=["📈 가격이 상승 추세입니다.", "✅ 안정적인 시장 상황입니다."],
            recommendations=["현재 시점이 투자하기 좋은 타이밍입니다."],
            created_at=datetime.now()
        )


class ReportGenerator:
    """리포트 생성기"""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_comprehensive_report(self, land_data: Dict, analysis_results: List[AnalyticsResult]) -> Dict:
        """종합 리포트 생성"""
        report = {
            'report_id': f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'land_info': land_data,
            'executive_summary': self._create_executive_summary(land_data, analysis_results),
            'detailed_analysis': {},
            'charts': [],
            'recommendations': [],
            'appendix': {}
        }
        
        # 분석 결과 통합
        for result in analysis_results:
            report['detailed_analysis'][result.analysis_type] = result.data
            report['charts'].extend(result.charts)
            report['recommendations'].extend(result.recommendations)
        
        # 종합 추천사항
        report['final_recommendation'] = self._create_final_recommendation(analysis_results)
        
        return report
    
    def generate_pdf_report(self, report_data: Dict) -> Optional[bytes]:
        """PDF 리포트 생성"""
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("ReportLab not available - cannot generate PDF")
            return None
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # 제목
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # 중앙 정렬
            )
            story.append(Paragraph("토지 투자 분석 리포트", title_style))
            story.append(Spacer(1, 20))
            
            # 기본 정보
            land_info = report_data.get('land_info', {})
            info_data = [
                ['항목', '내용'],
                ['주소', land_info.get('address', '')],
                ['지목', land_info.get('land_category', '')],
                ['면적', f"{land_info.get('area', 0):.1f}㎡"],
                ['용도지역', land_info.get('zone_type', '')],
                ['생성일시', report_data.get('generated_at', '')]
            ]
            
            info_table = Table(info_data)
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # 요약
            story.append(Paragraph("요약", styles['Heading2']))
            summary = report_data.get('executive_summary', {})
            for key, value in summary.items():
                story.append(Paragraph(f"• {key}: {value}", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # 추천사항
            story.append(Paragraph("추천사항", styles['Heading2']))
            recommendations = report_data.get('recommendations', [])
            for rec in recommendations[:5]:  # 상위 5개만
                story.append(Paragraph(f"• {rec}", styles['Normal']))
            
            # PDF 생성
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return None
    
    def _create_executive_summary(self, land_data: Dict, analysis_results: List[AnalyticsResult]) -> Dict:
        """경영진 요약 생성"""
        summary = {
            '토지_개요': f"{land_data.get('address', '')} - {land_data.get('area', 0):.1f}㎡",
            '투자_등급': 'B+',  # 분석 결과 기반으로 계산
            '예상_수익률': '연 5-8%',
            '주요_리스크': '시장 변동성',
            '투자_추천도': '보통'
        }
        
        # 분석 결과 기반 요약 업데이트
        for result in analysis_results:
            if result.analysis_type == 'investment_opportunity':
                investment_data = result.data.get('investment_score', {})
                overall_score = investment_data.get('overall', 70)
                
                if overall_score >= 80:
                    summary['투자_등급'] = 'A'
                    summary['투자_추천도'] = '강력추천'
                elif overall_score >= 70:
                    summary['투자_등급'] = 'B+'
                    summary['투자_추천도'] = '추천'
                else:
                    summary['투자_등급'] = 'B'
                    summary['투자_추천도'] = '보통'
        
        return summary
    
    def _create_final_recommendation(self, analysis_results: List[AnalyticsResult]) -> Dict:
        """최종 추천사항 생성"""
        recommendation = {
            'action': 'hold',  # buy, sell, hold
            'confidence': 'medium',  # high, medium, low
            'timeframe': '중장기',
            'key_factors': [],
            'next_steps': []
        }
        
        # 분석 결과 기반 추천사항 결정
        investment_scores = []
        for result in analysis_results:
            if result.analysis_type == 'investment_opportunity':
                score = result.data.get('investment_score', {}).get('overall', 70)
                investment_scores.append(score)
        
        if investment_scores:
            avg_score = sum(investment_scores) / len(investment_scores)
            
            if avg_score >= 80:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'high'
            elif avg_score >= 70:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'medium'
            elif avg_score >= 60:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = 'medium'
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = 'low'
        
        recommendation['key_factors'] = [
            '시장 트렌드 분석 결과',
            '투자 점수 종합 평가',
            '리스크 요인 검토'
        ]
        
        recommendation['next_steps'] = [
            '현장 실사 진행',
            '법무 검토 실시',
            '자금 조달 계획 수립'
        ]
        
        return recommendation