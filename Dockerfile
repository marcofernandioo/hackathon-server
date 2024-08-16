FROM python:3.8

WORKDIR /code

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
    
COPY . .

ENV PORT=80

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]