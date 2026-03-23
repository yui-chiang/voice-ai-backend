import os
import json
from groq import Groq
import logging

logger = logging.getLogger(__name__)

PARSE_PROMPT = """你是一個記帳助手。從以下文字中提取所有記帳項目，回傳 JSON 陣列格式。

規則：
- 若文字包含多個消費項目（例如「麵包73和咖啡125」），必須拆成多筆記錄
- 每筆記錄獨立列出，不可合併金額
- 類別選項：food（餐飲）、drink（飲料）、transport（交通）、shopping（購物）、housing（居家）、health（醫療）、entertainment（娛樂）、other（其他）

回傳格式（只回傳 JSON 陣列，不要其他文字）：
[{{"amount": 數字, "description": "描述", "category": "類別"}}]

文字：{text}"""


class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY is not set in environment!")
        self.client = Groq(api_key=api_key)

    async def speech_to_text(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language="zh"
            )
        return transcript.text

    async def parse_transactions(self, text: str) -> list[dict]:
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": PARSE_PROMPT.format(text=text)}
                ],
                temperature=0,
                max_tokens=400,
            )
            raw = response.choices[0].message.content.strip()
            data = json.loads(raw)
            items = data if isinstance(data, list) else [data]
            return [
                {
                    "amount": float(item.get("amount", 0)),
                    "description": item.get("description", text),
                    "category": item.get("category", "other").lower(),
                }
                for item in items
                if float(item.get("amount", 0)) > 0
            ]
        except Exception as e:
            logger.error(f"LLM parse failed: {e}, falling back to raw text")
            return [{"amount": 0.0, "description": text, "category": "other"}]
