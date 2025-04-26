FROM python:3.11-slim

WORKDIR /app/model-generator

COPY requirements.txt ./
COPY install.sh ./

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN chmod +x ./install.sh && ./install.sh

EXPOSE 5000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
