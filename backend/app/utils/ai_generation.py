from app.database.models import DeadlineTask, Schedule
from app.schemas import DeadlineGenerate, DeadlineTaskCreateForm,\
  ScheduleGenerate, ScheduleUpdateForm, AddScheduleTasksAI
from app.utils.user import User, get_user_settings
from app.utils.ai_config import (
    ai_url,
    get_headers,
    payload_generate_deadline,
    payload_schedule_generation,
    payload_add_schedule_tasks,
    make_schedule_tasks,
)

from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import aiohttp
import json


async def generate_deadline(response: DeadlineGenerate,
                            current_user: User,
                            session: AsyncSession,
                            api_key: str) -> list[DeadlineTask]:
    url = ai_url
    headers = await get_headers(api_key)
    settings = await get_user_settings(current_user, session)
    payload = await payload_generate_deadline(settings, response)

    async with aiohttp.ClientSession() as client:
        async with client.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)

                ans = []
                for task in ai_response["tasks"]:
                    date = datetime.datetime.strptime(task["deadline_time"], f"%Y-%m-%dT%H:%M:%S")
                    db_task = DeadlineTaskCreateForm(
                        description=task["description"],
                        deadline_time=date,
                        priority=task["priority"]
                    )
                    ans.append(db_task)
                    return ans
                else:
                    return []
    


async def schedule_generation(response: ScheduleGenerate, 
                              current_user: User, 
                              session: AsyncSession,
                              api_key: str) -> list[Schedule]:
    url = ai_url
    headers = await get_headers(api_key)
    settings = await get_user_settings(current_user, session)
    payload = await payload_schedule_generation(settings, response)

    async with aiohttp.ClientSession() as client:
        async with client.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)

                ans = make_schedule_tasks(ai_response["tasks"])
                return ans
            else:
                return []


async def add_schedule_tasks(response: AddScheduleTasksAI,
                             current_user: User,
                             session: AsyncSession,
                             api_key: str) -> list[Schedule]:
    url = ai_url
    headers = await get_headers(api_key)
    settings = await get_user_settings(current_user, session)
    payload = await payload_add_schedule_tasks(settings, response)

    async with aiohttp.ClientSession() as client:
        async with client.post(url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()

                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                ai_response = json.loads(ai_response_text)

                ans = make_schedule_tasks(ai_response["tasks"])
                return ans
            else:
                return []