FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY apps/mcp-server/pyproject.toml ./pyproject.toml
COPY apps/mcp-server/careerpilot_mcp ./careerpilot_mcp
RUN pip install --no-cache-dir .

ENV CAREERPILOT_MCP_TRANSPORT=streamable-http
ENV CAREERPILOT_MCP_HOST=0.0.0.0
ENV CAREERPILOT_MCP_PORT=8765
EXPOSE 8765
CMD ["careerpilot-mcp"]
