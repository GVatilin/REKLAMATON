from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os
import requests

load_dotenv(override=True)

# --- Настройка GigaChat ---
GIGA_CREDENTIALS = os.environ.get("GIGACHAT_TOKEN")
giga_client = None

try:
    giga_client = GigaChat(credentials=GIGA_CREDENTIALS, verify_ssl_certs=False, model="GigaChat-2-Max")
except Exception as e:
    print(f"[ОШИБКА GigaChat Init] {e}")

def call_llm(prompt_text, system_instruction):
    if giga_client is None: return "[ОШИБКА API] Клиент GigaChat не инициализирован."
    # print(f"\nВызов GigaChat: Системная инструкция (начало): {system_instruction[:100]}... Промпт: {prompt_text[:100]}...")
    try:
        messages = [SystemMessage(content=system_instruction), HumanMessage(content=prompt_text)]
        res = giga_client.invoke(messages)
        # print(f"GigaChat ответ (начало): {res.content[:100]}...")
        return res.content.strip()
    except Exception as e:
        print(f"Ошибка вызова GigaChat API: {e}")
        return f"[ОШИБКА API] {e}"

def call_llm_image_bytes(data: bytes, filename: str = "image.png"):
    if giga_client is None:
        return "[ОШИБКА API] Клиент GigaChat не инициализирован."

    try:
        # Временная загрузка через BytesIO, если SDK принимает file-like объект:
        from io import BytesIO
        file_like = BytesIO(data)
        file_like.name = filename  # иногда SDK смотрит на name
        uploaded = giga_client.upload_file(file_like, purpose="general")

        prompt = (
            "Ты — опытный дейтинг-коуч и психолог, который помогает людям с вопросами о знакомствах и отношениях. "
            "Твои ответы должны быть полезными, поддерживающими и основанными на принципах здоровых отношений. "
            "Оцени, насколько привлекательна эта фотка для анкеты на сайте знакомств, "
            "Опиши сильные и слабые стороны и дай рекомендации по улучшению. Сделай это максимально кратко и лаконично."
        )

        result = giga_client.invoke([
            HumanMessage(
                content=prompt,
                additional_kwargs={"attachments": [uploaded.id_]}
            )
        ])

        return result.content.strip()

    except Exception as e:
        print(f"[ОШИБКА GigaChat image] {e}")
        return f"[ОШИБКА API] {e}"
