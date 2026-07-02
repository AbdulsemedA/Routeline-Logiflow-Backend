FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
