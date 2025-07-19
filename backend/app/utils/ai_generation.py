from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
import json
from sqlalchemy.future import select 
from uuid import UUID
from typing import Optional, Union
from pathlib import Path

from app.utils.ai_config import (
    ai_url,
    get_headers,
    payload_test,
    payload_default,
    payload_form_analyze,
    payload_partner,
    payload_chat_analysis,
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


async def form_analyze(form, history):
    payload = await payload_form_analyze(form, history)
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


async def partner_ai_answer(text, history):
    payload = await payload_partner(text, history)
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
            

async def chat_analysis_ai_functions(history):
    payload = await payload_chat_analysis(history)
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
            
