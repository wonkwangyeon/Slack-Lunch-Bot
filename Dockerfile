FROM python:3.7-alpine
LABEL authors="WonKwangYeon, luiseok"
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]