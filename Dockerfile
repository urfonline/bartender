FROM python:3.6-alpine

WORKDIR /app
RUN mkdir /app/config && mkdir /app/data
COPY . /app

RUN pip install -r requirements.txt
RUN pip install gunicorn==19.9.0

EXPOSE 8000
VOLUME /app/config /app/data

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0", "show_status:app"]
