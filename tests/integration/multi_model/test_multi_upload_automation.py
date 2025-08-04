#!/usr/bin/env python3
"""
Automated Multi-Upload Testing Suite for FeedMiner
Tests both small and full-size datasets with all 6 AI models
"""

import json
import time
import requests
import sys
from typing import Dict, List, Any, Optional
from decimal import Decimal

# API Configuration
API_BASE_URL = 'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev'

# Test Datasets
SMALL_TEST_DATASET = {
    "type": "instagram_export",
    "user_id": "test-user-automation",
    "exportInfo": {
        "dataTypes": ["saved_posts", "liked_posts"],
        "extractedAt": "2025-08-03T18:33:33.060Z",
        "exportFolder": "meta-2025-Jul-13-19-10-01/instagram-test-automation/"
    },
    "saved_posts": {
        "saved_saved_media": [
            {
                "title": "test_post_1",
                "string_map_data": {
                    "Saved on": {
                        "href": "https://www.instagram.com/reel/TEST1/",
                        "timestamp": 1752408896
                    }
                }
            },
            {
                "title": "test_post_2",
                "string_map_data": {
                    "Saved on": {
                        "href": "https://www.instagram.com/reel/TEST2/",
                        "timestamp": 1752322461
                    }
                }
            }
        ]
    },
    "liked_posts": {
        "likes_media_likes": [
            {
                "title": "test_liked_1",
                "string_map_data": {
                    "Liked on": {
                        "href": "https://www.instagram.com/p/TESTLIKE1/",
                        "timestamp": 1752100000
                    }
                }
            }
        ]
    },
    "dataTypes": ["saved_posts", "liked_posts"]
}

# Model configurations for testing (all 6 models)
TEST_MODELS = [
    # Claude Family
    {
        "id": "claude-sonnet",
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.7,
        "family": "Claude"
    },
    {
        "id": "claude-bedrock",
        "provider": "bedrock",
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "temperature": 0.7,
        "family": "Claude"
    },
    # Nova Family
    {
        "id": "nova-micro",
        "provider": "nova",
        "model": "us.amazon.nova-micro-v1:0",
        "temperature": 0.7,
        "family": "Nova"
    },
    {
        "id": "nova-lite",
        "provider": "nova",
        "model": "us.amazon.nova-lite-v1:0",
        "temperature": 0.7,
        "family": "Nova"
    },
    # Llama Family
    {
        "id": "llama-8b",
        "provider": "llama",
        "model": "meta.llama3-1-8b-instruct-v1:0",
        "temperature": 0.7,
        "family": "Llama"
    },
    {
        "id": "llama-70b",
        "provider": "llama",
        "model": "meta.llama3-1-70b-instruct-v1:0",
        "temperature": 0.7,
        "family": "Llama"
    }
]

class MultiUploadTester:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.test_results = []
        self.full_dataset = None
    
    def load_full_dataset(self) -> Optional[Dict]:
        """Load the full dataset from S3 (downloaded to /tmp/full_dataset.json)"""
        try:
            # Load the real dataset downloaded from S3
            with open('/tmp/full_dataset.json', 'r') as f:
                data = json.load(f)
                
                # Convert from uploaded format to multi-upload format
                saved_posts_data = data.get('content', {}).get('saved_posts', [])
                
                # Create consolidated Instagram export format
                return {
                    "type": "instagram_export",
                    "user_id": "test-user-full-automation",
                    "exportInfo": {
                        "dataTypes": ["saved_posts"],
                        "extractedAt": "2025-08-03T18:33:33.060Z",
                        "exportFolder": "meta-2025-Jul-13-19-10-01/instagram-full-real-data/"
                    },
                    "saved_posts": {
                        "saved_saved_media": [
                            {
                                "title": post.get('author', 'unknown'),
                                "string_map_data": {
                                    "Saved on": {
                                        "href": post.get('url', ''),
                                        "timestamp": int(post.get('saved_at', '2025-01-01T00:00:00+00:00').replace('-', '').replace(':', '').replace('T', '').replace('+00:00', '')[:8])
                                    }
                                }
                            } for post in saved_posts_data[:50]  # Limit to 50 posts for testing
                        ]
                    },
                    "dataTypes": ["saved_posts"]
                }
        except FileNotFoundError:
            print("⚠️  Full dataset file not found at /tmp/full_dataset.json, will skip full dataset tests")
            return None
        except Exception as e:
            print(f"⚠️  Error loading full dataset: {e}")
            return None
    
    def upload_content(self, dataset: Dict, model_config: Dict) -> Dict:
        """Upload content with specific model configuration"""
        payload = dataset.copy()
        payload["modelPreference"] = {
            "provider": model_config["provider"],
            "model": model_config["model"],
            "temperature": model_config["temperature"]
        }
        
        response = requests.post(
            f"{self.base_url}/multi-upload",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "model": model_config,
            "payload_size": len(json.dumps(payload))
        }
    
    def test_small_dataset_all_models(self) -> List[Dict]:
        """Test small dataset with all 6 models"""
        print("🧪 Testing Small Dataset (1-2KB) with All 6 Models...")
        results = []
        
        for model_config in TEST_MODELS:
            print(f"  Testing {model_config['family']} - {model_config['id']}...")
            
            try:
                start_time = time.time()
                result = self.upload_content(SMALL_TEST_DATASET, model_config)
                end_time = time.time()
                
                result["duration_seconds"] = round(end_time - start_time, 2)
                result["test_type"] = "small_dataset"
                results.append(result)
                
                if result["status_code"] == 200:
                    print(f"    ✅ Success ({result['duration_seconds']}s, {result['payload_size']} bytes)")
                    # Extract content ID for potential cleanup
                    if isinstance(result["response"], dict) and "contentId" in result["response"]:
                        result["content_id"] = result["response"]["contentId"]
                else:
                    print(f"    ❌ Failed: {result['status_code']} - {result['response']}")
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
                results.append({
                    "status_code": 0,
                    "response": str(e),
                    "model": model_config,
                    "test_type": "small_dataset",
                    "error": True
                })
        
        return results
    
    def test_full_dataset_selected_models(self) -> List[Dict]:
        """Test full dataset with representative models from each family"""
        if not self.full_dataset:
            print("⚠️  Skipping full dataset tests - no full dataset available")
            return []
        
        print("📊 Testing Full Dataset (300-400KB) with Representative Models...")
        
        # Test with one representative model from each family
        representative_models = [
            next(m for m in TEST_MODELS if m["id"] == "claude-sonnet"),  # Claude
            next(m for m in TEST_MODELS if m["id"] == "nova-micro"),     # Nova (recommended)
            next(m for m in TEST_MODELS if m["id"] == "llama-8b")        # Llama (fastest)
        ]
        
        results = []
        
        for model_config in representative_models:
            print(f"  Testing Full Dataset with {model_config['family']} - {model_config['id']}...")
            
            try:
                start_time = time.time()
                result = self.upload_content(self.full_dataset, model_config)
                end_time = time.time()
                
                result["duration_seconds"] = round(end_time - start_time, 2)
                result["test_type"] = "full_dataset"
                results.append(result)
                
                if result["status_code"] == 200:
                    print(f"    ✅ Success ({result['duration_seconds']}s, {result['payload_size']} bytes)")
                    if isinstance(result["response"], dict) and "contentId" in result["response"]:
                        result["content_id"] = result["response"]["contentId"]
                else:
                    print(f"    ❌ Failed: {result['status_code']} - {result['response']}")
                
                # Longer delay for full dataset tests
                time.sleep(2)
                
            except Exception as e:
                print(f"    ❌ Exception: {str(e)}")
                results.append({
                    "status_code": 0,
                    "response": str(e),
                    "model": model_config,
                    "test_type": "full_dataset",
                    "error": True
                })
        
        return results
    
    def validate_model_preferences(self, content_id: str, expected_model: Dict) -> bool:
        """Validate that model preferences were stored correctly"""
        try:
            response = requests.get(
                f"{self.base_url}/content/{content_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                content_data = response.json()
                stored_model = content_data.get("modelPreference", {})
                
                return (
                    stored_model.get("provider") == expected_model["provider"] and
                    stored_model.get("model") == expected_model["model"] and
                    abs(float(stored_model.get("temperature", 0)) - expected_model["temperature"]) < 0.001
                )
        except Exception as e:
            print(f"    ⚠️  Model preference validation failed: {e}")
        
        return False
    
    def generate_report(self, all_results: List[Dict]) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "test_summary": {
                "total_tests": len(all_results),
                "successful_tests": len([r for r in all_results if r["status_code"] == 200]),
                "failed_tests": len([r for r in all_results if r["status_code"] != 200]),
                "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "small_dataset_results": [r for r in all_results if r.get("test_type") == "small_dataset"],
            "full_dataset_results": [r for r in all_results if r.get("test_type") == "full_dataset"],
            "performance_metrics": {},
            "model_family_success_rates": {}
        }
        
        # Calculate performance metrics
        successful_results = [r for r in all_results if r["status_code"] == 200]
        if successful_results:
            durations = [r["duration_seconds"] for r in successful_results]
            payload_sizes = [r["payload_size"] for r in successful_results]
            
            report["performance_metrics"] = {
                "avg_response_time": round(sum(durations) / len(durations), 2),
                "min_response_time": min(durations),
                "max_response_time": max(durations),
                "avg_payload_size": round(sum(payload_sizes) / len(payload_sizes)),
                "min_payload_size": min(payload_sizes),
                "max_payload_size": max(payload_sizes)
            }
        
        # Calculate success rates by model family
        for family in ["Claude", "Nova", "Llama"]:
            family_results = [r for r in all_results if r.get("model", {}).get("family") == family]
            if family_results:
                successful = len([r for r in family_results if r["status_code"] == 200])
                total = len(family_results)
                report["model_family_success_rates"][family] = {
                    "success_rate": round((successful / total) * 100, 1),
                    "successful": successful,
                    "total": total
                }
        
        return report
    
    def run_comprehensive_tests(self) -> Dict:
        """Run all tests and generate report"""
        print("🚀 Starting Comprehensive Multi-Upload Test Suite")
        print("=" * 60)
        
        # Load full dataset
        self.full_dataset = self.load_full_dataset()
        
        all_results = []
        
        # Test 1: Small dataset with all 6 models
        small_results = self.test_small_dataset_all_models()
        all_results.extend(small_results)
        
        print()
        
        # Test 2: Full dataset with representative models
        full_results = self.test_full_dataset_selected_models()
        all_results.extend(full_results)
        
        print()
        
        # Test 3: Validate model preferences for successful uploads
        print("🔍 Validating Model Preferences Storage...")
        preference_validations = 0
        successful_validations = 0
        
        for result in all_results:
            if result["status_code"] == 200 and "content_id" in result:
                preference_validations += 1
                if self.validate_model_preferences(result["content_id"], result["model"]):
                    successful_validations += 1
                    print(f"    ✅ Model preferences validated for {result['model']['id']}")
                else:
                    print(f"    ❌ Model preferences validation failed for {result['model']['id']}")
        
        print()
        
        # Generate final report
        report = self.generate_report(all_results)
        report["preference_validation"] = {
            "total_validations": preference_validations,
            "successful_validations": successful_validations,
            "validation_rate": round((successful_validations / preference_validations) * 100, 1) if preference_validations > 0 else 0
        }
        
        return report

def print_summary_report(report: Dict):
    """Print a formatted summary report"""
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    summary = report["test_summary"]
    print(f"🕒 Test Timestamp: {summary['test_timestamp']}")
    print(f"📋 Total Tests: {summary['total_tests']}")
    print(f"✅ Successful: {summary['successful_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"📈 Success Rate: {round((summary['successful_tests'] / summary['total_tests']) * 100, 1)}%")
    
    print()
    print("🏃 PERFORMANCE METRICS")
    print("-" * 30)
    if report["performance_metrics"]:
        perf = report["performance_metrics"]
        print(f"Average Response Time: {perf['avg_response_time']}s")
        print(f"Response Time Range: {perf['min_response_time']}s - {perf['max_response_time']}s")
        print(f"Average Payload Size: {perf['avg_payload_size']:,} bytes")
        print(f"Payload Size Range: {perf['min_payload_size']:,} - {perf['max_payload_size']:,} bytes")
    
    print()
    print("🤖 MODEL FAMILY SUCCESS RATES")
    print("-" * 35)
    for family, stats in report["model_family_success_rates"].items():
        print(f"{family}: {stats['success_rate']}% ({stats['successful']}/{stats['total']})")
    
    print()
    print("🔧 MODEL PREFERENCE VALIDATION")
    print("-" * 35)
    pref = report["preference_validation"]
    print(f"Validation Rate: {pref['validation_rate']}% ({pref['successful_validations']}/{pref['total_validations']})")
    
    print()
    print("💾 DETAILED RESULTS")
    print("-" * 20)
    print("Small Dataset Tests:")
    for result in report["small_dataset_results"]:
        status = "✅" if result["status_code"] == 200 else "❌"
        model_name = f"{result['model']['family']} - {result['model']['id']}"
        duration = result.get("duration_seconds", "N/A")
        print(f"  {status} {model_name} ({duration}s)")
    
    if report["full_dataset_results"]:
        print("Full Dataset Tests:")
        for result in report["full_dataset_results"]:
            status = "✅" if result["status_code"] == 200 else "❌"
            model_name = f"{result['model']['family']} - {result['model']['id']}"
            duration = result.get("duration_seconds", "N/A")
            print(f"  {status} {model_name} ({duration}s)")

if __name__ == "__main__":
    try:
        tester = MultiUploadTester()
        report = tester.run_comprehensive_tests()
        
        print()
        print_summary_report(report)
        
        # Save detailed report to file
        with open("multi_upload_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print()
        print("📄 Detailed report saved to: multi_upload_test_report.json")
        
        # Exit with appropriate code
        if report["test_summary"]["failed_tests"] == 0:
            print("🎉 All tests passed!")
            sys.exit(0)
        else:
            print("⚠️  Some tests failed. Check the detailed report.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)