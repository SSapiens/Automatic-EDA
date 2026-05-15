FROM python:3.10-slim-bookworm

WORKDIR /app

# Install JRE for Pellet, SWI-Prolog for logic inference, and build-essential for C extensions
RUN apt-get update && mkdir -p /usr/share/man/man1 && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-jre-headless \
    swi-prolog \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
