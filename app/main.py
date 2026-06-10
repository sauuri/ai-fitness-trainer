import json
import pathlib
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config import settings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent


def lang_sys(lang: str) -> str:
    """Append language instruction to system prompt."""
    if lang == "en":
        return " Always respond in English. Use English for all text including exercise names, tips, and advice."
    return ""


class RoutineRequest(BaseModel):
    gender: str
    age: int
    goal: str
    level: str
    weight: float
    height: float
    target: str
    location: str
    equipment: list[str]
    injury: list[str]
    duration: int
    sleep_hours: float = 7.0
    fatigue: int = 5
    stress: str = "보통"
    soreness: bool = False
    motivation: str = "보통"
    condition: int = 7
    lang: str = "ko"


class RiskRequest(BaseModel):
    sleep_hours: float = 7.0
    fatigue: int = 5
    stress: str = "보통"
    soreness: bool = False
    motivation: str = "보통"
    available_time: int = 60
    recent_logs: list[dict] = []
    missed_logs: list[dict] = []
    lang: str = "ko"


class MinRoutineRequest(BaseModel):
    gender: str
    goal: str
    level: str
    target: str
    location: str
    equipment: list[str]
    injury: list[str]
    reason: str
    available_time: int = 10
    lang: str = "ko"


class ReportRequest(BaseModel):
    gender: str
    goal: str
    level: str
    logs: list[dict]
    lang: str = "ko"


class FeedbackRequest(BaseModel):
    gender: str
    goal: str
    level: str
    recent_logs: list[dict]
    lang: str = "ko"


class AnalysisRequest(BaseModel):
    gender: str
    goal: str
    level: str
    logs: list[dict]
    missed_logs: list[dict] = []
    lang: str = "ko"


class ConvertRequest(BaseModel):
    original_routine: dict
    convert_to: str
    target_time: int = 15
    injury: list[str] = []
    equipment: list[str] = []
    lang: str = "ko"


class MotivationRequest(BaseModel):
    reason: str
    situation: str = ""
    lang: str = "ko"


class CaloriesRequest(BaseModel):
    gender: str
    age: int
    weight: float
    height: float
    goal: str
    weekly_days: int
    diet_style: str = "한식"
    ingredients: list = []
    today_kcal: int = 0
    workout_done: bool = False
    lang: str = "ko"


class RecoveryRequest(BaseModel):
    what_ate: str
    gender: str
    age: int
    weight: float
    height: float
    goal: str
    diet_style: str = "한식"
    lang: str = "ko"


class ExcuseRequest(BaseModel):
    excuse: str
    lang: str = "ko"


@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")


@app.get("/support")
async def support():
    html = """<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>지원 — No-Zero-Day</title>
<style>
  body{font-family:-apple-system,sans-serif;max-width:720px;margin:0 auto;padding:40px 24px;background:#06080f;color:#cbd5e1;line-height:1.8}
  h1{color:#f97316;font-size:24px;margin-bottom:4px}
  h2{color:#f8fafc;font-size:17px;margin-top:32px;margin-bottom:8px}
  p,li{font-size:15px;color:#94a3b8}
  a{color:#f97316;text-decoration:none}
  .card{background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:20px 24px;margin-top:12px}
  .badge{font-size:12px;color:#64748b;margin-top:48px}
</style>
</head>
<body>
<h1>No-Zero-Day 지원</h1>
<p>앱 사용 중 문제가 생기셨나요? 아래에서 도움을 받으세요.</p>

<h2>📧 문의하기</h2>
<div class="card">
  <p>이메일로 문의 주시면 24시간 내에 답변드립니다.<br>
  <a href="mailto:dlwjdghks9729@gmail.com">dlwjdghks9729@gmail.com</a></p>
</div>

<h2>❓ 자주 묻는 질문</h2>
<div class="card">
  <p><strong>Q. 운동 기록이 사라졌어요.</strong><br>
  앱 데이터는 기기 로컬에 저장됩니다. 앱 삭제 시 데이터도 함께 삭제됩니다. 앱 삭제 전 백업을 권장합니다.</p>
</div>
<div class="card">
  <p><strong>Q. AI 루틴 생성이 안 돼요.</strong><br>
  인터넷 연결 상태를 확인해 주세요. 문제가 지속되면 이메일로 문의해 주세요.</p>
</div>
<div class="card">
  <p><strong>Q. 칼로리 계산이 정확한가요?</strong><br>
  MET(운동 대사당량) 기반으로 계산되며 개인차가 있을 수 있습니다. 참고용으로 활용해 주세요.</p>
</div>
<div class="card">
  <p><strong>Q. 개인 정보는 어떻게 처리되나요?</strong><br>
  모든 운동 기록은 기기에만 저장되며 서버에 저장되지 않습니다.<br>
  <a href="/privacy">개인정보 처리방침 보기 →</a></p>
</div>

<h2>🛠 앱 정보</h2>
<div class="card">
  <p>개발자: 이정환 (sauuri)<br>
  버전: 1.0<br>
  플랫폼: iOS</p>
</div>

<p class="badge">© 2026 이정환 (sauuri). 최종 업데이트: 2026년 5월 26일</p>
</body>
</html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)


@app.get("/privacy")
async def privacy():
    html = """<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>개인정보 처리방침 — No-Zero-Day</title>
<style>
  body{font-family:-apple-system,sans-serif;max-width:720px;margin:0 auto;padding:40px 24px;background:#06080f;color:#cbd5e1;line-height:1.8}
  h1{color:#f97316;font-size:24px;margin-bottom:8px}
  h2{color:#f8fafc;font-size:17px;margin-top:32px;margin-bottom:8px}
  p,li{font-size:15px;color:#94a3b8}
  a{color:#f97316}
  .badge{font-size:12px;color:#64748b;margin-top:48px}
</style>
</head>
<body>
<h1>개인정보 처리방침</h1>
<p>No-Zero-Day (이하 "앱")는 사용자의 개인정보를 소중히 여기며 다음과 같이 처리합니다.</p>

<h2>1. 수집하는 정보</h2>
<p>앱은 서버에 개인정보를 저장하지 않습니다. 프로필(이름·나이·성별·체중·신장·운동 목표 등) 및 운동 기록은 사용자 기기의 <strong>로컬 저장소(localStorage)</strong>에만 저장됩니다.</p>

<h2>2. AI 서비스 이용</h2>
<p>맞춤 루틴 생성 시 컨디션·목표·장비 등 <strong>개인 식별 정보가 포함되지 않는</strong> 운동 관련 데이터가 OpenAI API로 전송될 수 있습니다. OpenAI의 개인정보 처리방침은 <a href="https://openai.com/privacy" target="_blank">openai.com/privacy</a>에서 확인하실 수 있습니다.</p>

<h2>3. 제3자 제공</h2>
<p>앱은 사용자의 데이터를 제3자에게 판매하거나 제공하지 않습니다.</p>

<h2>4. 데이터 삭제</h2>
<p>앱 삭제 시 기기에 저장된 모든 데이터가 함께 삭제됩니다. 프로필 탭에서 데이터를 직접 초기화할 수도 있습니다.</p>

<h2>5. 저작권</h2>
<p>© 2026 이정환 (sauuri). No-Zero-Day 앱 및 관련 콘텐츠의 저작권은 개발자에게 있습니다. 무단 복제 및 재배포를 금합니다.</p>

<h2>6. 문의</h2>
<p>개인정보 처리방침에 관한 문의: <a href="mailto:dlwjdghks9729@gmail.com">dlwjdghks9729@gmail.com</a></p>

<p class="badge">최종 업데이트: 2026년 5월 25일</p>
</body>
</html>"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(html)


@app.post("/routine")
async def generate_routine(req: RoutineRequest):
    injury_text = f"부상 부위: {', '.join(req.injury)}" if req.injury else "부상 없음"
    equip_text = ', '.join(req.equipment) if req.equipment else "맨몸"

    condition_notes = []
    if req.sleep_hours < 6:
        condition_notes.append(f"수면 {req.sleep_hours}시간 (부족)")
    if req.fatigue >= 7:
        condition_notes.append(f"피로도 {req.fatigue}/10 (높음)")
    if req.stress == "높음":
        condition_notes.append("스트레스 높음")
    if req.soreness:
        condition_notes.append("근육통 있음")
    if req.motivation == "낮음":
        condition_notes.append("운동 의욕 낮음")
    condition_summary = " / ".join(condition_notes) if condition_notes else "컨디션 양호"

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 정보를 바탕으로 오늘의 운동 루틴을 짜주세요.

성별: {req.gender} / 나이: {req.age}세 / 몸무게: {req.weight}kg / 키: {req.height}cm
목표: {req.goal} / 경험: {req.level} / 오늘 부위: {req.target}
운동 장소: {req.location} / 보유 장비: {equip_text}
{injury_text} / 운동 가능 시간: {req.duration}분

오늘 컨디션:
- 수면: {req.sleep_hours}시간
- 피로도: {req.fatigue}/10
- 스트레스: {req.stress}
- 근육통: {'있음' if req.soreness else '없음'}
- 운동 의욕: {req.motivation}
- 요약: {condition_summary}

부상 부위 운동은 절대 포함하지 마세요.
피로도가 7 이상이거나 수면이 6시간 미만이면 고중량·고강도 대신 중간 강도 루틴으로 조정하세요.
피로도 9 이상이면 회복 중심의 가벼운 루틴을 짜주세요.

다음 JSON 형식으로만 응답:
{{
    "title": "루틴 제목",
    "intro": "한줄 소개",
    "difficulty": "중급",
    "condition_note": "오늘 컨디션 반영 설명 (1~2문장)",
    "warmup": [{{"name": "운동명", "duration": "5분", "desc": "설명"}}],
    "main": [{{
        "name": "운동명",
        "sets": 3,
        "reps": "12회",
        "rest": "60초",
        "purpose": "운동 목적",
        "tip": "자세 팁",
        "caution": "주의사항",
        "alternative": "대체 운동명"
    }}],
    "cooldown": [{{"name": "스트레칭명", "duration": "2분", "desc": "설명"}}],
    "total_time": "약 50분",
    "calories": "약 350kcal",
    "advice": "오늘 루틴 조언",
    "injury_note": "부상 관련 주의사항 (없으면 빈 문자열)"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/predict-risk")
async def predict_risk(req: RiskRequest):
    recent_summary = ""
    if req.recent_logs:
        missed = sum(1 for l in req.recent_logs if l.get("skipped"))
        recent_summary = f"최근 {len(req.recent_logs)}회 기록 중 {missed}회 건너뜀"

    missed_reasons: dict[str, int] = {}
    for l in req.missed_logs[-14:]:
        r = l.get("reason", "기타")
        missed_reasons[r] = missed_reasons.get(r, 0) + 1
    missed_summary = ", ".join(f"{k} {v}회" for k, v in missed_reasons.items()) or "없음"

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 운동 심리 전문 AI 코치입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""오늘 사용자의 운동 실패 위험도를 분석해주세요.

오늘 상태:
- 수면: {req.sleep_hours}시간
- 피로도: {req.fatigue}/10
- 스트레스: {req.stress}
- 근육통: {'있음' if req.soreness else '없음'}
- 운동 의욕: {req.motivation}
- 가능한 시간: {req.available_time}분
- 최근 운동 기록: {recent_summary or '없음'}
- 최근 실패 원인: {missed_summary}

다음 JSON 형식으로만 응답:
{{
    "risk_score": 75,
    "risk_level": "높음",
    "reasons": ["수면 부족으로 집중력 저하", "피로도가 높아 부상 위험"],
    "recommendation": "오늘은 60분 루틴 대신 집에서 10분 최소 실행 루틴을 추천합니다.",
    "go_or_min": "min"
}}

go_or_min은 risk_score 60 미만이면 'go', 60 이상이면 'min'.
risk_level: 30 미만 '낮음' / 30~59 '보통' / 60~79 '높음' / 80 이상 '매우 높음'."""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/min-routine")
async def get_min_routine(req: MinRoutineRequest):
    injury_text = f"부상 부위: {', '.join(req.injury)}" if req.injury else "부상 없음"
    equip_text = ', '.join(req.equipment) if req.equipment else "맨몸"

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 운동 습관 코치입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""사용자가 오늘 운동하기 싫다고 합니다.
이유: {req.reason}
목표 부위: {req.target} / 장소: {req.location} / 장비: {equip_text}
{injury_text} / 가능한 시간: {req.available_time}분
목표: {req.goal} / 경험: {req.level}

"제로데이를 막는" 최소 실행 루틴을 짜주세요.
목표는 완벽한 운동이 아니라 오늘 하루 0일을 막는 것입니다.
총 {req.available_time}분 이내, 정말 쉽고 간단하게.

다음 JSON 형식으로만 응답:
{{
    "title": "최소 실행 루틴 제목",
    "tagline": "오늘의 목표: 0일을 막는 것",
    "total_time": "8분",
    "steps": [
        {{"step": 1, "name": "운동복 입기", "duration": "1분", "desc": "준비만 해도 절반은 성공"}},
        {{"step": 2, "name": "스쿼트", "reps": "10개", "desc": "천천히"}}
    ],
    "success_message": "오늘의 성공 기준은 완벽한 운동이 아니라 0일을 막는 것입니다.",
    "upgrade_prompt": "여기까지 했으면 5분만 더 해볼까요? 어차피 시작했으니까."
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/analyze-failures")
async def analyze_failures(req: AnalysisRequest):
    logs_text = json.dumps(req.logs[-30:], ensure_ascii=False)
    missed_text = json.dumps(req.missed_logs[-20:], ensure_ascii=False)

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 운동 기록을 분석하고 실패 패턴을 파악해주세요.

성별: {req.gender} / 목표: {req.goal} / 경험: {req.level}
운동 기록: {logs_text}
운동 실패 기록: {missed_text}

다음 JSON 형식으로만 응답:
{{
    "total_logged": 12,
    "total_missed": 5,
    "completion_rate": 71,
    "top_failure_reason": "피로",
    "pattern_summary": "주로 피로와 시간 부족으로 운동을 놓칩니다.",
    "failure_analysis": "당신은 의지 부족보다 피로 누적으로 운동을 놓치는 경우가 많습니다.",
    "strategy": [
        "월요일은 20분 짧은 루틴으로 시작하세요",
        "피로도가 7 이상이면 자동으로 최소 실행 루틴을 추천합니다"
    ],
    "next_week_plan": "다음 주 전략 요약 (2~3문장)"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/convert-routine")
async def convert_routine(req: ConvertRequest):
    injury_text = f"부상 부위: {', '.join(req.injury)}" if req.injury else "부상 없음"
    equip_text = ', '.join(req.equipment) if req.equipment else "맨몸"
    convert_map = {
        "home": "집에서 할 수 있는 맨몸/덤벨 루틴",
        "short": f"{req.target_time}분 이내 짧은 루틴",
        "recovery": "회복 중심 저강도 루틴",
        "no_equipment": "장비 없이 맨몸만으로 하는 루틴",
        "knee_safe": "무릎에 부담 없는 루틴",
    }
    convert_desc = convert_map.get(req.convert_to, "적합한 대안 루틴")
    original_text = json.dumps(req.original_routine, ensure_ascii=False)

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 운동 루틴을 변환해주세요.

원본 루틴: {original_text}
변환 목표: {convert_desc}
{injury_text} / 사용 가능 장비: {equip_text}

다음 JSON 형식으로만 응답:
{{
    "title": "변환된 루틴 제목",
    "convert_summary": "변환 요약 (1~2문장)",
    "main": [{{
        "original_name": "원래 운동명",
        "name": "변환된 운동명",
        "sets": 3,
        "reps": "12회",
        "rest": "60초",
        "tip": "자세 팁",
        "convert_reason": "변환 이유"
    }}],
    "total_time": "약 20분",
    "note": "추가 안내사항"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/report")
async def get_report(req: ReportRequest):
    logs_text = json.dumps(req.logs, ensure_ascii=False)
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 운동 기록을 바탕으로 4주 성장 리포트를 작성해주세요.

성별: {req.gender} / 목표: {req.goal} / 경험: {req.level}
전체 운동 기록: {logs_text}

다음 JSON 형식으로만 응답:
{{
    "total_sessions": 12,
    "avg_completion": 82,
    "most_trained": "상체",
    "least_trained": "하체",
    "streak": 3,
    "weight_change": "기록 없음",
    "strength_growth": "점진적 향상",
    "summary": "전반적인 4주 총평 (3~4문장)",
    "next_focus": "다음 2주 집중 추천",
    "achievements": ["달성한 것 1", "달성한 것 2"],
    "warnings": ["주의할 점 1"]
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/feedback")
async def get_feedback(req: FeedbackRequest):
    logs_text = json.dumps(req.recent_logs, ensure_ascii=False)
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 운동 기록을 분석하고 피드백을 주세요.

성별: {req.gender} / 목표: {req.goal} / 경험: {req.level}
최근 운동 기록: {logs_text}

다음 JSON 형식으로만 응답:
{{
    "summary": "전체 운동 패턴 요약",
    "good": ["잘하고 있는 점 1", "잘하고 있는 점 2"],
    "improve": ["개선할 점 1", "개선할 점 2"],
    "next_tip": "다음 운동을 위한 핵심 조언",
    "weekly_goal": "이번 주 목표 제안"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/motivation")
async def get_motivation(req: MotivationRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 현실적이고 공감하는 헬스 트레이너입니다. '당신은 할 수 있어요', '파이팅', '화이팅', '힘내세요' 같은 뻔한 문구는 절대 쓰지 마세요. 사용자의 상황을 인정하고 오늘의 목표를 낮춰서 재정의하는 방식으로 답하세요. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""사용자가 오늘 헬스 가기 싫다고 합니다.
상황: {req.situation or '그냥 귀찮음'}
이유: {req.reason or '특별한 이유 없음'}

다음 JSON 형식으로만 응답:
{{
    "emoji": "💪",
    "message": "공감하면서 따끔한 동기부여 멘트 (3~4문장)",
    "quote": "헬스/스포츠 관련 명언",
    "challenge": "오늘 최소한 이것만 해봐요 (아주 짧고 쉬운 미션)"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/calories")
async def get_calories(req: CaloriesRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 No-Zero-Day 앱의 복구 식단 코치입니다. 완벽한 다이어트를 강요하는 영양사가 아닙니다. 사용자가 운동을 못 했거나, 야식을 먹었거나, 하루가 망한 것 같을 때 자책하지 않고 다시 이어갈 수 있도록 돕습니다. 목표는 완벽한 식단이 아니라 오늘을 완전히 0점으로 끝내지 않는 것입니다. 칼로리와 영양소는 참고용으로만 제시하고 사용자를 압박하지 마세요. '힘내세요', '포기하지 마세요' 같은 뻔한 문구는 쓰지 마세요. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""다음 정보를 바탕으로 오늘 실천 가능한 복구 식단을 추천해주세요.

성별: {req.gender} / 나이: {req.age}세 / 몸무게: {req.weight}kg / 키: {req.height}cm
목표: {req.goal} / 주당 운동 횟수: {req.weekly_days}회
선호 식단 스타일: {req.diet_style}
오늘 운동 여부: {'완료 (소모 칼로리: ' + str(req.today_kcal) + 'kcal)' if req.workout_done else '운동 못 함'}
{"보유 재료: " + ", ".join(req.ingredients) if req.ingredients else "보유 재료: 특별히 없음"}

식단 작성 규칙:
1. 보유 재료가 있으면 그 재료를 최대한 활용한 식단을 구성하세요.
2. {req.diet_style} 스타일을 기반으로 작성하되, 보유 재료와 자연스럽게 조합하세요.
3. 오늘 운동을 완료했으면 소모 칼로리를 고려해 회복·보충 중심 식단으로 구성하세요.
4. 오늘 운동을 못 했으면 가볍고 유지하기 좋은 식단으로, 자책 없이 구성하세요.
5. 각 식사 설명에 재료별 구체적인 양을 반드시 포함하세요. 예: "두부 1/2모(175g, 단백질 12g)", "닭가슴살 150g(단백질 35g)", "햇반 1개(210g, 탄수화물 69g)"
6. 중요: 아침+점심+저녁+간식의 단백질 합계가 protein 값과 일치해야 하고, 칼로리 합계가 target_calories와 일치해야 합니다. 수치를 먼저 정하고 그에 맞춰 식사를 구성하세요.
7. ingredient_note 필드에: 보유 재료만으로 단백질 목표({req.weight * 2:.0f}g 기준)를 채울 수 있는지 현실적으로 한 줄 평가해주세요. 예: "두부 두 모로는 단백질 약 48g — 목표의 1/3 수준. 닭가슴살 200g 추가하면 충분합니다."

tip 필드는 반드시 다음 내용을 포함하세요:
1. 오늘 상황에 대한 짧은 공감 (자책 유발 금지)
2. 오늘 이 식단이 왜 괜찮은지 한 문장
3. 내일 다시 이어가기 위한 작은 행동 1개

다음 JSON 형식으로만 응답:
{{
    "tdee": 2200,
    "target_calories": 1900,
    "protein": 140,
    "carbs": 210,
    "fat": 50,
    "meals": {{
        "breakfast": "두부 1/2모(175g, 단백질 12g) + 햇반 1개 예시",
        "lunch": "재료명 용량(단백질/탄수화물 표기) 예시",
        "dinner": "재료명 용량 예시",
        "snack": "간식 예시"
    }},
    "ingredient_note": "보유 재료로 단백질 목표 달성 가능 여부 한 줄 평가",
    "tip": "공감 + 괜찮은 이유 + 내일을 위한 작은 행동"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/recovery-meal")
async def recovery_meal(req: RecoveryRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 No-Zero-Day 앱의 식단 회복 코치입니다. 오늘 과식하거나 식단을 망친 사람에게 자책 없이 내일 어떻게 조절하면 되는지 숫자로 명확하게 알려줍니다. '힘내세요', '괜찮아요' 같은 뻔한 위로는 하지 않습니다. 그냥 현실적인 숫자와 실천 가능한 식단을 제시합니다. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""오늘 먹은 것: {req.what_ate}
성별: {req.gender} / 나이: {req.age}세 / 몸무게: {req.weight}kg / 키: {req.height}cm
목표: {req.goal} / 선호 식단: {req.diet_style}

중요: 사용자가 입력한 수량을 반드시 그대로 사용하세요. "한통", "두 개", "한 판" 등 수량 표현이 있으면 절대 1인분으로 바꾸지 마세요. 수량이 명시되지 않은 경우에만 1인분으로 가정하세요.

다음을 계산해주세요:
1. 오늘 먹은 것의 칼로리 추정 — 입력된 수량 그대로 계산 (브랜드/메뉴 알면 실제 수치 사용)
2. 이 사람의 하루 권장 칼로리(daily_target) 계산
3. 초과분(excess) = what_ate_kcal - daily_target
4. 내일 목표(tomorrow_target) = daily_target - excess (단, 기초대사량 이하로는 내리지 말 것)
5. 내일 식단 — 아침+점심+저녁+간식 칼로리 합계가 반드시 tomorrow_target과 일치해야 함

식단 작성 규칙:
- 한식이면 밥을 반드시 포함하고 밥 칼로리(공기밥 300kcal)를 함께 표기할 것. 예: "김치찌개 1인분 + 공기밥 (550kcal)"
- 양식/간편식도 주식+반찬 형태로 현실적으로 구성할 것
- 각 끼니 칼로리를 명시하고, 4끼 합계 = tomorrow_target 이 되도록 수치를 먼저 정하고 식단을 구성할 것

tone: 자책 유발 금지. 그냥 숫자 사실만. "이틀 평균으로 보면 됩니다" 식으로.

JSON 형식:
{{
  "what_ate_kcal": 1700,
  "what_ate_detail": "엽떡 한통(2인분 기준) 약 1700kcal — 떡볶이 1000kcal + 순대 400kcal + 튀김 300kcal",
  "daily_target": 2000,
  "excess": 350,
  "tomorrow_target": 1650,
  "adjustment_note": "내일 350kcal만 줄이면 이틀 평균이 맞춰져요. 끼니당 약 100kcal씩 줄이면 됩니다.",
  "meals": {{
    "breakfast": "음식명 (칼로리)",
    "lunch": "음식명 (칼로리)",
    "dinner": "음식명 (칼로리)",
    "snack": "음식명 (칼로리)"
  }},
  "tip": "자책 없는 한 줄 코멘트"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/excuse")
async def translate_excuse(req: ExcuseRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": f"당신은 운동 포기 직전의 사람을 잡아주는 AI 코치입니다. 절대 혼내지 않고, 공감하면서 작은 행동으로 안내합니다. '당신은 할 수 있어요', '파이팅', '화이팅', '힘내세요', '포기하지 마세요' 같은 뻔한 동기부여 문구는 절대 쓰지 마세요. 사용자의 핑계를 인정하고, 오늘의 목표 자체를 낮춰서 재정의하세요. 예: '오늘 목표는 근성장이 아니라 운동 흐름 유지입니다'. JSON으로만 응답합니다.{lang_sys(req.lang)}"},
            {"role": "user", "content": f"""사용자가 오늘 운동을 포기하려 합니다.
변명/이유: "{req.excuse}"

이 변명을 공감하면서 실행 가능한 최소 행동으로 변환해주세요.
목표는 완벽한 운동이 아니라 오늘을 0으로 끝내지 않는 것입니다.

다음 JSON 형식으로만 응답:
{{
    "empathy": "변명에 공감하는 짧은 말 (1문장, 따뜻하게)",
    "reframe": "관점을 바꿔주는 말 (1문장, 오늘 목표를 낮춰줌)",
    "action": "지금 당장 할 수 있는 최소 행동 (구체적으로, 1~2문장)",
    "route": "1min 또는 5min 또는 rest",
    "button_label": "행동 버튼 텍스트 (10자 이내)"
}}

route 기준: 피로/통증/늦은시간 → rest / 귀찮음/의욕없음/운동복 → 1min / 여유있음 → 5min"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))
