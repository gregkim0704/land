"""
보안 및 에러 처리 시스템
Security and Error Handling System
"""

import os
import hashlib
import secrets
import logging
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
import json
import re
from dataclasses import dataclass
import sqlite3

# 암호화 라이브러리
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# 입력 검증 라이브러리
try:
    import validators
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False


@dataclass
class SecurityEvent:
    """보안 이벤트"""
    event_type: str
    user_id: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict
    severity: str  # low, medium, high, critical


class SecurityManager:
    """보안 관리자"""
    
    def __init__(self, db_path: str = "security.db"):
        self.db_path = db_path
        self.setup_logging()
        self.init_security_database()
        self.load_security_config()
    
    def setup_logging(self):
        """보안 로깅 설정"""
        # 보안 전용 로거 설정
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.INFO)
        
        # 보안 로그 파일 핸들러
        security_handler = logging.FileHandler('security.log')
        security_handler.setLevel(logging.INFO)
        
        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(formatter)
        
        self.security_logger.addHandler(security_handler)
        
        # 일반 로거
        self.logger = logging.getLogger(__name__)
    
    def init_security_database(self):
        """보안 데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 보안 이벤트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                event_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                severity TEXT DEFAULT 'medium'
            )
        ''')
        
        # 실패한 로그인 시도 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failed_logins (
                attempt_id TEXT PRIMARY KEY,
                username TEXT,
                ip_address TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT
            )
        ''')
        
        # API 사용량 추적 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_usage (
                usage_id TEXT PRIMARY KEY,
                user_id TEXT,
                endpoint TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                response_time REAL
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_user ON security_events(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_failed_ip ON failed_logins(ip_address)')
        
        conn.commit()
        conn.close()
    
    def load_security_config(self):
        """보안 설정 로드"""
        self.config = {
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'session_timeout_hours': 24,
            'password_min_length': 8,
            'api_rate_limit_per_minute': 60,
            'max_file_size_mb': 10,
            'allowed_file_types': ['.pdf', '.txt', '.docx'],
            'sensitive_data_patterns': [
                r'\d{3}-\d{2}-\d{4}',  # SSN pattern
                r'\d{4}-\d{4}-\d{4}-\d{4}',  # Credit card pattern
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # Email pattern
            ]
        }
    
    def log_security_event(self, event_type: str, user_id: str = None, 
                          ip_address: str = None, details: Dict = None, 
                          severity: str = 'medium'):
        """보안 이벤트 로깅"""
        event_id = secrets.token_hex(16)
        
        # 데이터베이스에 저장
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events 
            (event_id, event_type, user_id, ip_address, details, severity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            event_id,
            event_type,
            user_id,
            ip_address,
            json.dumps(details or {}),
            severity
        ))
        
        conn.commit()
        conn.close()
        
        # 로그 파일에도 기록
        self.security_logger.info(
            f"Event: {event_type} | User: {user_id} | IP: {ip_address} | Severity: {severity}"
        )
        
        # 심각한 이벤트는 즉시 알림
        if severity in ['high', 'critical']:
            self._send_security_alert(event_type, user_id, details)
    
    def validate_input(self, data: Any, validation_type: str) -> tuple[bool, str]:
        """입력 데이터 검증"""
        try:
            if validation_type == 'email':
                if VALIDATORS_AVAILABLE:
                    return validators.email(data), "유효한 이메일 주소가 아닙니다."
                else:
                    # 간단한 이메일 검증
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    return bool(re.match(email_pattern, data)), "유효한 이메일 주소가 아닙니다."
            
            elif validation_type == 'password':
                if len(data) < self.config['password_min_length']:
                    return False, f"비밀번호는 최소 {self.config['password_min_length']}자 이상이어야 합니다."
                
                # 복잡성 검사
                if not re.search(r'[A-Za-z]', data):
                    return False, "비밀번호에 영문자가 포함되어야 합니다."
                if not re.search(r'\d', data):
                    return False, "비밀번호에 숫자가 포함되어야 합니다."
                
                return True, ""
            
            elif validation_type == 'address':
                # 주소 기본 검증
                if len(data) < 10:
                    return False, "주소가 너무 짧습니다."
                if len(data) > 200:
                    return False, "주소가 너무 깁니다."
                
                # 한글, 영문, 숫자, 기본 특수문자만 허용
                allowed_pattern = r'^[가-힣a-zA-Z0-9\s\-,.()]+$'
                if not re.match(allowed_pattern, data):
                    return False, "주소에 허용되지 않은 문자가 포함되어 있습니다."
                
                return True, ""
            
            elif validation_type == 'numeric':
                try:
                    float(data)
                    return True, ""
                except ValueError:
                    return False, "숫자만 입력 가능합니다."
            
            elif validation_type == 'phone':
                # 한국 전화번호 패턴
                phone_pattern = r'^01[0-9]-\d{3,4}-\d{4}$'
                return bool(re.match(phone_pattern, data)), "올바른 전화번호 형식이 아닙니다."
            
            return True, ""
            
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            return False, "입력 검증 중 오류가 발생했습니다."
    
    def sanitize_input(self, data: str) -> str:
        """입력 데이터 정화"""
        if not isinstance(data, str):
            return str(data)
        
        # HTML 태그 제거
        data = re.sub(r'<[^>]+>', '', data)
        
        # SQL 인젝션 방지를 위한 특수문자 이스케이프
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            data = data.replace(char, '')
        
        # 스크립트 태그 제거
        data = re.sub(r'<script.*?</script>', '', data, flags=re.IGNORECASE | re.DOTALL)
        
        # 길이 제한
        if len(data) > 1000:
            data = data[:1000]
        
        return data.strip()
    
    def check_rate_limit(self, user_id: str, endpoint: str = 'general') -> bool:
        """API 호출 제한 확인"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 최근 1분간 호출 횟수 확인
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        
        cursor.execute('''
            SELECT COUNT(*) FROM api_usage 
            WHERE user_id = ? AND endpoint = ? AND timestamp > ?
        ''', (user_id, endpoint, one_minute_ago))
        
        call_count = cursor.fetchone()[0]
        conn.close()
        
        if call_count >= self.config['api_rate_limit_per_minute']:
            self.log_security_event(
                'rate_limit_exceeded',
                user_id=user_id,
                details={'endpoint': endpoint, 'call_count': call_count},
                severity='medium'
            )
            return False
        
        return True
    
    def log_api_usage(self, user_id: str, endpoint: str, ip_address: str = None, 
                     response_time: float = None):
        """API 사용량 로깅"""
        usage_id = secrets.token_hex(16)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_usage (usage_id, user_id, endpoint, ip_address, response_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (usage_id, user_id, endpoint, ip_address, response_time))
        
        conn.commit()
        conn.close()
    
    def encrypt_sensitive_data(self, data: str, password: str = None) -> str:
        """민감한 데이터 암호화"""
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptography library not available - data not encrypted")
            return data
        
        try:
            if password is None:
                password = os.getenv('ENCRYPTION_PASSWORD', 'default-password-change-this')
            
            # 키 생성
            password_bytes = password.encode()
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            
            # 암호화
            f = Fernet(key)
            encrypted_data = f.encrypt(data.encode())
            
            # salt와 암호화된 데이터를 함께 저장
            return base64.urlsafe_b64encode(salt + encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return data
    
    def decrypt_sensitive_data(self, encrypted_data: str, password: str = None) -> str:
        """민감한 데이터 복호화"""
        if not CRYPTO_AVAILABLE:
            return encrypted_data
        
        try:
            if password is None:
                password = os.getenv('ENCRYPTION_PASSWORD', 'default-password-change-this')
            
            # 데이터 디코딩
            data_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            salt = data_bytes[:16]
            encrypted_content = data_bytes[16:]
            
            # 키 재생성
            password_bytes = password.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            
            # 복호화
            f = Fernet(key)
            decrypted_data = f.decrypt(encrypted_content)
            
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def scan_for_sensitive_data(self, text: str) -> List[str]:
        """민감한 데이터 패턴 스캔"""
        found_patterns = []
        
        for pattern in self.config['sensitive_data_patterns']:
            matches = re.findall(pattern, text)
            if matches:
                found_patterns.extend(matches)
        
        if found_patterns:
            self.log_security_event(
                'sensitive_data_detected',
                details={'patterns_found': len(found_patterns)},
                severity='high'
            )
        
        return found_patterns
    
    def _send_security_alert(self, event_type: str, user_id: str, details: Dict):
        """보안 알림 발송 (실제 구현 시 이메일/SMS 등)"""
        alert_message = f"""
        보안 알림: {event_type}
        사용자: {user_id}
        시간: {datetime.now()}
        세부사항: {details}
        """
        
        # 실제 구현 시 이메일/SMS/Slack 등으로 알림
        self.logger.critical(f"SECURITY ALERT: {alert_message}")


class ErrorHandler:
    """에러 처리 관리자"""
    
    def __init__(self):
        self.setup_logging()
        self.error_counts = {}
    
    def setup_logging(self):
        """에러 로깅 설정"""
        self.error_logger = logging.getLogger('errors')
        self.error_logger.setLevel(logging.ERROR)
        
        # 에러 로그 파일 핸들러
        error_handler = logging.FileHandler('errors.log')
        error_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - ERROR - %(name)s - %(levelname)s - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        self.error_logger.addHandler(error_handler)
    
    def handle_error(self, error: Exception, context: Dict = None, user_id: str = None) -> Dict:
        """에러 처리"""
        error_id = secrets.token_hex(8)
        error_type = type(error).__name__
        error_message = str(error)
        
        # 에러 카운트 증가
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # 상세 에러 정보
        error_info = {
            'error_id': error_id,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # 로깅
        self.error_logger.error(
            f"Error ID: {error_id} | Type: {error_type} | User: {user_id} | Message: {error_message}"
        )
        
        # 사용자 친화적 메시지 생성
        user_message = self._get_user_friendly_message(error_type, error_message)
        
        return {
            'error_id': error_id,
            'user_message': user_message,
            'technical_details': error_info if os.getenv('DEBUG') == 'True' else None
        }
    
    def _get_user_friendly_message(self, error_type: str, error_message: str) -> str:
        """사용자 친화적 에러 메시지 생성"""
        friendly_messages = {
            'ValidationError': '입력하신 정보를 다시 확인해주세요.',
            'ConnectionError': '네트워크 연결에 문제가 있습니다. 잠시 후 다시 시도해주세요.',
            'TimeoutError': '요청 처리 시간이 초과되었습니다. 다시 시도해주세요.',
            'FileNotFoundError': '요청하신 파일을 찾을 수 없습니다.',
            'PermissionError': '해당 작업을 수행할 권한이 없습니다.',
            'ValueError': '입력값이 올바르지 않습니다.',
            'KeyError': '필수 정보가 누락되었습니다.',
            'DatabaseError': '데이터베이스 처리 중 오류가 발생했습니다.',
            'APIError': 'API 호출 중 오류가 발생했습니다.'
        }
        
        return friendly_messages.get(error_type, '시스템 오류가 발생했습니다. 관리자에게 문의해주세요.')


def secure_endpoint(require_auth: bool = True, rate_limit: bool = True):
    """보안 엔드포인트 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            error_handler = ErrorHandler()
            
            try:
                # 인증 확인
                if require_auth:
                    # 실제 구현 시 세션/토큰 검증
                    pass
                
                # 속도 제한 확인
                if rate_limit:
                    user_id = kwargs.get('user_id', 'anonymous')
                    if not security_manager.check_rate_limit(user_id, func.__name__):
                        raise Exception("API 호출 제한을 초과했습니다.")
                
                # 함수 실행
                result = func(*args, **kwargs)
                
                # API 사용량 로깅
                security_manager.log_api_usage(
                    user_id=kwargs.get('user_id', 'anonymous'),
                    endpoint=func.__name__
                )
                
                return result
                
            except Exception as e:
                error_info = error_handler.handle_error(
                    e, 
                    context={'function': func.__name__, 'args': str(args)[:100]},
                    user_id=kwargs.get('user_id')
                )
                
                # 보안 이벤트 로깅
                security_manager.log_security_event(
                    'function_error',
                    user_id=kwargs.get('user_id'),
                    details={'function': func.__name__, 'error_id': error_info['error_id']},
                    severity='medium'
                )
                
                raise Exception(error_info['user_message'])
        
        return wrapper
    return decorator


def validate_and_sanitize(validation_rules: Dict):
    """입력 검증 및 정화 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            security_manager = SecurityManager()
            
            # 입력 검증 및 정화
            for param_name, rule in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    
                    # 검증
                    is_valid, error_message = security_manager.validate_input(value, rule)
                    if not is_valid:
                        raise ValueError(f"{param_name}: {error_message}")
                    
                    # 정화
                    if isinstance(value, str):
                        kwargs[param_name] = security_manager.sanitize_input(value)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator