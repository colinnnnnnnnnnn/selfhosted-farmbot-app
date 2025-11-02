
FROM python:3.13-slim


# Set the working directory in the container
WORKDIR /app

# Install dependencies

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt


COPY . .

EXPOSE 8000


CMD ["python", "run.py"]
