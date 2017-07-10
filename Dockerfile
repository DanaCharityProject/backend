FROM python:3.5-alpine
ADD . /code
VOLUME /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "app.py"]