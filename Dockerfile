FROM python:3.10-slim

WORKDIR /app

# Namesti sistemske odvisnosti za OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/

CMD ["python", "src/naloga1.py"]
