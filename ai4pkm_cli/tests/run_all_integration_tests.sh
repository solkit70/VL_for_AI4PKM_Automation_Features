#!/bin/bash

# Run All Integration Tests
# This script runs all KTG/KTP/KTE integration tests sequentially with cleanup

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║           KTG/KTP/KTE Integration Test Suite                              ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Change to AI4PKM root directory
cd "$(dirname "$0")/../.."
echo "Working directory: $(pwd)"
echo ""

# Cleanup function
cleanup_before_test() {
    echo "🧹 Cleaning up old test artifacts..."

    # Kill any running watchdog processes
    pkill -f "ai4pkm -t" 2>/dev/null || true
    sleep 2

    # Remove old task files from previous tests
    rm -f "AI/Tasks/2025-10-17"*.md 2>/dev/null || true
    rm -f "Ingest/Clippings/2025-10-17 Test"*.md 2>/dev/null || true
    rm -f "Projects/2025-10-17 Test"*.md 2>/dev/null || true
    rm -f "Ingest/Limitless/2025-10-17-test"*.md 2>/dev/null || true

    # Remove old request files
    rm -f "AI/Tasks/Requests/Clipping/2025-10-17"*.json 2>/dev/null || true
    rm -f "AI/Tasks/Requests/Hashtag/2025-10-17"*.json 2>/dev/null || true
    rm -f "AI/Tasks/Requests/Limitless/2025-10-17"*.json 2>/dev/null || true

    # Remove test logs
    rm -f ai4pkm_cli/tests/watchdog_*.log 2>/dev/null || true

    echo "   ✅ Cleanup complete"
    echo ""
}

# Run single test
run_test() {
    local test_name="$1"
    local test_file="$2"
    local timeout="${3:-180}"  # Default 3 minutes

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Running: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Run test with timeout
    if timeout "$timeout" python "$test_file"; then
        echo ""
        echo "   ✅ $test_name PASSED"
        echo ""
        return 0
    else
        local exit_code=$?
        echo ""
        if [ $exit_code -eq 124 ]; then
            echo "   ⏱️  $test_name TIMEOUT (exceeded ${timeout}s)"
        else
            echo "   ❌ $test_name FAILED (exit code: $exit_code)"
        fi
        echo ""
        return 1
    fi
}

# Track results
total_tests=0
passed_tests=0
failed_tests=()

# Test 1: EIC (Enrich Ingested Content)
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  TEST 1/3: EIC (Enrich Ingested Content) Workflow"
echo "═══════════════════════════════════════════════════════════════════════════"
cleanup_before_test
if run_test "EIC Test" "ai4pkm_cli/tests/test_ktg_ktp_eic_integration.py" 240; then
    ((passed_tests++))
else
    failed_tests+=("EIC Test")
fi
((total_tests++))
sleep 5  # Brief pause between tests

# Test 2: Hashtag (#AI)
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  TEST 2/3: Hashtag (#AI) Workflow"
echo "═══════════════════════════════════════════════════════════════════════════"
cleanup_before_test
if run_test "Hashtag Test" "ai4pkm_cli/tests/test_ktg_ktp_hashtag_integration.py" 240; then
    ((passed_tests++))
else
    failed_tests+=("Hashtag Test")
fi
((total_tests++))
sleep 5  # Brief pause between tests

# Test 3: Limitless ("Hey PKM")
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  TEST 3/3: Limitless (Hey PKM) Workflow"
echo "═══════════════════════════════════════════════════════════════════════════"
cleanup_before_test
if run_test "Limitless Test" "ai4pkm_cli/tests/test_ktg_ktp_limitless_integration.py" 240; then
    ((passed_tests++))
else
    failed_tests+=("Limitless Test")
fi
((total_tests++))

# Final cleanup
cleanup_before_test

# Results Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                        TEST SUITE SUMMARY                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "  Total Tests:  $total_tests"
echo "  Passed:       $passed_tests"
echo "  Failed:       $((total_tests - passed_tests))"
echo ""

if [ ${#failed_tests[@]} -gt 0 ]; then
    echo "  Failed Tests:"
    for test in "${failed_tests[@]}"; do
        echo "    ❌ $test"
    done
    echo ""
    exit 1
else
    echo "  🎉 All tests passed!"
    echo ""
    exit 0
fi
