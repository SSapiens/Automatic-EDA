FROM python:3.10-slim-bookworm

WORKDIR /app

# Use Bookworm stable to ensure package availability
RUN apt-get update && mkdir -p /usr/share/man/man1 && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
