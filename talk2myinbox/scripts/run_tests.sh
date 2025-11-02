#!/bin/bash

# Test Runner Script for talk2myinbox
# Executes all test suites with proper configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}talk2myinbox Test Suite Runner${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Set test environment
export ENV=test
export EMAIL_MOCK_MODE=true
export CALENDAR_MOCK_MODE=true
export OPENAI_API_KEY=test_key
export ANTHROPIC_API_KEY=test_key
export ELEVENLABS_API_KEY=test_key

# Create necessary directories
mkdir -p backend/tests/logs
mkdir -p backend/tests/coverage

# Function to run tests
run_tests() {
    local test_type=$1
    local test_path=$2
    local marker=$3

    echo -e "${YELLOW}Running ${test_type} tests...${NC}"
    echo ""

    cd backend

    if [ -n "$marker" ]; then
        pytest "$test_path" -v -m "$marker" \
            --cov=voice_agent \
            --cov-report=term-missing \
            --cov-report=html:tests/coverage/html_${test_type} \
            --cov-report=xml:tests/coverage/coverage_${test_type}.xml \
            --junit-xml=tests/coverage/junit_${test_type}.xml \
            --tb=short \
            || test_failed=true
    else
        pytest "$test_path" -v \
            --cov=voice_agent \
            --cov-report=term-missing \
            --cov-report=html:tests/coverage/html_${test_type} \
            --cov-report=xml:tests/coverage/coverage_${test_type}.xml \
            --junit-xml=tests/coverage/junit_${test_type}.xml \
            --tb=short \
            || test_failed=true
    fi

    cd ..

    if [ -n "$test_failed" ]; then
        echo -e "${RED}✗ ${test_type} tests failed${NC}"
        echo ""
        return 1
    else
        echo -e "${GREEN}✓ ${test_type} tests passed${NC}"
        echo ""
        return 0
    fi
}

# Parse arguments
TEST_TYPE="${1:-all}"
SKIP_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-install)
            SKIP_INSTALL=true
            shift
            ;;
        unit|integration|e2e|all|smoke|fast)
            TEST_TYPE=$1
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Install dependencies
if [ "$SKIP_INSTALL" = false ]; then
    echo -e "${YELLOW}Installing test dependencies...${NC}"
    pip install -q pytest pytest-asyncio pytest-cov pytest-xdist pytest-timeout 2>/dev/null || {
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
fi

# Track overall success
OVERALL_SUCCESS=true

# Run tests based on type
case $TEST_TYPE in
    unit)
        run_tests "Unit" "tests/unit/" "unit" || OVERALL_SUCCESS=false
        ;;

    integration)
        run_tests "Integration" "tests/integration/" "integration" || OVERALL_SUCCESS=false
        ;;

    e2e)
        run_tests "E2E" "tests/e2e/" "e2e" || OVERALL_SUCCESS=false
        ;;

    smoke)
        echo -e "${YELLOW}Running smoke tests (critical paths only)...${NC}"
        cd backend
        pytest tests/ -v -m "smoke" --tb=short || OVERALL_SUCCESS=false
        cd ..
        ;;

    fast)
        echo -e "${YELLOW}Running fast tests only...${NC}"
        cd backend
        pytest tests/unit/ -v -m "unit and not slow" --tb=short || OVERALL_SUCCESS=false
        cd ..
        ;;

    all)
        echo -e "${BLUE}Running all test suites...${NC}"
        echo ""

        run_tests "Unit" "tests/unit/" "unit" || OVERALL_SUCCESS=false
        run_tests "Integration" "tests/integration/" "integration" || OVERALL_SUCCESS=false
        run_tests "E2E" "tests/e2e/" "e2e" || OVERALL_SUCCESS=false
        ;;

    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Usage: ./scripts/run_tests.sh [unit|integration|e2e|smoke|fast|all] [--skip-install]"
        exit 1
        ;;
esac

# Generate summary
echo ""
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}Test Results Summary${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Count results
if [ -f backend/tests/coverage/junit_Unit.xml ]; then
    echo -e "Coverage reports generated in: ${GREEN}backend/tests/coverage/${NC}"
    echo ""
fi

if [ "$OVERALL_SUCCESS" = true ]; then
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Check the output above for details.${NC}"
    echo ""
    exit 1
fi
