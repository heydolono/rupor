FROM python:3.8-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV HF_HOME=/app/.cache/huggingface
RUN mkdir -p /app/.cache/huggingface && chmod -R 777 /app/.cache
CMD ["gunicorn", "ruporblog.wsgi:application", "--bind", "0:8000", "--reload", "--timeout", "120"]