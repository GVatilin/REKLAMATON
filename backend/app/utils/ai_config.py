from app.schemas import ScheduleUpdateForm


import datetime


ai_url = "https://api.deepseek.com/chat/completions"
ai_model = "deepseek-chat"


async def get_generate_deadline_text():
    return ("Ты превращаешь текстовый запрос пользователя в одну или несколько моделей создания дедлайна. "
            "Верни список дедлайнов по запросу пользователя. "
            f"Если пользователь не вводит точное время, выбери подходящее сам (например: рано вечером - в 18:00). Сейчас {datetime.datetime.now()}. "
            "Не пиши никакое время в description или указание дня недели, части дня, только описание события. Сначала идут предпочтения пользователя, то есть его личные настройки, "
            "потом идет запрос - то, что ты должен добавить как дедлайн. Учитывай предпочтения пользователя по дням недели, если пользователь пишет, "
            f"что обычно просыпается в 10, а по четвергам в 7, учитывай это и можешь ставить дедлайны раньше 10. deadline_time должен быть в формате %Y-%m-%dT%H:%M:%S."
            "Если пользователь указывает на срочность задания, то выстави значения priority как 0 - обычный, 1 - достаточно важный, 2 - важный, 3 - очень важный. "
            "По умолчанию приоритет равен 0."
            "Верни json объекты { tasks: list[ { description: str, deadline_time: str, priority: int} ] }"
            )


async def get_schedule_generation_text():
    return ("Ты генерируешь расписание (список задач с началом и концом выполнения) для пользователя по текстовому запросу. "
             "Расписание должно быть составлено на целый день, составь его так, чтобы человек был максимально продуктивен и вовремя отдыхал, "
             "Если ты считаешь, что в какой-то промежуток пользователю надо отдохнуть, не генерируй задач, которые занимают это время, просто оставь пустое место. "
             f"Если пользователь не вводит точное время, выбери подходящее сам (например: рано вечером - в 18:00). Сейчас {datetime.datetime.now()}. "
             "Не пиши никакое время в name или text или указание дня недели, части дня, только описание события. Сначала идут предпочтения пользователя, то есть его личные настройки, "
             "потом идет запрос - то, что пользователю надо сделать в этот день. Учитывай предпочтения пользователя по дням недели, если пользователь пишет, "
             f"что обычно просыпается в 10, а по четвергам в 7, учитывай это и можешь ставить задачи раньше 10. start_time и end_time должны быть в формате %Y-%m-%dT%H:%M:%S."
             "Верни json объекты { tasks: list[ { name: str, text: str, start_time: str, end_time: str, recurring: bool } ] }"
             )


async def get_add_schedule_tasks_text():
    return ("Ты превращаешь текстовый запрос пользователя в одну или несколько моделей блока задачи в расписании. "
            "Верни список блоков задач в расписании по запросу пользователя. "
            f"Если пользователь не вводит точное время, выбери подходящее сам (например: рано вечером - в 18:00). Сейчас {datetime.datetime.now()}. "
            "Не пиши никакое время в description или указание дня недели, части дня, только описание события. Сначала идут предпочтения пользователя, то есть его личные настройки, "
            "потом идет запрос - то, что ты должен добавить как блоки задач в расписании. Учитывай предпочтения пользователя по дням недели, если пользователь пишет, "
            f"что обычно просыпается в 10, а по четвергам в 7, учитывай это и можешь ставить дедлайны раньше 10. deadline_time должен быть в формате %Y-%m-%dT%H:%M:%S."
            "Верни json объекты { tasks: list[ { name: str, text: str, start_time: str, end_time: str, recurring: bool } ] }")


async def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


async def payload_generate_deadline(settings, response):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": await get_generate_deadline_text()
            },
            {
                "role": "user",
                "content": f'Предпочтения пользователя: {settings.text_settings}, запрос пользователя: {response.text}'
            },
        ],
    }


async def payload_schedule_generation(settings, response):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": await get_schedule_generation_text()
            },
            {
                "role": "user",
                "content": (f'Предпочтения пользователя: {settings.text_settings}, '
                            f'рабочее время пользователя: {settings.start_working} - {settings.end_working}, '
                            f'запрос пользователя: {response.text}')
            },
        ],
    }


async def payload_add_schedule_tasks(settings, response):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": await get_add_schedule_tasks_text()
            },
            {
                "role": "user",
                "content": f'Предпочтения пользователя: {settings.text_settings}, запрос пользователя: {response.text}'
            },
        ],
    }


async def make_schedule_tasks(data):
    ans = []
    for task in data:
        start_time = datetime.datetime.strptime(task["start_time"], f"%Y-%m-%dT%H:%M:%S")
        end_time = datetime.datetime.strptime(task["end_time"], f"%Y-%m-%dT%H:%M:%S")
        db_task = ScheduleUpdateForm(
            name=task["name"],
            text=task["text"],
            start_time=start_time,
            end_time=end_time,
            recurring=task["recurring"]
        )
        ans.append(db_task)
    
    return ans
