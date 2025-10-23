# 📁 프로젝트 폴더 구조

```
land/
│
├── 📄 app.py                          # Streamlit 웹 애플리케이션
├── 📄 land_ai_core.py                 # 토지 분석 핵심 엔진
├── 📄 land_ai_chatbot.py              # AI 컨설팅 챗봇
├── 📄 requirements.txt                # Python 의존성
│
├── 📖 README.md                       # 프로젝트 메인 문서
├── 📖 QUICKSTART.md                   # 5분 빠른 시작 가이드
├── 📖 DELIVERY_REPORT.md              # 개발 완료 보고서
├── 📖 land_ai_system_plan.md          # 상세 개발 계획
├── 📖 GITHUB_UPLOAD_GUIDE.md          # GitHub 업로드 가이드
├── 📖 STRUCTURE.md                    # 이 파일
│
├── ▶️  start.bat                      # Windows 실행 스크립트
├── ▶️  start.sh                       # macOS/Linux 실행 스크립트
│
├── 📋 .gitignore                      # Git 제외 파일 설정
└── 📋 LICENSE                         # MIT 라이선스

```

## 📂 향후 추가될 폴더 (Phase 2+)

```
land/
├── data/                              # 데이터 디렉토리
│   ├── raw/                          # 원본 데이터
│   ├── processed/                    # 처리된 데이터
│   └── models/                       # 학습된 ML 모델
│
├── src/                               # 소스 코드 (리팩토링 후)
│   ├── core/                         # 핵심 로직
│   ├── api/                          # API 통합
│   ├── models/                       # 데이터 모델
│   └── utils/                        # 유틸리티
│
├── tests/                             # 테스트 코드
│   ├── test_core.py
│   ├── test_chatbot.py
│   └── test_api.py
│
├── docs/                              # 추가 문서
│   ├── api_reference.md
│   ├── user_guide.md
│   └── development.md
│
├── .github/                           # GitHub 설정
│   └── workflows/                    # GitHub Actions
│       └── test.yml
│
└── config/                            # 설정 파일
    ├── database.yaml
    └── api_keys.example
```

## 📝 파일별 설명

### 실행 파일
- **app.py**: Streamlit 기반 웹 UI, 메인 진입점
- **land_ai_core.py**: 토지 분석 알고리즘, 가격 예측, 리스크 분석
- **land_ai_chatbot.py**: AI 챗봇, 계약서 분석

### 문서
- **README.md**: GitHub 메인 페이지 (프로젝트 소개)
- **QUICKSTART.md**: 5분 설치 및 사용법
- **DELIVERY_REPORT.md**: 개발 현황 및 성과
- **land_ai_system_plan.md**: 기술 스펙 및 로드맵
- **GITHUB_UPLOAD_GUIDE.md**: Git/GitHub 사용법

### 설정
- **requirements.txt**: pip 의존성 목록
- **.gitignore**: Git에서 제외할 파일
- **LICENSE**: MIT 오픈소스 라이선스

### 스크립트
- **start.bat**: Windows 원클릭 실행
- **start.sh**: Unix 원클릭 실행

## 🎯 파일 크기

| 파일 | 크기 | 설명 |
|------|------|------|
| app.py | 22KB | 웹 UI 코드 |
| land_ai_core.py | 19KB | 분석 엔진 |
| land_ai_chatbot.py | 15KB | 챗봇 |
| README.md | 8KB | 문서 |
| **전체** | **~90KB** | 매우 가벼움! |

## 🔄 버전 관리

### v1.0.0 (현재)
- MVP 기능 구현
- 웹 UI 완성
- 기본 문서화

### v1.1.0 (계획)
- 공공 API 연동
- 데이터베이스 구축
- 테스트 코드 추가

### v2.0.0 (계획)
- 머신러닝 모델
- 모바일 앱
- API 서비스

## 📦 의존성 구조

```
streamlit (웹 프레임워크)
  ├── pandas (데이터 처리)
  ├── numpy (수치 계산)
  └── plotly (시각화)

anthropic (향후 추가)
  └── Claude API 통합

requests (공공 API 호출)
  └── 국토교통부, 토지이음
```

## 🚀 실행 흐름

```
사용자
  ↓
start.bat/sh  (실행 스크립트)
  ↓
streamlit run app.py
  ↓
app.py (웹 UI)
  ├─→ land_ai_core.py (분석)
  └─→ land_ai_chatbot.py (챗봇)
  ↓
브라우저 (http://localhost:8501)
```

## 💾 데이터 흐름

```
입력 (사용자)
  ↓
LandInfo (데이터 모델)
  ↓
LandAnalyzer (분석 엔진)
  ├─→ 건축규제 조회
  ├─→ 개발가능성 점수
  ├─→ 가격 예측
  └─→ 리스크 체크
  ↓
Report (JSON)
  ↓
웹 UI (Streamlit)
```

## 🔐 보안 고려사항

### Git에 포함되지 않는 파일 (.gitignore)
```
.env              # API 키
*.db              # 데이터베이스
__pycache__/      # Python 캐시
.venv/            # 가상환경
data/raw/*        # 원본 데이터
```

### 안전한 관리
```python
# API 키는 환경변수로
import os
api_key = os.getenv('ANTHROPIC_API_KEY')

# 고객 정보는 암호화
from cryptography.fernet import Fernet
```

## 📊 코드 통계

- **Python 파일**: 3개
- **총 코드 줄 수**: ~1,500줄
- **주석 비율**: 20%+
- **함수/클래스**: 25개+

## 🎨 코드 스타일

- **PEP 8** 준수
- **타입 힌팅** 사용
- **Docstring** 포함
- **모듈화** 설계

## 🧪 테스트 (향후)

```
tests/
├── test_land_analyzer.py
├── test_chatbot.py
└── test_matcher.py
```

## 📈 성능

- **분석 속도**: < 5초
- **메모리 사용**: < 100MB
- **동시 사용자**: 10명+ (Streamlit Cloud)

## 🌐 배포 옵션

1. **로컬**: `streamlit run app.py`
2. **Streamlit Cloud**: 무료 호스팅
3. **Heroku**: 클라우드 배포
4. **AWS/GCP**: 프로덕션 스케일

---

**이 구조는 확장 가능하도록 설계되었습니다!** 🚀
