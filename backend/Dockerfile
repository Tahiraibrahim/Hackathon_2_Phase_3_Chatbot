# 1. Python ka base image (Foundation)
FROM python:3.12

# 2. Folder set karein
WORKDIR /app

# 3. Requirements copy aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Sara code copy karein
COPY . .

# 5. Database permission (Zaroori hai taake SQLite error na de)
RUN chmod -R 777 /app

# 6. App start karein (Port 7860 Hugging Face ka standard hai)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]