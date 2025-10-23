#!/bin/bash

echo "===================================="
echo "토지 AI 시스템 시작"
echo "===================================="
echo ""

# 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "가상환경 활성화 중..."
    source venv/bin/activate
fi

# Streamlit 앱 실행
echo "Streamlit 서버 시작 중..."
echo "브라우저에서 http://localhost:8501 로 접속하세요"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

streamlit run app.py
