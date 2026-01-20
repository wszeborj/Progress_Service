FROM python:3.12.8-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VIRTUALENVS_CREATE=0

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . /app/

EXPOSE 8000

CMD ["fastapi", "dev", "app/main.py","--host", "0.0.0.0", "--port", "8000"]