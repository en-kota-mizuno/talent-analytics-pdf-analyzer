"""
Azure OpenAI API接続テストスクリプト
エンドポイント、デプロイメント名、APIキーが正しく動作するか検証します
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()


def test_azure_openai():
    """Azure OpenAI APIの接続をテスト"""
    print("=" * 60)
    print("Azure OpenAI API 接続テスト")
    print("=" * 60)
    
    # 環境変数の取得
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # 環境変数の確認
    print("\n【環境変数の確認】")
    print(f"AZURE_OPENAI_ENDPOINT: {endpoint}")
    print(f"AZURE_OPENAI_API_KEY: {api_key[:10] + '...' if api_key and len(api_key) > 10 else '未設定'}")
    print(f"AZURE_OPENAI_DEPLOYMENT: {deployment}")
    print(f"AZURE_OPENAI_API_VERSION: {api_version}")
    
    # 必須項目のチェック
    if not endpoint:
        print("\n❌ エラー: AZURE_OPENAI_ENDPOINT が設定されていません")
        return False
    
    if not api_key:
        print("\n❌ エラー: AZURE_OPENAI_API_KEY が設定されていません")
        return False
    
    if not deployment:
        print("\n❌ エラー: AZURE_OPENAI_DEPLOYMENT が設定されていません")
        return False
    
    # エンドポイントの末尾スラッシュを削除
    endpoint_clean = endpoint.rstrip('/')
    print(f"\n使用するエンドポイント: {endpoint_clean}")
    
    # Azure OpenAIクライアントの初期化
    print("\n【クライアント初期化】")
    try:
        # base_url を使用（以前のコードに合わせる）
        client = AzureOpenAI(
            api_key=api_key,
            base_url=endpoint_clean,
            api_version=api_version
        )
        print("✅ クライアントの初期化に成功しました")
    except Exception as e:
        print(f"❌ クライアントの初期化に失敗しました: {e}")
        return False
    
    # 簡単なAPI呼び出しテスト
    print("\n【API呼び出しテスト】")
    print("簡単なチャット完了リクエストを送信します...")
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": "こんにちは。簡単に自己紹介してください。"}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        print("✅ API呼び出しに成功しました！")
        print(f"\n【レスポンス】")
        print(f"モデル: {response.model}")
        print(f"使用トークン数: {response.usage.total_tokens if response.usage else 'N/A'}")
        print(f"\n回答内容:")
        print(response.choices[0].message.content)
        
        print("\n" + "=" * 60)
        print("✅ すべてのテストが成功しました！")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ API呼び出しに失敗しました")
        print(f"\n【エラー詳細】")
        print(f"エラータイプ: {type(e).__name__}")
        print(f"エラーメッセージ: {str(e)}")
        
        # エラーの詳細情報を表示
        if hasattr(e, 'status_code'):
            print(f"HTTPステータスコード: {e.status_code}")
        if hasattr(e, 'response'):
            print(f"レスポンス: {e.response}")
        if hasattr(e, 'body'):
            print(f"エラーボディ: {e.body}")
        
        print("\n【トラブルシューティング】")
        print("1. エンドポイントURLが正しいか確認してください")
        print("2. デプロイメント名が正しいか確認してください")
        print("3. APIキーが有効か確認してください")
        print("4. APIバージョンがサポートされているか確認してください")
        print("5. ネットワーク接続を確認してください")
        
        print("\n" + "=" * 60)
        print("❌ テストが失敗しました")
        print("=" * 60)
        return False


if __name__ == "__main__":
    test_azure_openai()

