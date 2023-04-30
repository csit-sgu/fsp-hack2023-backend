FROM python:3.11-alpine

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.4.1

WORKDIR /app
COPY pyproject.toml /app/

RUN apk add --no-cache gcc libffi-dev musl-dev python3-dev postgresql-dev
RUN pip install poetry==${POETRY_VERSION} 
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
