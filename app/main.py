import json
import pathlib
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config import settings

app = FastAPI()
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
    condition: int = 5       # 1~10: 오늘 컨디션
    motivation: str = "보통"  # 낮음 / 보통 / 높음


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


@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")


@app.post("/routine")
async def generate_routine(req: RoutineRequest):
    injury_text = f"부상 부위: {', '.join(req.injury)}" if req.injury else "부상 없음"
    equip_text = ', '.join(req.equipment) if req.equipment else "맨몸"

    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {"role": "system", "content": "당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다."},
            {"role": "user", "content": f"""다음 정보를 바탕으로 오늘의 운동 루틴을 짜주세요.

성별: {req.gender} / 나이: {req.age}세 / 몸무게: {req.weight}kg / 키: {req.height}cm
목표: {req.goal} / 경험: {req.level} / 오늘 부위: {req.target}
운동 장소: {req.location} / 보유 장비: {equip_text}
{injury_text} / 운동 가능 시간: {req.duration}분
오늘 컨디션: {req.condition}/10 / 운동 의욕: {req.motivation}

부상 부위 운동은 절대 포함하지 마세요. 대체 운동을 제시해주세요.
컨디션이 낮으면(1~4) 고중량·고강도 운동 대신 가볍고 안전한 루틴으로 조정하세요.

다음 JSON 형식으로만 응답:
{{
    "title": "루틴 제목",
    "intro": "한줄 소개",
    "warmup": [
        {{"name": "운동명", "duration": "5분", "desc": "설명"}}
    ],
    "main": [
        {{
            "name": "운동명",
            "sets": 3,
            "reps": "12회",
            "rest": "60초",
            "purpose": "운동 목적",
            "tip": "자세 팁",
            "caution": "주의사항",
            "alternative": "대체 운동명"
        }}
    ],
    "cooldown": [
        {{"name": "스트레칭명", "duration": "2분", "desc": "설명"}}
    ],
    "total_time": "약 50분",
    "calories": "약 350kcal",
    "advice": "오늘 루틴 조언",
    "injury_note": "부상 관련 주의사항 (없으면 빈 문자열)"
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
    "strength_growth": "벤치프레스 기록 향상",
    "summary": "전반적인 4주 총평 (3~4문장)",
    "next_focus": "다음 2주 집중 추천 (예: 하체 주 2회 포함)",
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
상황: {req.situation if req.situation else '그냥 귀찮음'}
이유: {req.reason if req.reason else '특별한 이유 없음'}

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
