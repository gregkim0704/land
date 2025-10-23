# 🚀 GitHub 저장소 업로드 가이드

## 📂 저장소 정보
- **GitHub URL**: https://github.com/gregkim0704/land
- **저장소명**: land
- **소유자**: gregkim0704

---

## 🎯 빠른 업로드 (3단계)

### 방법 1: 명령줄 사용 (추천)

#### 1단계: 로컬에 Git 저장소 초기화
```bash
# 프로젝트 폴더로 이동
cd /path/to/land_ai_system

# Git 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: 토지전문 부동산 AI 시스템 v1.0.0"
```

#### 2단계: GitHub 저장소 연결
```bash
# 원격 저장소 추가
git remote add origin https://github.com/gregkim0704/land.git

# 브랜치 이름 main으로 설정
git branch -M main
```

#### 3단계: Push
```bash
# GitHub에 업로드
git push -u origin main
```

---

### 방법 2: GitHub Desktop 사용 (초보자)

1. **GitHub Desktop** 설치 (https://desktop.github.com/)
2. **File → Add Local Repository** 선택
3. 프로젝트 폴더 선택
4. **Publish repository** 클릭
5. 저장소 이름: `land` 입력
6. **Publish repository** 버튼 클릭

---

### 방법 3: GitHub 웹사이트에서 직접 업로드

1. https://github.com/gregkim0704/land 접속
2. **Add file → Upload files** 클릭
3. 모든 파일 드래그 앤 드롭
4. Commit message 입력: "Initial commit: 토지 AI 시스템 v1.0.0"
5. **Commit changes** 클릭

---

## 📋 업로드 전 체크리스트

### ✅ 필수 확인사항
- [ ] 모든 파일이 같은 폴더에 있는지 확인
- [ ] .gitignore 파일 포함 확인
- [ ] LICENSE 파일 포함 확인
- [ ] API 키나 비밀번호 없는지 확인
- [ ] requirements.txt 최신 버전 확인

### 📁 업로드할 파일 목록 (총 11개)
```
✅ app.py                    # 웹 애플리케이션
✅ land_ai_core.py           # 분석 엔진
✅ land_ai_chatbot.py        # AI 챗봇
✅ requirements.txt          # 의존성
✅ README.md                 # 프로젝트 설명
✅ QUICKSTART.md             # 빠른 시작
✅ DELIVERY_REPORT.md        # 개발 보고서
✅ land_ai_system_plan.md    # 개발 계획
✅ start.bat                 # Windows 실행
✅ start.sh                  # Unix 실행
✅ .gitignore                # Git 제외 파일
✅ LICENSE                   # 라이선스
```

---

## 🔐 보안 주의사항

### ⚠️ 절대 업로드 금지
```bash
# 다음 파일들은 절대 GitHub에 올리지 마세요!
- API 키 (.env 파일)
- 비밀번호
- 고객 개인정보
- 데이터베이스 파일
- 대용량 데이터 파일 (>100MB)
```

### ✅ 안전한 API 키 관리
```python
# .env 파일 사용 (Git에는 올리지 않음)
ANTHROPIC_API_KEY=your_key_here

# 코드에서 사용
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')
```

---

## 📝 커밋 메시지 가이드

### 좋은 커밋 메시지 예시
```bash
✅ git commit -m "Initial commit: 토지 AI 시스템 v1.0.0"
✅ git commit -m "Add: 토지 가격 예측 기능 추가"
✅ git commit -m "Fix: 챗봇 응답 오류 수정"
✅ git commit -m "Update: requirements.txt 의존성 업데이트"
✅ git commit -m "Docs: README 사용법 보완"
```

### 커밋 유형
- `Add`: 새 기능 추가
- `Fix`: 버그 수정
- `Update`: 기존 기능 개선
- `Docs`: 문서 수정
- `Refactor`: 코드 리팩토링
- `Test`: 테스트 추가
- `Style`: 코드 포맷팅

---

## 🌿 브랜치 전략 (향후 개발용)

### 기본 브랜치 구조
```
main (또는 master)  → 프로덕션 코드
  ↑
develop              → 개발 브랜치
  ↑
feature/기능명       → 새 기능 개발
```

### 브랜치 생성 예시
```bash
# 개발 브랜치 생성
git checkout -b develop

# 기능 브랜치 생성
git checkout -b feature/price-prediction

# 작업 후 커밋
git add .
git commit -m "Add: 머신러닝 가격 예측 모델"

# develop에 병합
git checkout develop
git merge feature/price-prediction

# main에 병합 (릴리스 시)
git checkout main
git merge develop
```

---

## 🔄 정기 업데이트 방법

### 코드 수정 후 업로드
```bash
# 1. 변경 사항 확인
git status

# 2. 변경된 파일 추가
git add .

# 3. 커밋
git commit -m "Update: 기능 개선"

# 4. Push
git push origin main
```

### 원격 저장소와 동기화
```bash
# 원격 변경사항 가져오기
git pull origin main

# 충돌 해결 후
git push origin main
```

---

## 📊 GitHub 저장소 설정 추천

### 1. About 섹션 설정
```
Description: 🏞️ AI 기반 토지 투자 분석 및 컨설팅 시스템
Website: (있다면 추가)
Topics: real-estate, ai, python, streamlit, land-analysis
```

### 2. README 배지 추가
```markdown
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
```

### 3. GitHub Pages 활성화 (선택)
- Settings → Pages
- Source: main branch / docs 폴더
- 문서 호스팅 가능

---

## 🐛 문제 해결

### Q1: "remote: Repository not found" 오류
```bash
# 해결: 저장소 URL 확인
git remote -v
git remote set-url origin https://github.com/gregkim0704/land.git
```

### Q2: "failed to push some refs" 오류
```bash
# 해결: Pull 먼저 실행
git pull origin main --rebase
git push origin main
```

### Q3: 인증 오류 (Username/Password)
```bash
# GitHub Personal Access Token 사용
# Settings → Developer settings → Personal access tokens
# 토큰 생성 후 비밀번호 대신 사용
```

### Q4: 파일이 너무 큰 경우 (>100MB)
```bash
# Git LFS 사용
git lfs install
git lfs track "*.csv"
git add .gitattributes
git commit -m "Add: Git LFS 설정"
```

---

## 📱 모바일에서 관리

### GitHub Mobile 앱
- iOS/Android에서 저장소 관리
- 코드 리뷰, 이슈 관리
- 알림 수신

---

## 🎉 완료 후 확인사항

### ✅ 체크리스트
- [ ] https://github.com/gregkim0704/land 접속하여 파일 확인
- [ ] README.md 제대로 표시되는지 확인
- [ ] 코드 파일들 열어서 문제 없는지 확인
- [ ] LICENSE 파일 확인
- [ ] .gitignore 작동하는지 확인
- [ ] Star ⭐ 눌러서 북마크!

---

## 💡 추가 팁

### 1. GitHub Actions로 자동화
```yaml
# .github/workflows/test.yml
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest
```

### 2. Issues로 버그 추적
- New Issue 생성
- 버그, 기능 요청 관리
- 라벨로 분류

### 3. Projects로 작업 관리
- 칸반 보드 스타일
- To Do → In Progress → Done
- 팀 협업에 유용

---

## 🆘 도움이 필요하면?

- **GitHub 문서**: https://docs.github.com
- **Git 기초**: https://git-scm.com/book/ko/v2
- **Markdown 가이드**: https://guides.github.com/features/mastering-markdown/

---

## 🚀 지금 바로 시작!

```bash
cd /path/to/land_ai_system
git init
git add .
git commit -m "Initial commit: 토지 AI 시스템 v1.0.0"
git remote add origin https://github.com/gregkim0704/land.git
git branch -M main
git push -u origin main
```

**성공하면 https://github.com/gregkim0704/land 에서 확인하세요!** 🎉
