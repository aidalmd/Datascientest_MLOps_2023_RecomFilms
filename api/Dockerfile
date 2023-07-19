FROM python:3.2.10

WORKDIR /app

RUN pip install --upgrade pip
COPY . .
RUN pip install --no-cache-dir -r  requirements.txt
ENV PORT 8080
EXPOSE 8080

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]