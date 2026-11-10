# -----------------------------------------------------------------------------
# Stage 1: Build Next.js Production Bundle
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Final Full-Stack Production Container (Python + Node.js)
# -----------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install Node.js 20 runtime, curl, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Backend Dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# 2. Copy Backend Application Code & Laboratory Datasets
COPY backend/ ./backend/
COPY data/ ./data/

# 3. Copy Built Frontend Application
WORKDIR /app/frontend
COPY --from=frontend-builder /app/frontend/package.json ./package.json
COPY --from=frontend-builder /app/frontend/node_modules ./node_modules
COPY --from=frontend-builder /app/frontend/.next ./.next
COPY --from=frontend-builder /app/frontend/public ./public
COPY --from=frontend-builder /app/frontend/next.config.js ./next.config.js

# 4. Copy Startup Entrypoint Script
WORKDIR /app
COPY docker/entrypoint.sh ./entrypoint.sh
RUN sed -i 's/\r$//' ./entrypoint.sh && chmod +x ./entrypoint.sh

ENV PORT=3000
EXPOSE 3000

# Execute Unified Entrypoint
CMD ["./entrypoint.sh"]
