FROM python:3.12-alpine

WORKDIR /backend

# Устанавливаем tesseract и языковые данные (eng + rus)
RUN apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-eng \
    tesseract-ocr-data-rus

RUN pip install poetry

COPY pyproject.toml poetry.lock /backend/

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY app /backend/app

ENV PYTHONPATH=/backend

CMD ["sh", "-c", "cd app/database && alembic upgrade head && cd .. && python3 ./main.py"]
