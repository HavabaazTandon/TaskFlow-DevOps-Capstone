FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --system taskflow && \
    useradd --system --gid taskflow --create-home taskflow

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=taskflow:taskflow . .

RUN mkdir -p instance logs && \
    chown -R taskflow:taskflow /app

USER taskflow

EXPOSE 5002

CMD ["python", "app.py"]
