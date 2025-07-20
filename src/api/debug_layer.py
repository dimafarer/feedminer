"""
Debug Lambda function to test layer imports.
"""

import json
import sys
import os

def handler(event, context):
    """Debug layer imports."""
    
    debug_info = {
        "python_path": sys.path,
        "environment_vars": dict(os.environ),
        "current_directory": os.getcwd(),
        "layer_test": {}
    }
    
    # Test layer imports
    try:
        import ai
        debug_info["layer_test"]["ai_module"] = "✅ SUCCESS"
        debug_info["layer_test"]["ai_location"] = str(ai.__file__)
    except ImportError as e:
        debug_info["layer_test"]["ai_module"] = f"❌ FAILED: {e}"
    
    try:
        from ai.providers import AIProviderManager
        debug_info["layer_test"]["ai_providers"] = "✅ SUCCESS"
    except ImportError as e:
        debug_info["layer_test"]["ai_providers"] = f"❌ FAILED: {e}"
    
    try:
        import boto3
        debug_info["layer_test"]["boto3"] = "✅ SUCCESS"
    except ImportError as e:
        debug_info["layer_test"]["boto3"] = f"❌ FAILED: {e}"
    
    try:
        import anthropic
        debug_info["layer_test"]["anthropic"] = "✅ SUCCESS"
    except ImportError as e:
        debug_info["layer_test"]["anthropic"] = f"❌ FAILED: {e}"
    
    # Check if /opt directory exists and contents
    opt_contents = []
    if os.path.exists("/opt"):
        for root, dirs, files in os.walk("/opt"):
            for d in dirs:
                opt_contents.append(f"DIR: {os.path.join(root, d)}")
            for f in files[:10]:  # Limit files shown
                opt_contents.append(f"FILE: {os.path.join(root, f)}")
    
    debug_info["opt_contents"] = opt_contents[:50]  # Limit output
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(debug_info, indent=2)
    }