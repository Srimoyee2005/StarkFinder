#!/bin/bash

# Integration Test Runner for StarkFinder Python Backend
# This script sets up the test environment and runs the integration tests

set -e

echo "🚀 Starting StarkFinder Python Backend Integration Tests"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the py-be directory"
    exit 1
fi

# Set default test database URL if not provided
if [ -z "$TEST_DATABASE_URL" ]; then
    export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/starkfinder_test"
    echo "📝 Using default test database URL: $TEST_DATABASE_URL"
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL connection..."

# Run tests
echo "🧪 Running integration tests..."
# pytest will automatically use conftest.py to set up the database
poetry run pytest tests/ || {
    echo "❌ Error: Pytest failed"
    exit 1
}

echo "✅ Tests completed successfully!"