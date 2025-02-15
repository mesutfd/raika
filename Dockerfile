FROM python:3.12-slim

WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir -r /code/requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
