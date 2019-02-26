FROM python:3.6-alpine

WORKDIR /app
RUN mkdir /app/config
COPY . /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 5000
VOLUME /app/config

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0", "show_status:app"]
