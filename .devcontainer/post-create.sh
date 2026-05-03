#!/usr/bin/env bash
# Post-create script for GitHub Codespaces.
# Runs once after the dev container is built: installs all dependencies,
# creates the .env file, applies database migrations and imports sample data.

set -euo pipefail

WORKSPACE=/workspace
BACKEND_DIR="$WORKSPACE/backend"
FRONTEND_DIR="$WORKSPACE/frontend"

echo "==> [1/5] Installing Node.js (via nvm) ..."
# The python:3.12 devcontainers image ships with nvm
export NVM_DIR="/usr/local/share/nvm"
# shellcheck source=/dev/null
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 20 --lts 2>/dev/null || true
nvm use 20 2>/dev/null || true

echo "==> [2/5] Installing backend Python dependencies ..."
cd "$BACKEND_DIR"
python -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev]"

echo "==> [3/5] Creating .env file from template ..."
if [ ! -f "$WORKSPACE/.env" ]; then
  cp "$WORKSPACE/.env.example" "$WORKSPACE/.env"
  # Overwrite with Codespaces-friendly values (postgres host = "postgres" service)
  cat > "$WORKSPACE/.env" << 'EOF'
# Generated for GitHub Codespaces – edit freely
POSTGRES_USER=fmc
POSTGRES_PASSWORD=fmc_secret
POSTGRES_DB=findmycaravan

DATABASE_URL=postgresql+asyncpg://fmc:fmc_secret@postgres:5432/findmycaravan
REDIS_URL=redis://redis:6379/0
DEBUG=true
LOG_LEVEL=DEBUG
MAX_UPLOAD_SIZE_MB=10

VITE_API_BASE_URL=http://localhost:8000/api/v1
EOF
  echo "    .env created"
else
  echo "    .env already exists, skipping"
fi

echo "==> [4/5] Running Alembic database migrations ..."
cd "$BACKEND_DIR"
source .venv/bin/activate
# Wait a few seconds for postgres to be fully ready
for i in {1..10}; do
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://fmc:fmc_secret@postgres:5432/findmycaravan'))" 2>/dev/null && break
  echo "    Waiting for PostgreSQL... ($i/10)"
  sleep 3
done
alembic upgrade head
echo "    Migrations applied"

echo "==> [5/5] Installing frontend Node dependencies ..."
cd "$FRONTEND_DIR"
npm install --silent

echo ""
echo "============================================================"
echo "  Find My Caravan dev environment is ready!  🚌"
echo "============================================================"
echo ""
echo "  Start the backend:"
echo "    cd backend && source .venv/bin/activate"
echo "    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  Start the frontend (in a second terminal):"
echo "    cd frontend && npm run dev -- --host 0.0.0.0"
echo ""
echo "  API docs:  http://localhost:8000/docs"
echo "  Frontend:  http://localhost:5173"
echo "  Import sample data: POST http://localhost:8000/api/v1/imports/csv"
echo "    (file: backend/sample_listings.csv)"
echo "============================================================"
