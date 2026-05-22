import json
import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from app.config import settings

app = FastAPI()
client = AsyncOpenAI(api_key=settings.openai_api_key)
BASE = pathlib.Path(__file__).parent


class RoutineRequest(BaseModel):
    goal: str        # 증량 / 감량 / 유지
    level: str       # 초급 / 중급 / 고급
    weight: float    # kg
    height: float    # cm
    target: str      # 전신 / 상체 / 하체 / 코어


class MotivationRequest(BaseModel):
    reason: str      # 헬스 가기 싫은 이유


@app.get("/")
async def root():
    return FileResponse(BASE / "static/index.html")


@app.post("/routine")
async def generate_routine(req: RoutineRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "당신은 전문 퍼스널 트레이너입니다. JSON으로만 응답합니다."
            },
            {
                "role": "user",
                "content": f"""다음 정보를 바탕으로 오늘의 운동 루틴을 짜주세요.

목표: {req.goal}
경험: {req.level}
몸무게: {req.weight}kg
키: {req.height}cm
오늘 운동 부위: {req.target}

다음 JSON 형식으로만 응답:
{{
    "title": "오늘의 루틴 제목",
    "intro": "오늘 루틴 한줄 소개",
    "exercises": [
        {{
            "name": "운동명",
            "sets": 3,
            "reps": "12회",
            "rest": "60초",
            "tip": "자세 팁"
        }}
    ],
    "total_time": "약 45분",
    "calories": "약 300kcal",
    "advice": "오늘 루틴 마무리 조언"
}}"""
            }
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))


@app.post("/motivation")
async def get_motivation(req: MotivationRequest):
    resp = await client.chat.completions.create(
        model=settings.model_name,
        messages=[
            {
                "role": "system",
                "content": "당신은 열정적인 헬스 트레이너입니다. JSON으로만 응답합니다."
            },
            {
                "role": "user",
                "content": f"""사용자가 오늘 헬스 가기 싫다고 합니다.
이유: {req.reason if req.reason else "그냥 귀찮아서"}

따끔하지만 공감되는 동기부여 멘트를 해주세요.

다음 JSON 형식으로만 응답:
{{
    "emoji": "💪",
    "message": "동기부여 멘트 (3~4문장, 현실적이고 공감되게)",
    "quote": "유명인 명언 또는 헬스 격언",
    "challenge": "오늘 최소한 이것만이라도 해봐요 (짧은 미션)"
}}"""
            }
        ],
        response_format={"type": "json_object"}
    )
    return JSONResponse(json.loads(resp.choices[0].message.content))
