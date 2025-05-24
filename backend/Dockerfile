FROM python:3.9-slim
WORKDIR /service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /service/app
COPY start.sh migrate_bot_table.py ./
RUN chmod +x start.sh
CMD ["./start.sh"]
