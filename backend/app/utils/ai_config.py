from uuid import uuid4

ai_url = "https://api.openai.com/v1/chat/completions"
ai_model = "gpt-4.1-mini"


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
