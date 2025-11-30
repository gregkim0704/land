"""
인증 시스템 테스트
"""

import pytest
import tempfile
import os
from auth_system import AuthManager, User


class TestAuthManager:
    """인증 관리자 테스트"""
    
    @pytest.fixture
    def auth_manager(self):
        """테스트용 인증 관리자"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name
        
        manager = AuthManager(db_path)
        yield manager
        
        # 정리
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_user(self, auth_manager):
        """사용자 생성 테스트"""
        result = auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            user_type="basic"
        )
        assert result is True
    
    def test_duplicate_user(self, auth_manager):
        """중복 사용자 생성 테스트"""
        # 첫 번째 사용자 생성
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # 같은 사용자명으로 다시 생성 시도
        result = auth_manager.create_user(
            username="testuser",
            email="test2@example.com",
            password="testpass456"
        )
        assert result is False
    
    def test_authenticate_user(self, auth_manager):
        """사용자 인증 테스트"""
        # 사용자 생성
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # 올바른 인증
        user = auth_manager.authenticate_user("testuser", "testpass123")
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        
        # 잘못된 비밀번호
        user = auth_manager.authenticate_user("testuser", "wrongpass")
        assert user is None
    
    def test_session_management(self, auth_manager):
        """세션 관리 테스트"""
        # 사용자 생성
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        user = auth_manager.authenticate_user("testuser", "testpass123")
        
        # 세션 생성
        session_id = auth_manager.create_session(user.user_id)
        assert session_id is not None
        
        # 세션 검증
        validated_user_id = auth_manager.validate_session(session_id)
        assert validated_user_id == user.user_id
    
    def test_api_limit(self, auth_manager):
        """API 제한 테스트"""
        # 사용자 생성
        auth_manager.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        user = auth_manager.authenticate_user("testuser", "testpass123")
        
        # 초기에는 API 호출 가능
        assert auth_manager.check_api_limit(user.user_id) is True
        
        # API 사용량 증가
        for _ in range(100):  # 기본 제한이 100
            auth_manager.increment_api_usage(user.user_id)
        
        # 제한 초과 후에는 호출 불가
        assert auth_manager.check_api_limit(user.user_id) is False