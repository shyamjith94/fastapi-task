FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV GIT_PYTHON_REFRESH=quiet
# Copy entire project (including main.py and app folder)
COPY . .
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY .env.dev .
COPY .env.prod .

# CMD overridden by docker-compose for Alembic
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
