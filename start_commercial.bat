@echo off
echo ========================================
echo 토지전문 AI 시스템 - 상업용 버전 시작
echo ========================================

REM 가상환경 활성화 (있는 경우)
if exist "venv\Scripts\activate.bat" (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
)

REM 환경변수 설정
echo 환경변수 설정 중...
set PYTHONPATH=%CD%
set STREAMLIT_SERVER_HEADLESS=true
set STREAMLIT_SERVER_PORT=8501

REM 필요한 디렉토리 생성
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "backups" mkdir backups

REM 의존성 확인 및 설치
echo 의존성 확인 중...
pip install -r requirements.txt --quiet

REM 데이터베이스 초기화 (첫 실행 시)
if not exist "land_ai.db" (
    echo 데이터베이스 초기화 중...
    python -c "from database_manager import DatabaseManager; DatabaseManager()"
)

REM 보안 설정 확인
if not exist ".env" (
    echo .env 파일이 없습니다. 환경변수를 설정해주세요.
    echo ANTHROPIC_API_KEY=your_api_key_here > .env.example
    echo JWT_SECRET_KEY=your_secret_key_here >> .env.example
    echo ENCRYPTION_PASSWORD=your_encryption_password_here >> .env.example
    echo .env.example 파일을 참고하여 .env 파일을 생성하세요.
)

echo ========================================
echo 상업용 토지 AI 시스템을 시작합니다...
echo 브라우저에서 http://localhost:8501 을 열어주세요
echo ========================================

REM Streamlit 앱 실행
streamlit run app_commercial.py

pause