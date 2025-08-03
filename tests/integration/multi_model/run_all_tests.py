#!/usr/bin/env python3
"""
Multi-Model AI Integration Test Suite Runner

Comprehensive test runner for all phases of the Nova/Llama integration.
Runs infrastructure, backend, frontend, and production tests in sequence.
"""

import sys
import os
import subprocess
import time
import argparse
from datetime import datetime
from typing import Dict, List, Tuple

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

class MultiModelTestSuite:
    """Comprehensive test suite for multi-model AI integration."""
    
    def __init__(self, ci_mode: bool = False, verbose: bool = False):
        self.ci_mode = ci_mode
        self.verbose = verbose
        self.test_results = []
        self.start_time = datetime.now()
    
    def run_test_script(self, script_name: str, description: str, timeout: int = 300) -> Tuple[bool, str, float]:
        """Run a test script and return success status, output, and duration."""
        print(f"\n{'='*60}")
        print(f"🧪 {description}")
        print(f"{'='*60}")
        
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        if not os.path.exists(script_path):
            return False, f"Test script not found: {script_path}", 0
        
        try:
            start_time = time.time()
            
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=not self.verbose,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(__file__)
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            output = result.stdout if result.stdout else result.stderr
            
            if self.verbose or not success:
                print(output)
            
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n{status} - {description} ({duration:.1f}s)")
            
            return success, output, duration
            
        except subprocess.TimeoutExpired:
            return False, f"Test timed out after {timeout} seconds", timeout
        except Exception as e:
            return False, f"Test execution error: {str(e)}", 0
    
    def run_infrastructure_tests(self) -> bool:
        """Run infrastructure and availability tests."""
        print(f"\n🏗️  INFRASTRUCTURE TESTS")
        print("="*40)
        
        tests = [
            ("check_bedrock_models.py", "AWS Bedrock Model Availability Check", 60),
        ]
        
        all_passed = True
        for script, description, timeout in tests:
            success, output, duration = self.run_test_script(script, description, timeout)
            self.test_results.append({
                "category": "Infrastructure",
                "test": description,
                "success": success,
                "duration": duration,
                "output": output[:200] if output else ""
            })
            if not success:
                all_passed = False
        
        return all_passed
    
    def run_backend_tests(self) -> bool:
        """Run backend implementation tests."""
        print(f"\n🔧 BACKEND TESTS")
        print("="*40)
        
        tests = [
            ("test_nova_llama_strands.py", "Strands Framework Compatibility", 180),
            ("test_phase2_backend.py", "Backend Implementation Validation", 300),
        ]
        
        all_passed = True
        for script, description, timeout in tests:
            success, output, duration = self.run_test_script(script, description, timeout)
            self.test_results.append({
                "category": "Backend",
                "test": description,
                "success": success,
                "duration": duration,
                "output": output[:200] if output else ""
            })
            if not success:
                all_passed = False
        
        return all_passed
    
    def run_frontend_tests(self) -> bool:
        """Run frontend implementation tests."""
        print(f"\n🎨 FRONTEND TESTS")
        print("="*40)
        
        tests = [
            ("test_frontend_phase3.py", "Frontend Enhancement Validation", 120),
        ]
        
        all_passed = True
        for script, description, timeout in tests:
            success, output, duration = self.run_test_script(script, description, timeout)
            self.test_results.append({
                "category": "Frontend",
                "test": description,
                "success": success,
                "duration": duration,
                "output": output[:200] if output else ""
            })
            if not success:
                all_passed = False
        
        return all_passed
    
    def run_production_tests(self) -> bool:
        """Run production deployment tests."""
        print(f"\n🚀 PRODUCTION TESTS")
        print("="*40)
        
        tests = [
            ("test_production_nova_llama.py", "Production Deployment Validation", 240),
            ("test_optimized_comparison.py", "Optimized Comparison Performance", 120),
        ]
        
        all_passed = True
        for script, description, timeout in tests:
            success, output, duration = self.run_test_script(script, description, timeout)
            self.test_results.append({
                "category": "Production",
                "test": description,
                "success": success,
                "duration": duration,
                "output": output[:200] if output else ""
            })
            if not success:
                all_passed = False
        
        return all_passed
    
    def generate_report(self) -> None:
        """Generate comprehensive test report."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n" + "="*80)
        print(f"📊 MULTI-MODEL AI INTEGRATION TEST REPORT")
        print(f"="*80)
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Test Execution Time: {total_duration:.1f} seconds")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Results by category
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"total": 0, "passed": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["passed"] += 1
        
        print(f"\n📋 Results by Category:")
        for category, stats in categories.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            status = "✅" if rate == 100 else "⚠️" if rate >= 50 else "❌"
            print(f"  {status} {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
        
        # Detailed results
        print(f"\n📝 Detailed Test Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            duration = f"{result['duration']:.1f}s"
            print(f"  {status} {result['test']} ({duration})")
            
            if not result["success"] and result["output"]:
                print(f"      Error: {result['output'][:100]}...")
        
        # Performance summary
        durations = [r["duration"] for r in self.test_results if r["success"]]
        if durations:
            print(f"\n⚡ Performance Summary:")
            print(f"  Average test duration: {sum(durations)/len(durations):.1f}s")
            print(f"  Fastest test: {min(durations):.1f}s")
            print(f"  Slowest test: {max(durations):.1f}s")
        
        # Overall assessment
        print(f"\n🎯 Integration Assessment:")
        if success_rate == 100:
            print(f"  ✅ EXCELLENT: All tests passing - integration fully functional")
            print(f"  🚀 Ready for production use and user adoption")
        elif success_rate >= 80:
            print(f"  ⚠️  GOOD: Most tests passing - minor issues to address")
            print(f"  🔧 Review failed tests and implement fixes")
        elif success_rate >= 50:
            print(f"  ❌ NEEDS WORK: Significant issues found")
            print(f"  🛠️  Major debugging and fixes required")
        else:
            print(f"  🚨 CRITICAL: Integration has serious problems")
            print(f"  🔥 Immediate attention required")
        
        # Recommendations
        if failed_tests > 0:
            print(f"\n💡 Recommendations:")
            failed_categories = [r["category"] for r in self.test_results if not r["success"]]
            unique_failed = set(failed_categories)
            
            for category in unique_failed:
                failed_in_category = [r for r in self.test_results 
                                    if r["category"] == category and not r["success"]]
                print(f"  🔸 {category}: {len(failed_in_category)} test(s) failing")
                for test in failed_in_category[:2]:  # Show first 2 failures
                    print(f"    - {test['test']}")
        
        if success_rate == 100:
            print(f"\n🎉 CONGRATULATIONS!")
            print(f"Multi-model AI integration is complete and fully functional!")
    
    def run_all_tests(self) -> bool:
        """Run the complete test suite."""
        print(f"🚀 MULTI-MODEL AI INTEGRATION TEST SUITE")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {'CI/CD' if self.ci_mode else 'Development'}")
        print(f"Verbose: {self.verbose}")
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Run test categories in sequence
        test_categories = [
            ("Infrastructure", self.run_infrastructure_tests),
            ("Backend", self.run_backend_tests),
            ("Frontend", self.run_frontend_tests),
            ("Production", self.run_production_tests),
        ]
        
        overall_success = True
        for category_name, test_method in test_categories:
            if not test_method():
                overall_success = False
                if self.ci_mode:
                    print(f"❌ {category_name} tests failed in CI mode - stopping execution")
                    break
        
        # Generate report
        self.generate_report()
        
        return overall_success
    
    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are met."""
        print(f"\n🔍 Checking Prerequisites...")
        
        # Check virtual environment
        try:
            import boto3
            print("  ✅ Virtual environment active (boto3 available)")
        except ImportError:
            print("  ❌ Virtual environment not active or boto3 not installed")
            print("     Run: source feedminer-env/bin/activate")
            return False
        
        # Check AWS credentials
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                print("  ✅ AWS credentials configured")
            else:
                print("  ❌ AWS credentials not found")
                return False
        except Exception:
            print("  ❌ AWS credentials check failed")
            return False
        
        # Check Anthropic API key
        anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if anthropic_key:
            print("  ✅ Anthropic API key found")
        else:
            # Try to read from creds file
            try:
                with open('../../../creds/anthropic-apikey', 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2 and lines[1].strip():
                        print("  ✅ Anthropic API key found in creds file")
                    else:
                        print("  ❌ Anthropic API key not found")
                        return False
            except:
                print("  ❌ Anthropic API key not found")
                return False
        
        print("  ✅ All prerequisites met")
        return True

def main():
    """Main test runner entry point."""
    parser = argparse.ArgumentParser(description="Multi-Model AI Integration Test Suite")
    parser.add_argument("--ci-mode", action="store_true", 
                       help="Run in CI/CD mode (stop on first failure)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--category", choices=["infrastructure", "backend", "frontend", "production"],
                       help="Run only specific test category")
    
    args = parser.parse_args()
    
    suite = MultiModelTestSuite(ci_mode=args.ci_mode, verbose=args.verbose)
    
    if args.category:
        # Run specific category
        category_methods = {
            "infrastructure": suite.run_infrastructure_tests,
            "backend": suite.run_backend_tests,
            "frontend": suite.run_frontend_tests,
            "production": suite.run_production_tests,
        }
        
        if not suite.check_prerequisites():
            sys.exit(1)
        
        success = category_methods[args.category]()
        suite.generate_report()
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = suite.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()