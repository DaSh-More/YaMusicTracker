FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Указываем переменные окружения (будут доступны в контейнере)
ENV CONFIG_PATH=/app/config.yaml
ENV ym_token=""
ENV PG_URL=""
ENV PG_PORT=5432
ENV PG_USER=yamusictracker
ENV PG_PASSWORD=""
ENV PG_DB=tracks

# Команда для запуска приложения
CMD ["uv", "run", "main.py"]
