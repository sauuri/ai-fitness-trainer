import httpx
from openai import AsyncOpenAI
from typing import Optional
import json

_cache: dict = {}

KO_TO_EN: dict = {
    "스쿼트": "squat",
    "벤치프레스": "bench press",
    "데드리프트": "deadlift",
    "풀업": "pull up",
    "친업": "chin up",
    "푸시업": "push up",
    "딥스": "dips",
    "숄더프레스": "shoulder press",
    "오버헤드프레스": "overhead press",
    "바벨로우": "barbell row",
    "덤벨컬": "dumbbell curl",
    "바벨컬": "barbell curl",
    "해머컬": "hammer curl",
    "트라이셉스익스텐션": "triceps extension",
    "스컬크러셔": "skull crusher",
    "레그프레스": "leg press",
    "런지": "lunge",
    "레그컬": "leg curl",
    "레그익스텐션": "leg extension",
    "플랭크": "plank",
    "크런치": "crunch",
    "레그레이즈": "leg raise",
    "버피": "burpee",
    "마운틴클라이머": "mountain climber",
    "점핑잭": "jumping jack",
    "케이블로우": "cable row",
    "시티드로우": "seated row",
    "랫풀다운": "lat pulldown",
    "체스트플라이": "chest fly",
    "덤벨플라이": "dumbbell fly",
    "인클라인벤치프레스": "incline bench press",
    "디클라인벤치프레스": "decline bench press",
    "인클라인프레스": "incline press",
    "사이드레터럴레이즈": "lateral raise",
    "레터럴레이즈": "lateral raise",
    "프론트레이즈": "front raise",
    "리버스플라이": "reverse fly",
    "글루트브릿지": "glute bridge",
    "힙쓰러스트": "hip thrust",
    "카프레이즈": "calf raise",
    "스텝업": "step up",
    "고블렛스쿼트": "goblet squat",
    "아놀드프레스": "arnold press",
    "로마니안데드리프트": "romanian deadlift",
    "케틀벨스윙": "kettlebell swing",
    "페이스풀": "face pull",
    "업라이트로우": "upright row",
    "시티드덤벨프레스": "seated dumbbell shoulder press",
    "인클라인덤벨컬": "incline dumbbell curl",
    "케이블크런치": "cable crunch",
    "행잉레그레이즈": "hanging leg raise",
    "러시안트위스트": "russian twist",
    "박스점프": "box jump",
}


def _normalize(name: str) -> str:
    return name.lower().strip().replace(" ", "").replace("-", "").replace("_", "")


def _to_en(name: str) -> str:
    norm = _normalize(name)
    for ko, en in KO_TO_EN.items():
        if _normalize(ko) in norm:
            return en
    return name


async def _generate_from_gpt(name: str, lang: str, openai_client: AsyncOpenAI) -> Optional[dict]:
    is_ko = lang == "ko"
    system = (
        "당신은 퍼스널 트레이너입니다. 운동 정보를 JSON으로만 반환하세요. 헬스장 전문 용어를 사용하세요."
        if is_ko else
        "You are a personal trainer. Return exercise info as JSON only. Use standard gym terminology."
    )
    user_prompt = (
        f'"{name}" 운동에 대한 정보를 다음 JSON 형식으로 작성해주세요:\n'
        if is_ko else
        f'Provide information about the exercise "{name}" in the following JSON format:\n'
    )
    user_prompt += json.dumps({
        "description": "운동 설명 (2-3문장)" if is_ko else "Exercise description (2-3 sentences)",
        "target": "주동근 (예: 대흉근)" if is_ko else "Primary muscle (e.g. pectorals)",
        "secondaryMuscles": ["협력근1", "협력근2"] if is_ko else ["secondary1", "secondary2"],
        "difficulty": "초급/중급/고급" if is_ko else "beginner/intermediate/advanced",
        "instructions": [
            "1단계 설명" if is_ko else "Step 1 description",
            "2단계 설명" if is_ko else "Step 2 description",
        ],
    }, ensure_ascii=False)

    try:
        resp = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=600,
        )
        data = json.loads(resp.choices[0].message.content)
        return {
            "name": name,
            "target": data.get("target", ""),
            "bodyPart": "",
            "equipment": "",
            "difficulty": data.get("difficulty", ""),
            "description": data.get("description", ""),
            "instructions": data.get("instructions", []),
            "secondaryMuscles": data.get("secondaryMuscles", []),
            "source": "ai",
        }
    except Exception:
        return None


async def _translate_ko(data: dict, openai_client: AsyncOpenAI) -> dict:
    payload = {
        "description": data.get("description", ""),
        "instructions": data.get("instructions", []),
        "target": data.get("target", ""),
        "bodyPart": data.get("bodyPart", ""),
        "difficulty": data.get("difficulty", ""),
    }
    resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "운동 설명을 한국어로 번역합니다. JSON만 반환하세요. 운동 전문 용어는 한국 헬스장에서 쓰는 표현으로 번역하세요."},
            {"role": "user", "content": f"다음 JSON을 한국어로 번역해주세요. 키 이름은 유지하고 값만 번역:\n{json.dumps(payload, ensure_ascii=False)}"},
        ],
        response_format={"type": "json_object"},
        max_tokens=800,
    )
    translated = json.loads(resp.choices[0].message.content)
    return {**data, **translated}


async def fetch_exercise_info(name: str, api_key: str, lang: str = "en", openai_client: Optional[AsyncOpenAI] = None) -> Optional[dict]:
    cache_key = f"{_normalize(name)}_{lang}"
    if cache_key in _cache:
        return _cache[cache_key]

    result = None

    # 1) ExerciseDB 시도
    if api_key:
        en_name = _to_en(name)
        search = en_name.lower().strip()
        try:
            async with httpx.AsyncClient(timeout=5.0) as http:
                r = await http.get(
                    f"https://exercisedb.p.rapidapi.com/exercises/name/{search}",
                    params={"limit": "1", "offset": "0"},
                    headers={
                        "X-RapidAPI-Key": api_key,
                        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com",
                    },
                )
                if r.status_code == 200:
                    data = r.json()
                    if data:
                        ex = data[0]
                        result = {
                            "name": ex.get("name", ""),
                            "target": ex.get("target", ""),
                            "bodyPart": ex.get("bodyPart", ""),
                            "equipment": ex.get("equipment", ""),
                            "difficulty": ex.get("difficulty", ""),
                            "description": ex.get("description", ""),
                            "instructions": ex.get("instructions", []),
                            "secondaryMuscles": ex.get("secondaryMuscles", []),
                            "source": "db",
                        }
                        if lang == "ko" and openai_client:
                            result = await _translate_ko(result, openai_client)
        except Exception:
            pass

    # 2) DB 결과 없으면 GPT로 직접 생성
    if not result and openai_client:
        result = await _generate_from_gpt(name, lang, openai_client)

    _cache[cache_key] = result
    return result
