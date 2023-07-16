FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
