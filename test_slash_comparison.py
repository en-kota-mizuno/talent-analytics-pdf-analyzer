"""
スラッシュの有無とazure_endpoint vs base_urlの違いをテスト
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip('/')
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

print("=" * 60)
print("スラッシュの有無とパラメータ名の違いをテスト")
print("=" * 60)

# テストケース
test_cases = [
    ("azure_endpoint (スラッシュなし)", endpoint, "azure_endpoint"),
    ("azure_endpoint (スラッシュあり)", endpoint + "/", "azure_endpoint"),
    ("base_url (スラッシュなし)", endpoint, "base_url"),
    ("base_url (スラッシュあり)", endpoint + "/", "base_url"),
]

for name, test_endpoint, param_name in test_cases:
    print(f"\n【テスト: {name}】")
    print(f"エンドポイント: {test_endpoint}")
    
    try:
        if param_name == "azure_endpoint":
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=test_endpoint.rstrip('/')
            )
        else:  # base_url
            client = AzureOpenAI(
                api_key=api_key,
                base_url=test_endpoint.rstrip('/'),
                api_version=api_version
            )
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "こんにちは"}],
            max_tokens=10
        )
        
        print(f"✅ 成功！")
        
    except Exception as e:
        print(f"❌ 失敗: {type(e).__name__}: {str(e)[:80]}")

