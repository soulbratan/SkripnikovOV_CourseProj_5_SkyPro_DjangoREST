FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=False

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

RUN poetry add drf-yasg

COPY . .

RUN mkdir -p static staticfiles

RUN python manage.py collectstatic --noinput

EXPOSE 8000
