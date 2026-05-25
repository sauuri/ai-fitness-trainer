# NZD AI Fitness — No-Zero-Day

<p align="center">
  <img src="https://img.shields.io/badge/App%20Store-심사%20중-f97316?style=flat-square&logo=apple&logoColor=white"/>
  <img src="https://img.shields.io/badge/Platform-iOS-000000?style=flat-square&logo=apple"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white"/>
  <img src="https://img.shields.io/badge/Capacitor-119EFF?style=flat-square&logo=capacitor&logoColor=white"/>
</p>

> 오늘 운동 빠지는 날은 없다. 컨디션이 어떻든 AI가 딱 맞는 루틴을 만들어줍니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| AI 맞춤 루틴 | 컨디션·부상·장비·목표 입력 → GPT-4o-mini가 루틴 즉시 생성 |
| 고점 / 최소 실행 | 오늘 전력으로 갈지, 5분만 할지 선택 가능 |
| 운동 실패 위험 예측 | 수면·피로·스트레스 기반 운동 실패 확률 분석 |
| MET 기반 칼로리 계산 | 세트·무게·휴식시간·체중·성별 반영한 실시간 칼로리 |
| 운동 타이머 | 실시간 경과 시간 측정, 일시정지 지원 |
| 달력 기록 | 운동 완료일 달력 시각화, 연속 기록 추적 |
| 실패 패턴 분석 | 운동 못 한 날 기록 → AI가 패턴 분석 |
| 4주 성장 리포트 | 주간 운동량·칼로리·균형 점수 리포트 생성 |
| 식단 추천 | 목표·체중 기반 AI 식단 추천 |

## 기술 스택

- **Frontend**: HTML/CSS/JS (Single Page App)
- **Backend**: FastAPI + OpenAI API
- **iOS 패키징**: Capacitor
- **배포**: Vercel (서버리스)

## 데모

🌐 [웹 버전 실행](https://ai-fitness-trainer-alpha.vercel.app)

## 로컬 실행

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
