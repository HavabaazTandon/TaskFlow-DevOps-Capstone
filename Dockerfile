FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system taskflow && \
    useradd --system --gid taskflow --create-home taskflow

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=taskflow:taskflow . .

RUN mkdir -p instance logs && \
    chown -R taskflow:taskflow /app

USER taskflow

EXPOSE 5002

CMD ["python", "app.py"]
