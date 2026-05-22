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
    allow_origins=[
        "http://localhost",
        "https://localhost",
        "capacitor://localhost",
        "ionic://localhost",
        "http://localhost:3000",
        "http://localhost:8100",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent


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


class RiskRequest(BaseModel):
    sleep_hours: float = 7.0
    fatigue: int = 5
    stress: str = "보통"
    soreness: bool = False
    motivation: str = "보통"
    available_time: int = 60
    recent_logs: list[dict] = []
    missed_logs: list[dict] = []


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


class ReportRequest(BaseModel):
    gender: str
    goal: str
    level: str
    logs: list[dict]


class FeedbackRequest(BaseModel):
    gender: str
    goal: str
    level: str
    recent_logs: list[dict]


class AnalysisRequest(BaseModel):
    gender: str
    goal: str
    level: str
    logs: list[dict]
    missed_logs: list[dict] = []


class ConvertRequest(BaseModel):
    original_routine: dict
    convert_to: str
    target_time: int = 15
    injury: list[str] = []
    equipment: list[str] = []


class MotivationRequest(BaseModel):
    reason: str
    situation: str = ""


class CaloriesRequest(BaseModel):
    gender: str
    age: int
    weight: float
    height: float
    goal: str
    weekly_days: int
    diet_style: str = "한식"


@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")


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
            {"role": "system", "content": "당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 운동 심리 전문 AI 코치입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 운동 습관 코치입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 데이터 기반 AI 피트니스 코치입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 현실적이고 공감하는 헬스 트레이너입니다. JSON으로만 응답합니다."},
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
            {"role": "system", "content": "당신은 영양사입니다. JSON으로만 응답합니다."},
            {"role": "user", "content": f"""다음 정보를 바탕으로 하루 칼로리와 식단을 추천해주세요.

성별: {req.gender} / 나이: {req.age}세 / 몸무게: {req.weight}kg / 키: {req.height}cm
목표: {req.goal} / 주당 운동 횟수: {req.weekly_days}회
선호 식단 스타일: {req.diet_style}

식단 예시는 반드시 {req.diet_style} 스타일로 작성해주세요.
한식이면 밥·국·반찬 위주, 양식이면 파스타·샐러드·스테이크 위주,
빵/샌드위치면 토스트·베이글·샌드위치 위주, 간편식이면 편의점·조리 최소화 위주,
고단백 위주면 닭가슴살·계란·단백질쉐이크 중심으로 작성해주세요.

다음 JSON 형식으로만 응답:
{{
    "tdee": 2200,
    "target_calories": 1900,
    "protein": 140,
    "carbs": 210,
    "fat": 50,
    "meals": {{
        "breakfast": "아침 식단 예시",
        "lunch": "점심 식단 예시",
        "dinner": "저녁 식단 예시",
        "snack": "간식 예시"
    }},
    "tip": "식단 조언"
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))
