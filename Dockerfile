# Base image Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project
COPY . .

# Buat folder untuk data dan logs
RUN mkdir -p data logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE 8000

# Buat start.sh executable
RUN chmod +x start.sh

# Run the bot
CMD ["./start.sh"]

CMD ["python", "-m", "src.main"]
