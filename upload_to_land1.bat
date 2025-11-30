@echo off
echo ========================================
echo Land1 저장소로 업로드
echo ========================================
echo.

echo ⚠️ 먼저 GitHub에서 land1 저장소를 생성해야 합니다!
echo    https://github.com/new
echo.
echo Repository name: land1
echo Description: 토지전문 AI 시스템 v2.0 - Gemini API 통합
echo.

pause

echo.
echo 🚀 업로드 시작...
echo.

REM 원격 저장소 추가 (이미 있으면 무시)
git remote add land1 https://github.com/gregkim0704/land1.git 2>nul

REM 푸시
echo 📤 코드를 land1 저장소로 푸시 중...
git push land1 main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 업로드 완료!
    echo ========================================
    echo.
    echo 저장소 URL:
    echo https://github.com/gregkim0704/land1
    echo.
) else (
    echo.
    echo ========================================
    echo ❌ 업로드 실패
    echo ========================================
    echo.
    echo 다음을 확인하세요:
    echo 1. GitHub에서 land1 저장소가 생성되었는지
    echo 2. 저장소 이름이 정확한지
    echo 3. 인터넷 연결 상태
    echo.
)

pause
