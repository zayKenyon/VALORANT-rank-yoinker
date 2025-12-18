#!/bin/bash
# Mock System Verification Script
# Run this to verify the mock system is working correctly

echo "=================================================="
echo "VALORANT Rank Yoinker - Mock System Verification"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local command="$2"

    echo -n "Testing $test_name... "

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# Test 1: Check if dependencies are installed
run_test "Dependencies" "python3 -c 'import colr, rich, InquirerPy'"

# Test 2: Check if mock_data.py works
run_test "Mock Data Generator" "python3 -c 'from mock_data import MockDataGenerator; gen = MockDataGenerator(seed=42)'"

# Test 3: Check if mock_requests.py works
run_test "Mock Request Interceptor" "python3 -c 'from mock_requests import MockRequests'"

# Test 4: Test INGAME state
run_test "INGAME State" "python3 run_mock_test.py --state ingame --cycles 1"

# Test 5: Test PREGAME state
run_test "PREGAME State" "python3 run_mock_test.py --state pregame --cycles 1"

# Test 6: Test MENUS state
run_test "MENUS State" "python3 run_mock_test.py --state menus --cycles 1"

# Test 7: Test different scenario
run_test "High ELO Scenario" "python3 run_mock_test.py --scenario high_elo --cycles 1"

# Test 8: Test with specific seed
run_test "Reproducible Seed" "python3 run_mock_test.py --seed 42 --cycles 1"

echo ""
echo "=================================================="
echo "Results:"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "=================================================="

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "Mock system is working correctly."
    echo ""
    echo "Next steps:"
    echo "1. Try: python3 run_mock_test.py --state ingame"
    echo "2. Read: MOCK_TESTING_GUIDE.md for full usage"
    echo "3. Integrate: See mock_integration_patch.py"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed.${NC}"
    echo "Please check the output above for details."
    echo ""
    echo "Troubleshooting:"
    echo "1. Install dependencies: pip3 install -r requirements.txt"
    echo "2. Check you're in project root: pwd"
    echo "3. See: MOCK_TESTING_GUIDE.md#troubleshooting"
    exit 1
fi
