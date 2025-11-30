"""
사용자 인증 및 권한 관리 시스템
User Authentication and Authorization System
"""

import streamlit as st
import hashlib
import sqlite3
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import os
from dataclasses import dataclass


@dataclass
class User:
    """사용자 정보"""
    user_id: str
    username: str
    email: str
    user_type: str  # 'admin', 'premium', 'basic'
    company: str
    created_at: datetime
    last_login: datetime
    is_active: bool


class AuthManager:
    """인증 관리자"""
    
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                user_type TEXT DEFAULT 'basic',
                company TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                subscription_end DATE,
                api_calls_used INTEGER DEFAULT 0,
                api_calls_limit INTEGER DEFAULT 100
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, 
                   user_type: str = 'basic', company: str = '') -> bool:
        """사용자 생성"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            user_id = hashlib.md5(f"{username}{email}".encode()).hexdigest()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, user_type, company)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, user_type, company))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """사용자 인증"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT * FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return User(
                user_id=result[0],
                username=result[1],
                email=result[2],
                user_type=result[4],
                company=result[5] or '',
                created_at=datetime.fromisoformat(result[6]),
                last_login=datetime.fromisoformat(result[7]) if result[7] else None,
                is_active=bool(result[8])
            )
        return None
    
    def create_session(self, user_id: str) -> str:
        """세션 생성"""
        session_id = hashlib.md5(f"{user_id}{datetime.now()}".encode()).hexdigest()
        expires_at = datetime.now() + timedelta(hours=24)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_sessions (session_id, user_id, expires_at)
            VALUES (?, ?, ?)
        ''', (session_id, user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[str]:
        """세션 검증"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id FROM user_sessions 
            WHERE session_id = ? AND expires_at > ? AND is_active = 1
        ''', (session_id, datetime.now()))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def check_api_limit(self, user_id: str) -> bool:
        """API 호출 제한 확인"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT api_calls_used, api_calls_limit FROM users WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            used, limit = result
            return used < limit
        return False
    
    def increment_api_usage(self, user_id: str):
        """API 사용량 증가"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users SET api_calls_used = api_calls_used + 1 WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()


def require_auth(func):
    """인증 데코레이터"""
    def wrapper(*args, **kwargs):
        if 'user' not in st.session_state:
            st.error("로그인이 필요합니다.")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def login_form():
    """로그인 폼"""
    st.title("🔐 로그인")
    
    with st.form("login_form"):
        username = st.text_input("사용자명")
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("로그인")
        
        if submitted:
            auth_manager = AuthManager()
            user = auth_manager.authenticate_user(username, password)
            
            if user:
                session_id = auth_manager.create_session(user.user_id)
                st.session_state.user = user
                st.session_state.session_id = session_id
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("잘못된 사용자명 또는 비밀번호입니다.")


def register_form():
    """회원가입 폼"""
    st.title("📝 회원가입")
    
    with st.form("register_form"):
        username = st.text_input("사용자명")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        password_confirm = st.text_input("비밀번호 확인", type="password")
        company = st.text_input("회사명 (선택)")
        
        submitted = st.form_submit_button("가입하기")
        
        if submitted:
            if password != password_confirm:
                st.error("비밀번호가 일치하지 않습니다.")
            elif len(password) < 6:
                st.error("비밀번호는 6자 이상이어야 합니다.")
            else:
                auth_manager = AuthManager()
                if auth_manager.create_user(username, email, password, company=company):
                    st.success("회원가입이 완료되었습니다! 로그인해주세요.")
                else:
                    st.error("이미 존재하는 사용자명 또는 이메일입니다.")


def show_user_info():
    """사용자 정보 표시"""
    if 'user' in st.session_state:
        user = st.session_state.user
        st.sidebar.markdown(f"👤 **{user.username}**")
        st.sidebar.markdown(f"📧 {user.email}")
        st.sidebar.markdown(f"🏢 {user.company}")
        st.sidebar.markdown(f"⭐ {user.user_type.upper()}")
        
        if st.sidebar.button("로그아웃"):
            del st.session_state.user
            del st.session_state.session_id
            st.rerun()