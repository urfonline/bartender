FROM python:3.6-alpine

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP show_status
ENV FLASK_ENV production
CMD ["flask", "run", "--host=0.0.0.0"]
