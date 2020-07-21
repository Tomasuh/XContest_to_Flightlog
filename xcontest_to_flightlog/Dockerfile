FROM python:3

COPY . /app
RUN chmod +x /app/gpsdump.64bit.0.28
RUN chmod 555 /app/gpsdump.64bit.0.28

RUN pip install -r /app/requirements.txt

CMD ["python", "-u", "/app/run.py"]