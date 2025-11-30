#!/bin/bash

echo "========================================"
echo "토지전문 AI 시스템 - 상업용 버전 시작"
echo "========================================"

# 가상환경 활성화 (있는 경우)
if [ -f "venv/bin/activate" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# 환경변수 설정
echo "환경변수 설정 중..."
export PYTHONPATH=$(pwd)
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_PORT=8501

# 필요한 디렉토리 생성
mkdir -p logs data backups

# 의존성 확인 및 설치
echo "의존성 확인 중..."
pip install -r requirements.txt --quiet

# 데이터베이스 초기화 (첫 실행 시)
if [ ! -f "land_ai.db" ]; then
    echo "데이터베이스 초기화 중..."
    python -c "from database_manager import DatabaseManager; DatabaseManager()"
fi

# 보안 설정 확인
if [ ! -f ".env" ]; then
    echo ".env 파일이 없습니다. 환경변수를 설정해주세요."
    cat > .env.example << EOF
ANTHROPIC_API_KEY=your_api_key_here
JWT_SECRET_KEY=your_secret_key_here
ENCRYPTION_PASSWORD=your_encryption_password_here
KAKAO_API_KEY=your_kakao_api_key_here
MOLIT_API_KEY=your_molit_api_key_here
VWORLD_API_KEY=your_vworld_api_key_here
DATA_GO_KR_KEY=your_data_go_kr_key_here
EOF
    echo ".env.example 파일을 참고하여 .env 파일을 생성하세요."
fi

echo "========================================"
echo "상업용 토지 AI 시스템을 시작합니다..."
echo "브라우저에서 http://localhost:8501 을 열어주세요"
echo "========================================"

# Streamlit 앱 실행
streamlit run app_commercial.py