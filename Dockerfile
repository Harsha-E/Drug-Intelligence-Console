FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole repo structure
COPY . .

# Add /app to pythonpath so imports work properly
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=7860

EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
