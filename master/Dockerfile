FROM python:3.11.6
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
COPY .. /app

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt
