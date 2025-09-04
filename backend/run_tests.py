#!/usr/bin/env python3
"""
Test runner script for MMDB project
Run all unit tests with coverage reporting
"""
import unittest
import sys
import os
from io import StringIO

def run_tests():
    """Run all unit tests and display results"""
    
    # Add current directory to path for imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print("="*70)
    print("MMDB PROJECT UNIT TEST RESULTS")
    print("="*70)
    print(stream.getvalue())
    
    # Summary
    print("\nTEST SUMMARY:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

def run_specific_test(test_file):
    """Run a specific test file"""
    if not test_file.startswith('test_'):
        test_file = f'test_{test_file}'
    if not test_file.endswith('.py'):
        test_file = f'{test_file}.py'
    
    print(f"Running specific test: {test_file}")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_file.replace('.py', ''))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test file
        success = run_specific_test(sys.argv[1])
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)
