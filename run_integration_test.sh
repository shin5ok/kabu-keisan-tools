#!/bin/bash
# Integration test script for kabu-keisan-tools
# This script runs both sample data files through the tool to verify everything works

echo "=== Running integration test with standard Date column ==="
cat tests/examples/sample_data.csv | python main.py

echo -e "\n\n=== Running integration test with Vest Date column ==="
cat tests/examples/sample_vest_data.csv | python main.py

echo -e "\n\n=== All tests completed ==="
