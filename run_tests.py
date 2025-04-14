#!/usr/bin/env python3
import unittest
import sys

def run_tests():
    """Run all tests and print results."""
    try:
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.discover('tests')
        
        # Run tests with verbosity
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print("\nTest Summary:")
        print(f"Ran {result.testsRun} tests")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        # Print any failures or errors
        if result.failures:
            print("\nFailures:")
            for failure in result.failures:
                print(f"\n{failure[0]}")
                print(failure[1])
        
        if result.errors:
            print("\nErrors:")
            for error in result.errors:
                print(f"\n{error[0]}")
                print(error[1])
        
        # Return appropriate exit code
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())