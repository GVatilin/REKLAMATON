from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json
from sqlalchemy.future import select 
from uuid import UUID


from app.utils.ai_config import (
    ai_url,
    get_headers,
    payload_test,
    payload_default,
)
from app.config import get_settings


async def ai_test():
    payload = await payload_test()
    headers = await get_headers(get_settings().API_KEY)

    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)
            
                return ai_response
            else:
                return f"check_error, status: {resp.status}"


async def default_ai_answer(text, history):
    payload = await payload_default(text, history)
    headers = await get_headers(get_settings().API_KEY)

    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)
            
                return ai_response
            else:
                return f"check_error, status: {resp.status}"