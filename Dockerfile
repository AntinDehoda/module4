# Multi-stage Dockerfile for CrewAI with MCP Sequential Thinking
# Includes both Python and Node.js for MCP server support

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install Node.js (required for npx and MCP servers)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Verify installations
RUN python --version && node --version && npx --version

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download MCP Sequential Thinking server (optional but speeds up first run)
RUN npx -y @modelcontextprotocol/server-sequential-thinking --help || true

# Copy application code
COPY config.py .
COPY parallel_agent_with_mcp.py .
COPY parallel_agent_with_mcp_memory.py .
COPY memory_agent.py .
COPY mcp_examples.py .
COPY README.md .

# Create directory for .env file (will be mounted as volume)
RUN mkdir -p /app/data

# Set environment variable to use .env from mounted volume
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "parallel_agent_with_mcp.py"]
