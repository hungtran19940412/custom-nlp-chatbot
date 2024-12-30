#!/bin/bash
set -e

# Function to wait for a service
wait_for_service() {
    local host="$1"
    local port="$2"
    local service="$3"
    
    echo "Waiting for $service to be ready..."
    while ! nc -z "$host" "$port"; do
        echo "Waiting for $service at $host:$port..."
        sleep 1
    done
    echo "$service is ready!"
}

# Wait for required services
if [ -n "$DATABASE_URL" ]; then
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | cut -d: -f1)
    DB_PORT=$(echo $DATABASE_URL | awk -F[@/] '{print $4}' | cut -d: -f2)
    wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL"
fi

if [ -n "$REDIS_URL" ]; then
    # Extract host and port from REDIS_URL
    REDIS_HOST=$(echo $REDIS_URL | awk -F[@/] '{print $3}' | cut -d: -f1)
    REDIS_PORT=$(echo $REDIS_URL | awk -F[@/] '{print $3}' | cut -d: -f2)
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
fi

# Initialize the database
echo "Running database migrations..."
alembic upgrade head

# Start Prometheus exporter if enabled
if [ "$ENABLE_METRICS" = "true" ]; then
    echo "Starting Prometheus exporter..."
    python -m prometheus_client.exposition --port 9090 &
fi

# Download model if not present
if [ ! -d "/app/models/base_model" ]; then
    echo "Downloading base model..."
    python -c "from transformers import AutoModel; AutoModel.from_pretrained('$MODEL_NAME', cache_dir='/app/models/base_model')"
fi

# Execute the main command
echo "Starting application..."
exec "$@"
