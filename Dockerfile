FROM python:3.5-alpine
ADD . /code
VOLUME /code
WORKDIR /code
RUN pip install -r requirements.txt
ENV FLASK_APP=application.py
CMD ["flask", "run", "--host", "0.0.0.0"]