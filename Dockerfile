FROM python:3.11-alpine
WORKDIR /opt/bot
COPY *.py requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
CMD python3 -u ./bot.py