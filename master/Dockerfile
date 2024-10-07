FROM python:3.11.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/PY/BIN:$PATH"

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /code/auth-service
COPY requirements.txt /code/auth-service
RUN pip install -r requirements.txt
COPY . /code/auth-service