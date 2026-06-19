# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# Создаём папку для базы данных (если используешь SQLite)
RUN mkdir -p /app/data

# Открываем порт (если используешь вебхуки, иначе необязательно)
EXPOSE 8000

# Команда запуска бота
CMD ["python", "run.py"]