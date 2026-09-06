FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "python main.py"]
