import base64
from typing import Optional, Union
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io
from pathlib import Path


class SimpleOCR:
    """Простой OCR процессор на базе Tesseract"""
    
    def init(self):
        """Инициализация и проверка Tesseract"""
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            raise Exception(
                "Tesseract не установлен. Установите:\n"
                "Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-rus\n"
                "macOS: brew install tesseract tesseract-lang\n"
                "Windows: скачайте с https://github.com/UB-Mannheim/tesseract/wiki"
            )
    
    async def extract_text(
        self, 
        image_data: Union[bytes, str, Path],
        lang: str = 'rus+eng',
        preprocess: bool = True
    ) -> str:
        """
        Извлекает текст из изображения
        
        Args:
            image_data: изображение (bytes, base64 строка или путь)
            lang: языки для распознавания
            preprocess: применять ли предобработку
            
        Returns:
            Извлеченный текст
        """
        try:
            # Подготавливаем изображение
            image = self._load_image(image_data)
            
            # Предобработка для улучшения качества
            if preprocess:
                image = self._preprocess_image(image)
            
            # Извлекаем текст
            text = pytesseract.image_to_string(image, lang=lang)
            
            # Очищаем результат
            return self._clean_text(text)
            
        except Exception as e:
            return f"Ошибка при извлечении текста: {str(e)}"
    
    def _load_image(self, image_data: Union[bytes, str, Path]) -> Image.Image:
        """Загружает изображение из разных форматов"""
        if isinstance(image_data, bytes):
            return Image.open(io.BytesIO(image_data))
        
        elif isinstance(image_data, str):
            # Проверяем, является ли это base64
            if image_data.startswith('data:image'):
                # Извлекаем base64 данные
                base64_str = image_data.split(',')[1]
                image_bytes = base64.b64decode(base64_str)
                return Image.open(io.BytesIO(image_bytes))
            else:
                # Считаем что это путь к файлу
                return Image.open(image_data)
        
        elif isinstance(image_data, Path):
            return Image.open(image_data)
        
        else:
            raise ValueError(f"Неподдерживаемый тип данных: {type(image_data)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Простая предобработка изображения для улучшения OCR"""
        
        # 1. Конвертируем в градации серого
        if image.mode != 'L':
            image = image.convert('L')
        
        # 2. Увеличиваем размер если слишком маленький
        width, height = image.size
        if width < 1000:
            scale = 1000 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 3. Увеличиваем контрастность
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(1.5)
        
        # 4. Увеличиваем резкость
        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(2.0)
        
        # 5. Применяем легкое размытие для удаления шума
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # 6. Бинаризация (черно-белое изображение)
        # Это особенно помогает с текстом на сложном фоне
        threshold = 128
        image = image.point(lambda p: p > threshold and 255)
        
        return image
    
    def _clean_text(self, text: str) -> str:
        """Очищает извлеченный текст"""
        # Удаляем лишние пробелы и переносы строк

        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]  # Удаляем пустые строки
        
        return '\n'.join(lines)


# Вспомогательные функции для интеграции с вашим AI

async def extract_text_from_screenshot(
    screenshot: Union[bytes, str, Path],
    lang: str = 'rus+eng'
) -> dict:
    """
    Простая функция для извлечения текста из скриншота
    
    Returns:
        dict с результатом
    """
    ocr = SimpleOCR()
    
    try:
        text = await ocr.extract_text(screenshot, lang=lang)
        return {
            "success": True,
            "text": text,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }


async def add_screenshot_to_message(
    message: str,
    screenshot: Optional[Union[bytes, str, Path]] = None
) -> str:
    """
    Добавляет текст со скриншота к сообщению
    
    Args:
        message: исходное сообщение
        screenshot: данные скриншота (опционально)
        
    Returns:
        Расширенное сообщение
    """
    if not screenshot:
        return message
    
    result = await extract_text_from_screenshot(screenshot)
    
    if result["success"] and result["text"]:
        return f"{message}\n\n[Текст со скриншота]:\n{result['text']}"
    
    return message


# Пример интеграции в ваши существующие функции

async def default_ai_answer_with_ocr(
    text: str,
    history: list,
    screenshot: Optional[Union[bytes, str, Path]] = None
):
    """Обновленная версия вашей функции с поддержкой OCR"""
    from app.utils.ai_config import ai_url, get_headers, payload_default
    from app.config import get_settings
    import aiohttp
    import json
    
    # Дополняем сообщение текстом со скриншота
    enhanced_text = await add_screenshot_to_message(text, screenshot)
    
    # Дальше ваш обычный код
    payload = await payload_default(enhanced_text, history)
    headers = await get_headers(get_settings().API_KEY)
    
    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                ai_response_text = data["choices"][0]["message"]["content"]
                if ai_response_text.startswith("```json"):
                    ai_response_text = ai_response_text[7:-3].strip()
                return json.loads(ai_response_text)
            else:
                return f"check_error, status: {resp.status}"
