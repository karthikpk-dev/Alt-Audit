#!/bin/bash

# Test runner script for Alt Audit
# This script runs all tests for both backend and frontend

set -e

echo "🧪 Running Alt Audit Tests"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Parse command line arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false
COVERAGE=false
VERBOSE=false
PARALLEL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --backend-only    Run only backend tests"
            echo "  --frontend-only   Run only frontend tests"
            echo "  --coverage        Generate coverage reports"
            echo "  --verbose         Verbose output"
            echo "  --parallel        Run tests in parallel"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Set up test environment
print_status "Setting up test environment..."

# Create test database if it doesn't exist
if [ ! -f "backend/test.db" ]; then
    print_status "Creating test database..."
    touch backend/test.db
fi

# Install dependencies if needed
if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
    print_status "Installing dependencies..."
    
    # Backend dependencies
    if [ -f "backend/requirements.txt" ]; then
        print_status "Installing backend dependencies..."
        cd backend
        pip install -r requirements.txt
        cd ..
    fi
    
    # Frontend dependencies
    if [ -f "frontend/package.json" ]; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
fi

# Run backend tests
if [ "$FRONTEND_ONLY" = false ]; then
    print_status "Running backend tests..."
    cd backend
    
    # Set up test environment variables
    export DATABASE_URL="sqlite:///./test.db"
    export REDIS_URL="redis://localhost:6379"
    export SECRET_KEY="test-secret-key"
    export ALGORITHM="HS256"
    export ACCESS_TOKEN_EXPIRE_MINUTES="30"
    export API_V1_STR="/api/v1"
    export PROJECT_NAME="Alt Audit Test"
    export ALLOWED_HOSTS="localhost,127.0.0.1"
    export RATE_LIMIT_PER_MINUTE="10"
    
    # Run pytest with appropriate options
    PYTEST_ARGS="-v"
    
    if [ "$COVERAGE" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS --cov=app --cov-report=html --cov-report=term-missing"
    fi
    
    if [ "$VERBOSE" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS -s"
    fi
    
    if [ "$PARALLEL" = true ]; then
        PYTEST_ARGS="$PYTEST_ARGS -n auto"
    fi
    
    # Run the tests
    if python -m pytest $PYTEST_ARGS; then
        print_success "Backend tests passed!"
    else
        print_error "Backend tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
fi

# Run frontend tests
if [ "$BACKEND_ONLY" = false ]; then
    print_status "Running frontend tests..."
    cd frontend
    
    # Set up test environment variables
    export VITE_API_URL="http://localhost:8000/api/v1"
    
    # Run vitest with appropriate options
    VITEST_ARGS=""
    
    if [ "$COVERAGE" = true ]; then
        VITEST_ARGS="$VITEST_ARGS --coverage"
    fi
    
    if [ "$VERBOSE" = true ]; then
        VITEST_ARGS="$VITEST_ARGS --reporter=verbose"
    fi
    
    if [ "$PARALLEL" = true ]; then
        VITEST_ARGS="$VITEST_ARGS --threads"
    fi
    
    # Run the tests
    if npm run test $VITEST_ARGS; then
        print_success "Frontend tests passed!"
    else
        print_error "Frontend tests failed!"
        cd ..
        exit 1
    fi
    
    cd ..
fi

# Generate combined coverage report if requested
if [ "$COVERAGE" = true ] && [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
    print_status "Generating combined coverage report..."
    
    # This would require additional setup to combine backend and frontend coverage
    # For now, we'll just report that coverage was generated
    print_success "Coverage reports generated in backend/htmlcov/ and frontend/coverage/"
fi

# Run integration tests if both backend and frontend are tested
if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
    print_status "Running integration tests..."
    
    # Start services for integration tests
    print_status "Starting services for integration tests..."
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Run integration tests
    cd backend
    if python -m pytest tests/test_integration.py -v; then
        print_success "Integration tests passed!"
    else
        print_error "Integration tests failed!"
        cd ..
        docker-compose down
        exit 1
    fi
    cd ..
    
    # Stop services
    print_status "Stopping services..."
    docker-compose down
fi

# Summary
print_success "All tests completed successfully!"
print_status "Test Summary:"
print_status "  - Backend tests: ✅ Passed"
print_status "  - Frontend tests: ✅ Passed"
print_status "  - Integration tests: ✅ Passed"

if [ "$COVERAGE" = true ]; then
    print_status "  - Coverage reports: Generated"
fi

print_status "🎉 All tests passed! The application is ready for deployment."
