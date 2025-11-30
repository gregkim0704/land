"""
파일 업로드 및 데이터 파싱 핸들러
File Upload and Data Parsing Handler
"""

import pandas as pd
import json
import io
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass


@dataclass
class LandDataFromFile:
    """파일에서 읽은 토지 데이터"""
    address: str
    land_category: str
    area: float
    official_price: float
    zone_type: str
    district: str = "일반"
    road_contact: bool = True
    nearest_station_km: float = 1.0
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'address': self.address,
            'land_category': self.land_category,
            'area': self.area,
            'official_price': self.official_price,
            'zone_type': self.zone_type,
            'district': self.district,
            'road_contact': self.road_contact,
            'nearest_station_km': self.nearest_station_km
        }


class FileUploadHandler:
    """파일 업로드 핸들러"""
    
    def __init__(self):
        self.setup_logging()
        
        # 필수 컬럼 매핑 (다양한 표현 지원)
        self.column_mapping = {
            'address': ['주소', 'address', '소재지', '위치', 'location'],
            'land_category': ['지목', 'land_category', '토지종류', 'category', '용도'],
            'area': ['면적', 'area', '토지면적', '평수', 'size'],
            'official_price': ['공시지가', 'official_price', '가격', 'price', '단가'],
            'zone_type': ['용도지역', 'zone_type', 'zone', '지역', 'zoning'],
            'district': ['용도지구', 'district', '지구'],
            'road_contact': ['도로접함', 'road_contact', '접도', 'road'],
            'nearest_station_km': ['역거리', 'nearest_station_km', 'station_distance', '역까지거리']
        }
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def parse_excel(self, file_content: bytes) -> List[LandDataFromFile]:
        """
        Excel 파일 파싱
        
        Args:
            file_content: 업로드된 파일 내용
            
        Returns:
            토지 데이터 리스트
        """
        try:
            # Excel 파일 읽기
            df = pd.read_excel(io.BytesIO(file_content))
            return self._parse_dataframe(df)
        except Exception as e:
            self.logger.error(f"Excel 파싱 오류: {e}")
            raise ValueError(f"Excel 파일을 읽을 수 없습니다: {e}")
    
    def parse_csv(self, file_content: bytes, encoding: str = 'utf-8') -> List[LandDataFromFile]:
        """
        CSV 파일 파싱
        
        Args:
            file_content: 업로드된 파일 내용
            encoding: 파일 인코딩 (기본: utf-8, 한글: cp949)
            
        Returns:
            토지 데이터 리스트
        """
        try:
            # CSV 파일 읽기
            df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
            return self._parse_dataframe(df)
        except UnicodeDecodeError:
            # UTF-8 실패 시 CP949(한글) 시도
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding='cp949')
                return self._parse_dataframe(df)
            except Exception as e:
                self.logger.error(f"CSV 파싱 오류: {e}")
                raise ValueError(f"CSV 파일을 읽을 수 없습니다: {e}")
        except Exception as e:
            self.logger.error(f"CSV 파싱 오류: {e}")
            raise ValueError(f"CSV 파일을 읽을 수 없습니다: {e}")
    
    def parse_json(self, file_content: bytes) -> List[LandDataFromFile]:
        """
        JSON 파일 파싱
        
        Args:
            file_content: 업로드된 파일 내용
            
        Returns:
            토지 데이터 리스트
        """
        try:
            # JSON 파일 읽기
            data = json.loads(file_content.decode('utf-8'))
            
            # 리스트 형태인지 확인
            if isinstance(data, list):
                return [self._parse_json_item(item) for item in data]
            elif isinstance(data, dict):
                return [self._parse_json_item(data)]
            else:
                raise ValueError("JSON 형식이 올바르지 않습니다.")
                
        except Exception as e:
            self.logger.error(f"JSON 파싱 오류: {e}")
            raise ValueError(f"JSON 파일을 읽을 수 없습니다: {e}")
    
    def _parse_dataframe(self, df: pd.DataFrame) -> List[LandDataFromFile]:
        """
        DataFrame을 토지 데이터로 변환
        
        Args:
            df: pandas DataFrame
            
        Returns:
            토지 데이터 리스트
        """
        # 컬럼명 정규화
        normalized_df = self._normalize_columns(df)
        
        # 필수 컬럼 확인
        required_columns = ['address', 'land_category', 'area', 'official_price', 'zone_type']
        missing_columns = [col for col in required_columns if col not in normalized_df.columns]
        
        if missing_columns:
            raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")
        
        # 각 행을 토지 데이터로 변환
        land_data_list = []
        for idx, row in normalized_df.iterrows():
            try:
                land_data = LandDataFromFile(
                    address=str(row['address']),
                    land_category=str(row['land_category']),
                    area=float(row['area']),
                    official_price=float(row['official_price']),
                    zone_type=str(row['zone_type']),
                    district=str(row.get('district', '일반')),
                    road_contact=self._parse_boolean(row.get('road_contact', True)),
                    nearest_station_km=float(row.get('nearest_station_km', 1.0))
                )
                land_data_list.append(land_data)
            except Exception as e:
                self.logger.warning(f"행 {idx+1} 파싱 실패: {e}")
                continue
        
        if not land_data_list:
            raise ValueError("유효한 토지 데이터가 없습니다.")
        
        return land_data_list
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        컬럼명을 표준 형식으로 정규화
        
        Args:
            df: 원본 DataFrame
            
        Returns:
            정규화된 DataFrame
        """
        normalized_df = df.copy()
        column_rename_map = {}
        
        # 각 컬럼을 표준 이름으로 매핑
        for standard_name, possible_names in self.column_mapping.items():
            for col in df.columns:
                if col in possible_names or col.lower() in [n.lower() for n in possible_names]:
                    column_rename_map[col] = standard_name
                    break
        
        normalized_df = normalized_df.rename(columns=column_rename_map)
        return normalized_df
    
    def _parse_json_item(self, item: Dict) -> LandDataFromFile:
        """
        JSON 항목을 토지 데이터로 변환
        
        Args:
            item: JSON 객체
            
        Returns:
            토지 데이터
        """
        # 키 정규화
        normalized_item = {}
        for standard_name, possible_names in self.column_mapping.items():
            for key in item.keys():
                if key in possible_names or key.lower() in [n.lower() for n in possible_names]:
                    normalized_item[standard_name] = item[key]
                    break
        
        return LandDataFromFile(
            address=str(normalized_item.get('address', '')),
            land_category=str(normalized_item.get('land_category', '')),
            area=float(normalized_item.get('area', 0)),
            official_price=float(normalized_item.get('official_price', 0)),
            zone_type=str(normalized_item.get('zone_type', '')),
            district=str(normalized_item.get('district', '일반')),
            road_contact=self._parse_boolean(normalized_item.get('road_contact', True)),
            nearest_station_km=float(normalized_item.get('nearest_station_km', 1.0))
        )
    
    def _parse_boolean(self, value: Any) -> bool:
        """
        다양한 형식의 불린 값 파싱
        
        Args:
            value: 파싱할 값
            
        Returns:
            불린 값
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['true', 'yes', 'y', '예', 'o', '○', '✓', '1']:
                return True
            elif value_lower in ['false', 'no', 'n', '아니오', 'x', '✗', '0']:
                return False
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        return True  # 기본값
    
    def create_template_excel(self) -> bytes:
        """
        Excel 템플릿 파일 생성
        
        Returns:
            Excel 파일 바이트
        """
        # 템플릿 데이터
        template_data = {
            '주소': ['경기도 성남시 분당구 정자동 123-45', '서울시 강남구 역삼동 456-78'],
            '지목': ['대지', '전'],
            '면적': [500.0, 800.0],
            '공시지가': [3000000, 2500000],
            '용도지역': ['제2종일반주거지역', '자연녹지지역'],
            '용도지구': ['일반', '일반'],
            '도로접함': ['예', '아니오'],
            '역거리': [0.8, 2.5]
        }
        
        df = pd.DataFrame(template_data)
        
        # Excel 파일로 변환
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='토지정보')
        
        output.seek(0)
        return output.getvalue()
    
    def create_template_csv(self) -> str:
        """
        CSV 템플릿 파일 생성
        
        Returns:
            CSV 문자열
        """
        template_data = {
            '주소': ['경기도 성남시 분당구 정자동 123-45', '서울시 강남구 역삼동 456-78'],
            '지목': ['대지', '전'],
            '면적': [500.0, 800.0],
            '공시지가': [3000000, 2500000],
            '용도지역': ['제2종일반주거지역', '자연녹지지역'],
            '용도지구': ['일반', '일반'],
            '도로접함': ['예', '아니오'],
            '역거리': [0.8, 2.5]
        }
        
        df = pd.DataFrame(template_data)
        return df.to_csv(index=False, encoding='utf-8-sig')
    
    def create_template_json(self) -> str:
        """
        JSON 템플릿 파일 생성
        
        Returns:
            JSON 문자열
        """
        template_data = [
            {
                "주소": "경기도 성남시 분당구 정자동 123-45",
                "지목": "대지",
                "면적": 500.0,
                "공시지가": 3000000,
                "용도지역": "제2종일반주거지역",
                "용도지구": "일반",
                "도로접함": "예",
                "역거리": 0.8
            },
            {
                "주소": "서울시 강남구 역삼동 456-78",
                "지목": "전",
                "면적": 800.0,
                "공시지가": 2500000,
                "용도지역": "자연녹지지역",
                "용도지구": "일반",
                "도로접함": "아니오",
                "역거리": 2.5
            }
        ]
        
        return json.dumps(template_data, ensure_ascii=False, indent=2)
    
    def validate_land_data(self, land_data: LandDataFromFile) -> tuple[bool, str]:
        """
        토지 데이터 유효성 검증
        
        Args:
            land_data: 검증할 토지 데이터
            
        Returns:
            (유효 여부, 오류 메시지)
        """
        # 주소 검증
        if not land_data.address or len(land_data.address) < 5:
            return False, "주소가 너무 짧거나 비어있습니다."
        
        # 면적 검증
        if land_data.area <= 0:
            return False, "면적은 0보다 커야 합니다."
        
        if land_data.area > 1000000:  # 100만㎡ 이상
            return False, "면적이 너무 큽니다. 확인해주세요."
        
        # 공시지가 검증
        if land_data.official_price <= 0:
            return False, "공시지가는 0보다 커야 합니다."
        
        if land_data.official_price > 100000000:  # 1억원/㎡ 이상
            return False, "공시지가가 너무 높습니다. 확인해주세요."
        
        # 지목 검증
        valid_categories = ['대지', '전', '답', '과수원', '임야', '목장용지', '공장용지', '학교용지', '주차장', '주유소용지']
        if land_data.land_category not in valid_categories:
            return False, f"지목이 올바르지 않습니다. 가능한 값: {', '.join(valid_categories)}"
        
        # 용도지역 검증
        valid_zones = [
            '제1종전용주거지역', '제2종전용주거지역',
            '제1종일반주거지역', '제2종일반주거지역', '제3종일반주거지역',
            '준주거지역', '중심상업지역', '일반상업지역', '근린상업지역',
            '일반공업지역', '준공업지역',
            '자연녹지지역', '생산녹지지역', '보전녹지지역'
        ]
        if land_data.zone_type not in valid_zones:
            return False, f"용도지역이 올바르지 않습니다."
        
        return True, ""
