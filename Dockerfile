FROM python:3.12-slim



RUN mkdir /usr/local/AURORA

COPY src/ /usr/local/AURORA/
RUN pip install --no-cache-dir -r /usr/local/AURORA/requirements.txt
CMD ["python3", "usr/local/AURORA/run.py"]