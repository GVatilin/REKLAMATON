from uuid import uuid4

ai_url = "https://api.deepseek.com/chat/completions"
ai_model = "deepseek-chat"


async def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


async def payload_test():
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Объяснение задачи для модели"
                )
            },
            {
                "role": "user",
                "content": f'ввод пользователя'
            },
        ],
    }

async def payload_default(message, history):
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты ии помощник для знакомств. Дай ответ на вопрос пользователя по этой теме."
                    "Тебе также доступна история вашего диалога, учитывай её когда будешь отвечать"
                    "Верни json объект { text: str }. "
                )
            },
            {
                "role": "user",
                "content": (
                    f'Новое сообщение пользователя, на которое тебе нужно ответить: {message}'
                    f'История диалога: {history}'
                )
            },
        ],
    }