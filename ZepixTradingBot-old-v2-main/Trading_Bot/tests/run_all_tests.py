import unittest
import sys
import os
import io

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
try:
    from tests.verify_39_features import TestZepix39Features
except ImportError as e:
    print(f"Error importing tests: {e}")
    sys.exit(1)

def run_suite():
    print("🚀 STARTING MASTER TEST SUITE")
    print("===========================")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add Feature Verification Tests (39/39)
    suite.addTests(loader.loadTestsFromTestCase(TestZepix39Features))
    
    # Run
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate Evidence Log
    with open("FEATURE_TEST_FULL_REPORT.log", "w", encoding="utf-8") as f:
        f.write("ZEPIX TRADING BOT - MASTER TEST SUITE REPORT\n")
        f.write("============================================\n")
        f.write(f"Tests Run: {result.testsRun}\n")
        f.write(f"Errors: {len(result.errors)}\n")
        f.write(f"Failures: {len(result.failures)}\n")
        f.write(f"Status: {'✅ PASSED' if result.wasSuccessful() else '❌ FAILED'}\n\n")
        
        if not result.wasSuccessful():
            f.write("FAILURE DETAILS:\n")
            for failures in result.failures:
                f.write(f"{failures[0]}\n{failures[1]}\n")
            for errors in result.errors:
                f.write(f"{errors[0]}\n{errors[1]}\n")
    
    if result.wasSuccessful():
        print("\n✅ MASTER SUITE PASSED")
        sys.exit(0)
    else:
        print("\n❌ MASTER SUITE FAILED")
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
