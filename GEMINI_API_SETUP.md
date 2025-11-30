# 🤖 Gemini API 설정 가이드

Google Gemini API를 토지 AI 시스템에 통합하는 완전한 가이드입니다.

---

## 📋 목차

1. [Gemini API란?](#gemini-api란)
2. [API 키 발급 방법](#api-키-발급-방법)
3. [프로젝트 설정](#프로젝트-설정)
4. [테스트 및 확인](#테스트-및-확인)
5. [사용량 및 요금](#사용량-및-요금)
6. [문제 해결](#문제-해결)

---

## 🎯 Gemini API란?

**Google Gemini**는 Google의 최신 대규모 언어 모델(LLM)입니다.

### 장점
- ✅ **무료 티어**: 월 60회/분 무료 (개발/테스트에 충분)
- ✅ **빠른 속도**: Claude보다 빠른 응답
- ✅ **저렴한 비용**: Claude 대비 1/40 가격
- ✅ **멀티모달**: 텍스트 + 이미지 분석 가능
- ✅ **한국어 지원**: 우수한 한국어 이해도

### 토지 AI 시스템에서의 활용
- 💬 **기본 상담**: 일반적인 토지 투자 질문
- 🔍 **토지 분석**: 기본 개발 가능성 평가
- 💰 **가격 예측**: 시장 가격 추정 보조
- 📊 **데이터 분석**: 시장 트렌드 분석

---

## 🔑 API 키 발급 방법

### 1단계: Google AI Studio 접속

1. 브라우저에서 다음 주소로 이동:
   ```
   https://makersuite.google.com/app/apikey
   ```

2. Google 계정으로 로그인
   - Gmail 계정이 필요합니다
   - 없으면 무료로 생성: https://accounts.google.com/signup

### 2단계: API 키 생성

1. **"Create API Key"** 버튼 클릭

2. 프로젝트 선택 또는 생성
   - 기존 Google Cloud 프로젝트가 있으면 선택
   - 없으면 **"Create API key in new project"** 선택

3. API 키 복사
   ```
   예시: AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
   ⚠️ **중요**: 이 키는 다시 볼 수 없으니 안전한 곳에 저장하세요!

### 3단계: API 키 보안

❌ **절대 하지 말 것**:
- GitHub에 업로드
- 공개 저장소에 포함
- 다른 사람과 공유
- 코드에 직접 하드코딩

✅ **올바른 방법**:
- `.env` 파일에 저장 (`.gitignore`에 포함됨)
- 환경 변수로 관리
- 비밀번호 관리자에 백업

---

## ⚙️ 프로젝트 설정

### 1단계: 환경 변수 파일 생성

프로젝트 루트 디렉토리에서:

```bash
# .env.example을 복사하여 .env 생성
cp .env.example .env
```

Windows에서:
```cmd
copy .env.example .env
```

### 2단계: API 키 입력

`.env` 파일을 텍스트 에디터로 열고 다음 줄을 찾아 수정:

```env
# Gemini API 키 (발급받은 키로 변경)
GEMINI_API_KEY=AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**실제 예시**:
```env
# 이전 (예시)
GEMINI_API_KEY=your_gemini_api_key_here

# 이후 (실제 키)
GEMINI_API_KEY=AIzaSyD-9Qx7YZ3mK5nP8rT2vW4xA6bC1dE0fG
```

### 3단계: 의존성 설치

Gemini API 사용을 위한 패키지 설치:

```bash
pip install google-generativeai
```

또는 전체 의존성 설치:

```bash
pip install -r requirements.txt
```

### 4단계: 설정 확인

`.env` 파일이 제대로 설정되었는지 확인:

```bash
# Windows
type .env | findstr GEMINI

# Linux/Mac
cat .env | grep GEMINI
```

출력 예시:
```
GEMINI_API_KEY=AIzaSyD-9Qx7YZ3mK5nP8rT2vW4xA6bC1dE0fG
```

---

## 🧪 테스트 및 확인

### 방법 1: Python 스크립트로 테스트

`test_gemini.py` 파일 생성:

```python
import os
from dotenv import load_dotenv
import google.generativeai as genai

# 환경 변수 로드
load_dotenv()

# API 키 확인
api_key = os.getenv('GEMINI_API_KEY')
print(f"API 키 확인: {api_key[:20]}..." if api_key else "❌ API 키 없음")

# Gemini 초기화
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # 간단한 테스트
    response = model.generate_content("안녕하세요! 간단히 인사해주세요.")
    print(f"\n✅ Gemini API 연결 성공!")
    print(f"응답: {response.text}")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
```

실행:
```bash
python test_gemini.py
```

### 방법 2: 토지 AI 시스템으로 테스트

```python
from ai_models_gemini import UnifiedAIManager

# AI 매니저 초기화
ai = UnifiedAIManager(prefer_gemini=True)

# 프로바이더 정보 확인
info = ai.get_provider_info()
print(f"활성 프로바이더: {info['active_provider']}")
print(f"Gemini 사용 가능: {info['gemini_available']}")

# 간단한 상담 테스트
if info['gemini_available']:
    response = ai.chat_consultation("토지 투자 시 주의할 점은?")
    print(f"\n응답:\n{response}")
```

### 방법 3: 웹 앱으로 테스트

```bash
# 앱 실행
streamlit run app_commercial.py

# 또는
start_commercial.bat  # Windows
./start_commercial.sh  # Linux/Mac
```

브라우저에서 `http://localhost:8501` 접속 후:
1. 회원가입/로그인
2. **AI 상담** 메뉴 선택
3. 질문 입력 (예: "농지 투자 어떤가요?")
4. Gemini의 응답 확인

---

## 💰 사용량 및 요금

### 무료 티어 (Free Tier)

**제한**:
- 분당 요청: 60회
- 일일 요청: 1,500회
- 월간 요청: 제한 없음

**충분한 경우**:
- ✅ 개발 및 테스트
- ✅ 소규모 프로젝트 (일 100명 이하)
- ✅ 프로토타입 제작

### 유료 플랜 (Pay-as-you-go)

**가격** (2024년 기준):
- 입력: $0.075 / 1M 토큰
- 출력: $0.30 / 1M 토큰

**비교** (Claude 대비):
- Claude: 입력 $3, 출력 $15 / 1M 토큰
- **Gemini가 40배 저렴!** 💰

**예상 비용** (월 1,000명 사용자):
- 기본 상담 5,000회: ~$5
- 토지 분석 1,000회: ~$3
- **총 예상: $8/월**

### 사용량 모니터링

Google Cloud Console에서 확인:
1. https://console.cloud.google.com/
2. 프로젝트 선택
3. **APIs & Services** > **Dashboard**
4. **Generative Language API** 클릭
5. 사용량 그래프 확인

---

## 🔧 고급 설정

### 1. 모델 선택

```python
# 기본 모델 (빠르고 저렴)
model = genai.GenerativeModel('gemini-pro')

# 향후 사용 가능한 모델
# model = genai.GenerativeModel('gemini-pro-vision')  # 이미지 분석
# model = genai.GenerativeModel('gemini-ultra')  # 최고 성능
```

### 2. 생성 설정

```python
generation_config = {
    "temperature": 0.7,  # 창의성 (0.0~1.0)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    'gemini-pro',
    generation_config=generation_config
)
```

### 3. 안전 설정

```python
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    'gemini-pro',
    safety_settings=safety_settings
)
```

---

## 🐛 문제 해결

### 문제 1: "API key not valid"

**원인**: API 키가 잘못되었거나 활성화되지 않음

**해결**:
1. API 키 재확인
2. Google AI Studio에서 새 키 발급
3. `.env` 파일 재확인
4. 앱 재시작

### 문제 2: "Quota exceeded"

**원인**: 무료 티어 한도 초과

**해결**:
1. 사용량 확인: https://console.cloud.google.com/
2. 다음 날까지 대기 (일일 한도)
3. 또는 유료 플랜 활성화

### 문제 3: "Module not found: google.generativeai"

**원인**: 패키지 미설치

**해결**:
```bash
pip install google-generativeai
```

### 문제 4: API 키가 로드되지 않음

**원인**: `.env` 파일 위치 또는 형식 문제

**해결**:
```bash
# 1. .env 파일 위치 확인 (프로젝트 루트)
ls -la .env  # Linux/Mac
dir .env     # Windows

# 2. 파일 내용 확인
cat .env | grep GEMINI  # Linux/Mac
type .env | findstr GEMINI  # Windows

# 3. 형식 확인 (공백 없이)
GEMINI_API_KEY=AIzaSy...  # ✅ 올바름
GEMINI_API_KEY = AIzaSy... # ❌ 공백 있음
```

### 문제 5: "Resource exhausted"

**원인**: 너무 많은 요청

**해결**:
```python
import time

# 요청 사이에 지연 추가
for i in range(10):
    response = model.generate_content(prompt)
    time.sleep(1)  # 1초 대기
```

---

## 📚 추가 리소스

### 공식 문서
- **Gemini API 문서**: https://ai.google.dev/docs
- **Python SDK**: https://github.com/google/generative-ai-python
- **가격 정보**: https://ai.google.dev/pricing

### 커뮤니티
- **Stack Overflow**: `[google-gemini]` 태그
- **GitHub Issues**: https://github.com/google/generative-ai-python/issues
- **Google AI Forum**: https://discuss.ai.google.dev/

### 예제 코드
- **공식 예제**: https://github.com/google/generative-ai-docs
- **Cookbook**: https://github.com/google/generative-ai-python/tree/main/samples

---

## 🎯 다음 단계

1. ✅ API 키 발급 완료
2. ✅ `.env` 파일 설정
3. ✅ 테스트 실행
4. 🚀 **토지 AI 시스템 실행**

```bash
# Windows
start_commercial.bat

# Linux/Mac
./start_commercial.sh
```

5. 🌐 브라우저에서 `http://localhost:8501` 접속
6. 💬 AI 상담 기능 사용해보기!

---

## 💡 팁

### 비용 절감 팁
1. **캐싱 활용**: 같은 질문은 캐시에서 응답
2. **프롬프트 최적화**: 짧고 명확한 프롬프트
3. **배치 처리**: 여러 요청을 한 번에 처리
4. **Gemini 우선**: 기본 작업은 Gemini, 복잡한 작업만 Claude

### 성능 최적화
1. **비동기 처리**: 여러 요청 동시 처리
2. **스트리밍**: 긴 응답은 스트리밍으로
3. **타임아웃 설정**: 응답 시간 제한

### 보안 팁
1. **API 키 회전**: 정기적으로 새 키 발급
2. **IP 제한**: Google Cloud에서 IP 화이트리스트 설정
3. **사용량 알림**: 예상치 못한 사용량 감지

---

## ✅ 체크리스트

설정 완료 확인:

- [ ] Google 계정 생성/로그인
- [ ] Gemini API 키 발급
- [ ] `.env` 파일 생성
- [ ] API 키 입력
- [ ] `google-generativeai` 패키지 설치
- [ ] 테스트 스크립트 실행
- [ ] 토지 AI 시스템 실행
- [ ] AI 상담 기능 테스트

---

**🎉 축하합니다! Gemini API 설정이 완료되었습니다!**

이제 비용 효율적이고 강력한 AI 기능을 토지 AI 시스템에서 사용할 수 있습니다.

질문이나 문제가 있으면 [GitHub Issues](https://github.com/YOUR_REPO/issues)에 올려주세요.

---

**작성일**: 2024-11-30  
**버전**: 1.0  
**작성자**: Kiro AI Assistant
