"""
외부 API 연동 시스템
External API Integration System
"""

import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import time
import logging
from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class RealEstateTransaction:
    """실거래 정보"""
    deal_amount: int
    deal_year: int
    deal_month: int
    deal_day: int
    area: float
    district: str
    dong: str
    land_category: str
    deal_type: str


class PublicAPIManager:
    """공공 API 관리자"""
    
    def __init__(self):
        self.setup_logging()
        self.load_api_keys()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LandAI/1.0 (Real Estate Analysis System)'
        })
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_api_keys(self):
        """API 키 로드"""
        self.molit_api_key = os.getenv('MOLIT_API_KEY', '')  # 국토교통부
        self.vworld_api_key = os.getenv('VWORLD_API_KEY', '')  # 브이월드
        self.data_go_kr_key = os.getenv('DATA_GO_KR_KEY', '')  # 공공데이터포털
    
    def get_real_estate_transactions(self, region_code: str, deal_ymd: str) -> List[RealEstateTransaction]:
        """
        국토교통부 실거래가 API 호출
        region_code: 지역코드 (예: 11110 - 종로구)
        deal_ymd: 거래년월 (예: 202410)
        """
        if not self.molit_api_key:
            self.logger.warning("MOLIT API key not found")
            return self._get_mock_transactions()
        
        url = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcLandTrade"
        
        params = {
            'serviceKey': self.molit_api_key,
            'LAWD_CD': region_code,
            'DEAL_YMD': deal_ymd,
            'numOfRows': 100,
            'pageNo': 1
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            transactions = []
            for item in items:
                transaction = RealEstateTransaction(
                    deal_amount=int(item.find('거래금액').text.replace(',', '').strip()),
                    deal_year=int(item.find('년').text),
                    deal_month=int(item.find('월').text),
                    deal_day=int(item.find('일').text),
                    area=float(item.find('거래면적').text),
                    district=item.find('시군구').text.strip(),
                    dong=item.find('법정동').text.strip(),
                    land_category=item.find('지목').text.strip(),
                    deal_type=item.find('거래유형').text.strip()
                )
                transactions.append(transaction)
            
            self.logger.info(f"Retrieved {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            self.logger.error(f"Error fetching real estate data: {e}")
            return self._get_mock_transactions()
    
    def get_land_use_plan(self, x: float, y: float) -> Dict:
        """
        토지이용계획 조회 (브이월드 API)
        x, y: 좌표 (WGS84)
        """
        if not self.vworld_api_key:
            self.logger.warning("VWorld API key not found")
            return self._get_mock_land_use_plan()
        
        url = "http://api.vworld.kr/req/data"
        
        params = {
            'service': 'data',
            'request': 'GetFeature',
            'data': 'LT_C_UQ111',  # 토지이용계획도
            'key': self.vworld_api_key,
            'geometry': f'POINT({x} {y})',
            'buffer': 100,
            'format': 'json',
            'size': 10
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('response', {}).get('status') == 'OK':
                features = data.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
                
                if features:
                    properties = features[0].get('properties', {})
                    return {
                        'zone_type': properties.get('UQ_NM', ''),  # 용도지역명
                        'zone_code': properties.get('UQ_CD', ''),  # 용도지역코드
                        'district_type': properties.get('UQ_GB', ''),  # 용도지구
                        'land_use_regulation': properties.get('UQ_REG', ''),  # 규제내용
                        'building_coverage_ratio': properties.get('BC_RAT', 0),  # 건폐율
                        'floor_area_ratio': properties.get('FA_RAT', 0)  # 용적률
                    }
            
            return self._get_mock_land_use_plan()
            
        except Exception as e:
            self.logger.error(f"Error fetching land use plan: {e}")
            return self._get_mock_land_use_plan()
    
    def get_official_land_price(self, pnu: str, year: str = None) -> Dict:
        """
        공시지가 조회
        pnu: 필지고유번호
        year: 조회년도 (기본값: 현재년도)
        """
        if year is None:
            year = str(datetime.now().year)
        
        # 실제 API 구현 시 공시지가 API 호출
        # 현재는 모의 데이터 반환
        return self._get_mock_official_price()
    
    def get_development_plans(self, region_code: str) -> List[Dict]:
        """
        개발계획 정보 조회
        region_code: 지역코드
        """
        # 실제 구현 시 국토교통부 개발계획 API 호출
        return self._get_mock_development_plans()
    
    def _get_mock_transactions(self) -> List[RealEstateTransaction]:
        """모의 실거래 데이터"""
        return [
            RealEstateTransaction(
                deal_amount=150000,
                deal_year=2024,
                deal_month=10,
                deal_day=15,
                area=500.0,
                district="분당구",
                dong="정자동",
                land_category="대지",
                deal_type="매매"
            ),
            RealEstateTransaction(
                deal_amount=280000,
                deal_year=2024,
                deal_month=9,
                deal_day=22,
                area=800.0,
                district="분당구",
                dong="정자동",
                land_category="대지",
                deal_type="매매"
            )
        ]
    
    def _get_mock_land_use_plan(self) -> Dict:
        """모의 토지이용계획 데이터"""
        return {
            'zone_type': '제2종일반주거지역',
            'zone_code': 'UQA220',
            'district_type': '일반',
            'land_use_regulation': '건폐율 60% 이하, 용적률 250% 이하',
            'building_coverage_ratio': 60,
            'floor_area_ratio': 250
        }
    
    def _get_mock_official_price(self) -> Dict:
        """모의 공시지가 데이터"""
        return {
            'official_price': 3000000,
            'price_year': 2024,
            'price_date': '2024-01-01',
            'land_category': '대지',
            'zone_type': '제2종일반주거지역'
        }
    
    def _get_mock_development_plans(self) -> List[Dict]:
        """모의 개발계획 데이터"""
        return [
            {
                'plan_name': 'GTX-A 노선 연장',
                'plan_type': '교통',
                'start_date': '2024-01-01',
                'end_date': '2026-12-31',
                'status': '진행중',
                'impact_radius_km': 2.0
            },
            {
                'plan_name': '판교 테크노밸리 확장',
                'plan_type': '산업단지',
                'start_date': '2025-03-01',
                'end_date': '2028-12-31',
                'status': '계획',
                'impact_radius_km': 3.0
            }
        ]


class MarketDataAnalyzer:
    """시장 데이터 분석기"""
    
    def __init__(self, api_manager: PublicAPIManager):
        self.api_manager = api_manager
        self.logger = logging.getLogger(__name__)
    
    def analyze_market_trend(self, region_code: str, months: int = 12) -> Dict:
        """시장 트렌드 분석"""
        transactions_by_month = {}
        
        # 최근 N개월 데이터 수집
        for i in range(months):
            date = datetime.now() - timedelta(days=30 * i)
            deal_ymd = date.strftime('%Y%m')
            
            transactions = self.api_manager.get_real_estate_transactions(region_code, deal_ymd)
            transactions_by_month[deal_ymd] = transactions
            
            # API 호출 제한 고려
            time.sleep(0.1)
        
        # 트렌드 분석
        monthly_stats = {}
        for month, transactions in transactions_by_month.items():
            if transactions:
                prices = [t.deal_amount for t in transactions]
                areas = [t.area for t in transactions]
                
                monthly_stats[month] = {
                    'transaction_count': len(transactions),
                    'avg_price': sum(prices) / len(prices),
                    'avg_area': sum(areas) / len(areas),
                    'total_volume': sum(prices)
                }
        
        return {
            'region_code': region_code,
            'analysis_period': f"{months}개월",
            'monthly_stats': monthly_stats,
            'trend_analysis': self._calculate_trend(monthly_stats),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_trend(self, monthly_stats: Dict) -> Dict:
        """트렌드 계산"""
        if len(monthly_stats) < 2:
            return {'trend': 'insufficient_data'}
        
        months = sorted(monthly_stats.keys())
        recent_month = monthly_stats[months[-1]]
        previous_month = monthly_stats[months[-2]]
        
        price_change = ((recent_month['avg_price'] - previous_month['avg_price']) / 
                       previous_month['avg_price'] * 100)
        
        volume_change = ((recent_month['transaction_count'] - previous_month['transaction_count']) / 
                        previous_month['transaction_count'] * 100)
        
        return {
            'price_change_percent': round(price_change, 2),
            'volume_change_percent': round(volume_change, 2),
            'trend_direction': 'up' if price_change > 0 else 'down' if price_change < 0 else 'stable'
        }


class GeocodeService:
    """주소-좌표 변환 서비스"""
    
    def __init__(self):
        self.kakao_api_key = os.getenv('KAKAO_API_KEY', '')
        self.session = requests.Session()
    
    def address_to_coordinates(self, address: str) -> Optional[Dict]:
        """주소를 좌표로 변환"""
        if not self.kakao_api_key:
            # 모의 좌표 반환
            return {'x': 127.1058342, 'y': 37.3595316}  # 분당구 정자동
        
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {'Authorization': f'KakaoAK {self.kakao_api_key}'}
        params = {'query': address}
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            documents = data.get('documents', [])
            
            if documents:
                return {
                    'x': float(documents[0]['x']),
                    'y': float(documents[0]['y']),
                    'address_name': documents[0]['address_name']
                }
            
            return None
            
        except Exception as e:
            logging.error(f"Geocoding error: {e}")
            return None