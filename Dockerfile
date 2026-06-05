# Беремо легку офіційну версію Python
FROM python:3.11-slim

# Встановлюємо робочу папку всередині контейнера
WORKDIR /app

# Копіюємо список залежностей
COPY requirements.txt .

# Встановлюємо бібліотеки
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь наш код у контейнер
COPY . .

# Команда для запуску бота
CMD ["python", "main.py"]