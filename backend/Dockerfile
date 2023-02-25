FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app
#RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app
CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000"]
#CMD ["python", "manage.py", "runserver"]