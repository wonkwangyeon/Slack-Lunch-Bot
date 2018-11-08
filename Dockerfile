FROM python:3.7-alpine
LABEL authors="WonKwangYeon, luiseok"
ADD . /app
WORKDIR /app
RUN apk --no-cache add tzdata && \
        cp /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
        echo "Asia/Seoul" > /etc/timezone && \
        pip install -r requirements.txt
CMD ["python", "app.py"]