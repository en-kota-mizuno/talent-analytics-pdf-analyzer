"""
エンドポイントURLのバリエーションテスト
API Management経由の場合、異なるエンドポイント形式を試します
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


def test_endpoint_variation(base_endpoint, deployment, api_key, api_version, variation_name):
    """エンドポイントのバリエーションをテスト"""
    print(f"\n【テスト: {variation_name}】")
    print(f"エンドポイント: {base_endpoint}")
    
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=base_endpoint
        )
        
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "こんにちは"}
            ],
            max_tokens=10
        )
        
        print(f"✅ 成功！レスポンス: {response.choices[0].message.content[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ 失敗: {type(e).__name__}: {str(e)[:100]}")
        return False


def main():
    """メイン関数"""
    print("=" * 60)
    print("エンドポイントURLバリエーションテスト")
    print("=" * 60)
    
    # 環境変数の取得
    original_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip('/')
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not all([original_endpoint, api_key, deployment]):
        print("❌ 環境変数が不足しています")
        return
    
    print(f"\n元のエンドポイント: {original_endpoint}")
    print(f"デプロイメント: {deployment}")
    print(f"APIバージョン: {api_version}")
    
    # テストするエンドポイントのバリエーション
    variations = []
    
    # 元のエンドポイント
    variations.append((original_endpoint, "元のエンドポイント（末尾スラッシュなし）"))
    
    # 末尾にスラッシュを追加
    if not original_endpoint.endswith('/'):
        variations.append((original_endpoint + '/', "末尾スラッシュあり"))
    
    # API Management経由の場合の可能性のある形式
    if 'azure-api.net' in original_endpoint:
        # パスを削除した形式
        base_domain = original_endpoint.split('/ait-takagi-poc')[0]
        variations.append((base_domain, "API Managementベースドメインのみ"))
        
        # openai.azure.com形式に変換を試みる（もし可能なら）
        if 'apim' in original_endpoint:
            print("\n⚠️  API Management経由のエンドポイントが検出されました")
            print("   通常のAzure OpenAIエンドポイント（*.openai.azure.com）を使用することを推奨します")
    
    # 各バリエーションをテスト
    success_count = 0
    for endpoint, name in variations:
        if test_endpoint_variation(endpoint, deployment, api_key, api_version, name):
            success_count += 1
            print(f"\n✅ 動作するエンドポイントが見つかりました: {endpoint}")
            print(f"   .envファイルのAZURE_OPENAI_ENDPOINTをこの値に更新してください")
            break
    
    if success_count == 0:
        print("\n" + "=" * 60)
        print("❌ すべてのエンドポイント形式で失敗しました")
        print("=" * 60)
        print("\n【推奨事項】")
        print("1. Azure Portalで正しいエンドポイントURLを確認してください")
        print("2. API Management経由ではなく、直接Azure OpenAIエンドポイントを使用することを検討してください")
        print("3. デプロイメント名が正しいか確認してください")
        print("4. APIキーが有効か確認してください")


if __name__ == "__main__":
    main()

