FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY . .

# Install dependencies using uv
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"


# Run the server
CMD ["python", "src/universal_mcp_scraper/server.py"]
