# Python bazasidan foydalaning
FROM python:3.12-slim

# Ishchi katalogini yarating
WORKDIR /app

# Talablar faylini va bot kodini yuklang
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]
