# Imagen base oficial de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y el código fuente
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Puerto expuesto
EXPOSE 5000

# Comando para correr Flask usando Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
