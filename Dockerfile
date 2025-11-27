FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=False

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

RUN poetry add drf-yasg

COPY . .

RUN mkdir -p static staticfiles

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]