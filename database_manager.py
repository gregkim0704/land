"""
데이터베이스 관리 시스템
Database Management System for Land AI
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass, asdict
import logging


@dataclass
class LandRecord:
    """토지 기록"""
    record_id: str
    user_id: str
    address: str
    land_category: str
    area: float
    official_price: float
    zone_type: str
    analysis_result: Dict
    created_at: datetime
    updated_at: datetime


@dataclass
class CustomerProfile:
    """고객 프로필"""
    profile_id: str
    user_id: str
    customer_name: str
    budget_min: float
    budget_max: float
    investment_purpose: str
    risk_tolerance: str
    preferred_zones: List[str]
    preferred_categories: List[str]
    created_at: datetime
    updated_at: datetime


class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self, db_path: str = "land_ai.db"):
        self.db_path = db_path
        self.init_database()
        self.setup_logging()
    
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('database.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 토지 분석 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS land_records (
                record_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                address TEXT NOT NULL,
                land_category TEXT,
                area REAL,
                official_price REAL,
                zone_type TEXT,
                analysis_result TEXT,  -- JSON 형태로 저장
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 고객 프로필 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_profiles (
                profile_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                budget_min REAL,
                budget_max REAL,
                investment_purpose TEXT,
                risk_tolerance TEXT,
                preferred_zones TEXT,  -- JSON 배열
                preferred_categories TEXT,  -- JSON 배열
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 채팅 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 계약서 분석 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contract_analyses (
                analysis_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                contract_text TEXT NOT NULL,
                analysis_result TEXT,  -- JSON 형태
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # 시장 데이터 테이블 (향후 확장용)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                data_id TEXT PRIMARY KEY,
                region TEXT,
                zone_type TEXT,
                avg_price REAL,
                transaction_count INTEGER,
                data_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_land_user ON land_records(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_customer_user ON customer_profiles(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id)')
        
        conn.commit()
        conn.close()
        self.logger.info("Database initialized successfully")
    
    def save_land_analysis(self, user_id: str, land_info: Dict, analysis_result: Dict) -> str:
        """토지 분석 결과 저장"""
        import hashlib
        
        record_id = hashlib.md5(f"{user_id}{land_info['address']}{datetime.now()}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO land_records 
                (record_id, user_id, address, land_category, area, official_price, zone_type, analysis_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_id,
                user_id,
                land_info['address'],
                land_info['land_category'],
                land_info['area'],
                land_info['official_price'],
                land_info['zone_type'],
                json.dumps(analysis_result, ensure_ascii=False)
            ))
            
            conn.commit()
            self.logger.info(f"Land analysis saved: {record_id}")
            return record_id
            
        except Exception as e:
            self.logger.error(f"Error saving land analysis: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_land_records(self, user_id: str, limit: int = 50) -> List[Dict]:
        """사용자의 토지 분석 기록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM land_records 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        records = []
        for row in results:
            record = {
                'record_id': row[0],
                'user_id': row[1],
                'address': row[2],
                'land_category': row[3],
                'area': row[4],
                'official_price': row[5],
                'zone_type': row[6],
                'analysis_result': json.loads(row[7]) if row[7] else {},
                'created_at': row[8],
                'updated_at': row[9]
            }
            records.append(record)
        
        return records
    
    def save_customer_profile(self, user_id: str, profile_data: Dict) -> str:
        """고객 프로필 저장"""
        import hashlib
        
        profile_id = hashlib.md5(f"{user_id}{profile_data['customer_name']}{datetime.now()}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO customer_profiles 
                (profile_id, user_id, customer_name, budget_min, budget_max, 
                 investment_purpose, risk_tolerance, preferred_zones, preferred_categories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile_id,
                user_id,
                profile_data['customer_name'],
                profile_data['budget_min'],
                profile_data['budget_max'],
                profile_data['investment_purpose'],
                profile_data['risk_tolerance'],
                json.dumps(profile_data['preferred_zones']),
                json.dumps(profile_data['preferred_categories'])
            ))
            
            conn.commit()
            self.logger.info(f"Customer profile saved: {profile_id}")
            return profile_id
            
        except Exception as e:
            self.logger.error(f"Error saving customer profile: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_customers(self, user_id: str) -> List[Dict]:
        """사용자의 고객 프로필 목록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM customer_profiles 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        profiles = []
        for row in results:
            profile = {
                'profile_id': row[0],
                'user_id': row[1],
                'customer_name': row[2],
                'budget_min': row[3],
                'budget_max': row[4],
                'investment_purpose': row[5],
                'risk_tolerance': row[6],
                'preferred_zones': json.loads(row[7]) if row[7] else [],
                'preferred_categories': json.loads(row[8]) if row[8] else [],
                'created_at': row[9],
                'updated_at': row[10]
            }
            profiles.append(profile)
        
        return profiles
    
    def save_chat_message(self, user_id: str, user_message: str, ai_response: str) -> str:
        """채팅 메시지 저장"""
        import hashlib
        
        chat_id = hashlib.md5(f"{user_id}{user_message}{datetime.now()}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_history (chat_id, user_id, user_message, ai_response)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, user_id, user_message, ai_response))
            
            conn.commit()
            return chat_id
            
        except Exception as e:
            self.logger.error(f"Error saving chat message: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_chat_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """사용자 채팅 기록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM chat_history 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        chats = []
        for row in results:
            chat = {
                'chat_id': row[0],
                'user_id': row[1],
                'user_message': row[2],
                'ai_response': row[3],
                'created_at': row[4]
            }
            chats.append(chat)
        
        return chats
    
    def get_analytics_data(self, user_id: str) -> Dict:
        """사용자 분석 통계 데이터"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 토지 분석 건수
        cursor.execute('SELECT COUNT(*) FROM land_records WHERE user_id = ?', (user_id,))
        land_count = cursor.fetchone()[0]
        
        # 고객 수
        cursor.execute('SELECT COUNT(*) FROM customer_profiles WHERE user_id = ?', (user_id,))
        customer_count = cursor.fetchone()[0]
        
        # 채팅 수
        cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ?', (user_id,))
        chat_count = cursor.fetchone()[0]
        
        # 최근 활동
        cursor.execute('''
            SELECT created_at FROM land_records 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        last_analysis = cursor.fetchone()
        
        conn.close()
        
        return {
            'land_analyses': land_count,
            'customers': customer_count,
            'chat_messages': chat_count,
            'last_activity': last_analysis[0] if last_analysis else None
        }
    
    def export_user_data(self, user_id: str) -> Dict:
        """사용자 데이터 내보내기"""
        return {
            'land_records': self.get_user_land_records(user_id),
            'customer_profiles': self.get_user_customers(user_id),
            'chat_history': self.get_user_chat_history(user_id),
            'analytics': self.get_analytics_data(user_id),
            'exported_at': datetime.now().isoformat()
        }
    
    def backup_database(self, backup_path: str):
        """데이터베이스 백업"""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise