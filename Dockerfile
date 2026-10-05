FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for building packages and sqlite
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential libsqlite3-dev \
	&& rm -rf /var/lib/apt/lists/*

# Install runtime Python dependencies
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn[standard] sqlalchemy aiosqlite pydantic

# Copy project
COPY . /app

EXPOSE 8000

# Default command to run the FastAPI app
CMD ["uvicorn", "src.core.main:app", "--host", "0.0.0.0", "--port", "8000"]
