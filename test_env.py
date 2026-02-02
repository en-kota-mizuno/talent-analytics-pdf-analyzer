"""
環境変数の設定確認スクリプト
.envファイルが正しく読み込まれているか確認します
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_env():
    """環境変数の設定を確認"""
    print("=" * 50)
    print("環境変数の設定確認")
    print("=" * 50)
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    checks = {
        "AZURE_OPENAI_ENDPOINT": endpoint,
        "AZURE_OPENAI_API_KEY": api_key,
        "AZURE_OPENAI_DEPLOYMENT": deployment,
    }
    
    all_ok = True
    for key, value in checks.items():
        if value:
            # APIキーは一部のみ表示（セキュリティのため）
            if "API_KEY" in key:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"✅ {key}: {display_value}")
        else:
            print(f"❌ {key}: 設定されていません")
            all_ok = False
    
    print("=" * 50)
    if all_ok:
        print("✅ すべての環境変数が正しく設定されています")
    else:
        print("❌ 一部の環境変数が設定されていません")
        print("   .envファイルを確認してください")
    print("=" * 50)
    
    return all_ok

if __name__ == "__main__":
    check_env()

