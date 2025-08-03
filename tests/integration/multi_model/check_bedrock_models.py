"""
Check which Bedrock models are available/activated in the current AWS account.
"""

import boto3
import json
from typing import List, Dict

def check_available_models():
    """List all available foundation models in Bedrock."""
    try:
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        
        # List all foundation models
        response = bedrock.list_foundation_models()
        
        models = response.get('modelSummaries', [])
        
        print(f"📊 Found {len(models)} foundation models in us-west-2")
        print("="*60)
        
        # Group by provider
        providers = {}
        for model in models:
            provider = model.get('providerName', 'Unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(model)
        
        # Display by provider
        for provider, provider_models in providers.items():
            print(f"\n🏢 {provider} ({len(provider_models)} models)")
            print("-" * 40)
            
            for model in provider_models:
                model_id = model.get('modelId', 'N/A')
                model_name = model.get('modelName', 'N/A')
                inference_types = model.get('inferenceTypesSupported', [])
                
                print(f"  📋 {model_name}")
                print(f"      ID: {model_id}")
                print(f"      Inference: {', '.join(inference_types)}")
                
                # Check for our target models
                if any(target in model_id for target in ['nova', 'llama3-1']):
                    print(f"      🎯 TARGET MODEL for integration!")
                print()
        
        return models
        
    except Exception as e:
        print(f"❌ Error checking models: {e}")
        return []

def check_specific_models():
    """Check our specific target models."""
    target_models = [
        "us.amazon.nova-micro-v1:0",
        "us.amazon.nova-lite-v1:0", 
        "meta.llama3-1-8b-instruct-v1:0",
        "meta.llama3-1-70b-instruct-v1:0"
    ]
    
    print("\n🎯 CHECKING TARGET MODELS")
    print("="*50)
    
    bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
    
    for model_id in target_models:
        print(f"\n📝 Testing {model_id}...")
        try:
            # Try a simple invoke to see if model is accessible
            response = bedrock_runtime.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": "Hi"}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 10,
                    "temperature": 0.7
                }
            )
            print(f"  ✅ {model_id} - ACCESSIBLE")
            
        except Exception as e:
            error_str = str(e)
            if "AccessDeniedException" in error_str:
                print(f"  ❌ {model_id} - NOT ACTIVATED (need to enable in console)")
            elif "ValidationException" in error_str:
                print(f"  ⚠️  {model_id} - Available but parameter issue")
            else:
                print(f"  ❌ {model_id} - Error: {error_str}")

def check_inference_profiles():
    """Check available inference profiles."""
    try:
        bedrock = boto3.client('bedrock', region_name='us-west-2')
        
        # List inference profiles
        response = bedrock.list_inference_profiles()
        profiles = response.get('inferenceProfileSummaries', [])
        
        print(f"\n🔗 INFERENCE PROFILES ({len(profiles)} found)")
        print("="*50)
        
        for profile in profiles:
            profile_id = profile.get('inferenceProfileId', 'N/A')
            profile_name = profile.get('inferenceProfileName', 'N/A')
            models = profile.get('models', [])
            
            print(f"📋 {profile_name}")
            print(f"    ID: {profile_id}")
            print(f"    Models: {', '.join([m.get('modelId', 'N/A') for m in models])}")
            
            # Check if this profile contains our target models
            for model in models:
                model_id = model.get('modelId', '')
                if any(target in model_id for target in ['nova', 'llama']):
                    print(f"    🎯 Contains target model: {model_id}")
            print()
            
    except Exception as e:
        print(f"❌ Error checking inference profiles: {e}")

if __name__ == "__main__":
    print("🔍 AWS BEDROCK MODEL AVAILABILITY CHECK")
    print("="*50)
    
    # Check all available models
    models = check_available_models()
    
    # Check our specific target models
    check_specific_models()
    
    # Check inference profiles
    check_inference_profiles()
    
    print("\n📋 SUMMARY:")
    print("- Models showing 'NOT ACTIVATED' need to be enabled in AWS Console")
    print("- Go to AWS Bedrock Console → Model access → Request access")
    print("- Nova and Llama models may need special request/approval process")
    print("- After enabling, models should work with our Strands implementation")