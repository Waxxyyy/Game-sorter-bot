# Используем официальный образ Python 3.9
FROM python:3.10

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы вашего проекта
COPY . .

# Экспортируем порт, который будет использоваться Flask-приложением
EXPOSE 8000

# Запускаем Flask-приложение
CMD ["python", "main.py"]
