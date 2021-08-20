# syntax=docker/dockerfile:1

FROM python:2.7-alpine

WORKDIR /usr/src/app

COPY techtrends/requirements.txt ./
RUN pip install -r requirements.txt

COPY techtrends .

EXPOSE 3111

RUN python init_db.py

CMD ["python", "app.py", "--host=0.0.0.0"]
