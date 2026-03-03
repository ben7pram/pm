# syntax=docker/dockerfile:1

# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
# copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
# copy the rest of the frontend source
COPY frontend/ .
# build static site (export is automatic with `output: export`)
RUN npm run build

# Base stage: install Python dependencies
FROM python:3.11-slim AS base

# set working directory
WORKDIR /app

# upgrade pip and install runtime dependencies
RUN pip install --upgrade pip

# install uv for future package management (not required for runtime)
RUN pip install uv

# copy project metadata for reference (not used by pip)
COPY backend/pyproject.toml /app/backend/

# install core dependencies via pip directly
RUN pip install fastapi uvicorn[standard]

# copy the rest of the backend code
COPY backend /app/backend

# copy frontend static export into backend static directory
# Next 16 with `output: export` writes the static HTML into .next/server/app
# and assets into .next/static. We mirror that structure under backend/static.
RUN mkdir -p /app/backend/static
# index.html and related page files
COPY --from=frontend-build /app/frontend/.next/server/app/ /app/backend/static/
# static assets (CSS/JS/fonts/images) should live under _next/static
RUN mkdir -p /app/backend/static/_next/static
COPY --from=frontend-build /app/frontend/.next/static/ /app/backend/static/_next/static/

# final runtime image
FROM base AS runtime
WORKDIR /app/backend

EXPOSE 8000

# default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
