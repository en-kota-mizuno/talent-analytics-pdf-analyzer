"""
Azure OpenAI クライアント
PDFを解析して面接官向けの情報を抽出する
"""

import os
import json
from typing import Dict, Any
from pathlib import Path
from openai import AzureOpenAI
from PyPDF2 import PdfReader
from dotenv import load_dotenv

from .models import AnalysisResult

load_dotenv()


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDFファイルからテキストを抽出する
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        抽出されたテキスト
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        ValueError: PDFの読み込みに失敗した場合
    """
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDFファイルが見つかりません: {pdf_path}")
    
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text.strip():
                text_parts.append(page_text)
        
        if not text_parts:
            raise ValueError("PDFからテキストを抽出できませんでした。画像のみのPDFの可能性があります。")
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        raise ValueError(f"PDFの読み込みに失敗しました: {e}")


def analyze_ta_pdf_with_azure(pdf_path: str) -> Dict[str, Any]:
    """
    Azure OpenAIを使用してTalent Analytics PDFを解析し、
    面接官向けの情報を抽出する
    
    Args:
        pdf_path: Talent Analytics PDFファイルのパス
        
    Returns:
        解析結果の辞書:
        {
            "summary": str,
            "risk_points": list[str],
            "attract_points": list[str],
            "notes_for_interviewer": list[str]
        }
        
    Raises:
        ValueError: 環境変数が設定されていない場合、またはPDF解析に失敗した場合
    """
    # 環境変数から設定を取得
    # AZURE_OPENAI_ENDPOINT または AZURE_OPENAI_API_ENDPOINT のどちらでも対応
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_OPENAI_API_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    # AZURE_OPENAI_DEPLOYMENT または AZURE_OPENAI_DEPLOYMENT_NAME のどちらでも対応
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    if not endpoint:
        raise ValueError("環境変数 AZURE_OPENAI_ENDPOINT または AZURE_OPENAI_API_ENDPOINT が設定されていません")
    if not api_key:
        raise ValueError("環境変数 AZURE_OPENAI_API_KEY が設定されていません")
    if not deployment:
        raise ValueError("環境変数 AZURE_OPENAI_DEPLOYMENT または AZURE_OPENAI_DEPLOYMENT_NAME が設定されていません")
    
    # エンドポイントの末尾スラッシュを削除
    endpoint_clean = endpoint.rstrip('/')
    
    # Azure OpenAIクライアントを初期化
    # 以前のコードでは base_url を使用していたため、それに合わせる
    client = AzureOpenAI(
        api_key=api_key,
        base_url=endpoint_clean,
        api_version=api_version
    )
    
    # PDFからテキストを抽出
    print(f"PDFを読み込み中: {pdf_path}")
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # テキストが長すぎる場合は切り詰め（トークン制限を考慮）
    # 目安として8000文字程度に制限（実際のトークン数は文字数より多い可能性あり）
    max_text_length = 8000
    if len(pdf_text) > max_text_length:
        print(f"警告: PDFテキストが長いため、最初の{max_text_length}文字のみを使用します")
        pdf_text = pdf_text[:max_text_length]
    
    # PydanticモデルからJSON Schemaを自動生成
    json_schema = AnalysisResult.model_json_schema()
    
    # APIバージョンをチェックしてJSON Schemaが使えるか判定
    api_version_date = api_version.replace("-preview", "").replace("-", "")
    can_use_json_schema = api_version_date >= "20240801" or "2024-08" in api_version
    
    # プロンプトを構築
    if can_use_json_schema:
        # JSON Schemaで形式が保証されるため、簡潔に
        system_prompt = """あなたは人事の専門家です。Talent Analytics（性格・価値観診断）の受検結果レポートを分析し、
面接官向けのブリーフィング情報を提供してください。

重要：
- すべての項目は日本語で記述してください
- risk_points、attract_points、notes_for_interviewerは配列形式で、それぞれ3-5個の項目を提供してください
- 具体的で実用的な内容にしてください
- summaryは200-300文字程度で記述してください
"""
    else:
        # JSON Schemaが使えない場合、プロンプトにJSON形式の例を含める
        system_prompt = """あなたは人事の専門家です。Talent Analytics（性格・価値観診断）の受検結果レポートを分析し、
面接官向けのブリーフィング情報を提供してください。

以下のJSON形式で回答してください。JSON以外の説明やコメントは一切含めないでください。

{
  "summary": "候補者の総合的な特徴の要約（日本語、200-300文字程度）",
  "risk_points": ["見定めポイント（リスク）1", "見定めポイント（リスク）2", "見定めポイント（リスク）3"],
  "attract_points": ["アトラクトポイント（強み）1", "アトラクトポイント（強み）2", "アトラクトポイント（強み）3"],
  "notes_for_interviewer": ["面接官向けの進め方メモ1", "面接官向けの進め方メモ2", "面接官向けの進め方メモ3"]
}

重要：
- すべての項目は日本語で記述してください
- risk_points、attract_points、notes_for_interviewerは配列形式で、それぞれ3-5個の項目を提供してください
- 具体的で実用的な内容にしてください
- 返答はJSON形式のみです（コードブロックやマークダウン記号は使用しないでください）
- JSONの前後に余計なテキストを付けないでください
"""

    user_prompt = f"""以下のTalent Analytics受検結果レポートを分析してください：

{pdf_text}
"""
    
    print("Azure OpenAIにリクエストを送信中...")
    
    try:
        # デバッグ情報を出力
        print(f"エンドポイント: {endpoint_clean}")
        print(f"デプロイメント名: {deployment}")
        print(f"APIバージョン: {api_version}")
        
        # API呼び出しのパラメータを準備
        api_params = {
            "model": deployment,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,  # 一貫性のある出力のため低めの温度設定
            "max_tokens": 2000
        }
        
        # JSON Schemaを使用してレスポンス形式を指定（APIバージョンが対応している場合）
        # 2024-08-01-preview以降でサポート
        if can_use_json_schema:
            try:
                api_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "analysis_result",
                        "schema": json_schema,
                        "strict": True  # スキーマに厳密に従う
                    }
                }
                print("✅ JSON Schemaを使用してリクエストを送信します")
            except Exception as e:
                print(f"⚠️  JSON Schemaの設定に失敗しました（フォールバックモード）: {e}")
                can_use_json_schema = False
        else:
            print(f"⚠️  APIバージョン {api_version} はJSON Schemaに対応していません（2024-08-01-preview以降が必要）")
            print("⚠️  従来のプロンプト方式でリクエストを送信します")
        
        # Azure OpenAI APIを呼び出し
        # JSON Schemaが使えない場合のフォールバック処理
        try:
            response = client.chat.completions.create(**api_params)
        except Exception as api_error:
            # JSON Schema使用時にエラーが発生した場合、JSON Schemaを外して再試行
            if can_use_json_schema and "json_schema" in str(api_error).lower():
                print(f"⚠️  JSON Schemaでエラーが発生しました: {api_error}")
                print("⚠️  JSON Schemaを外して再試行します...")
                # response_formatを削除
                api_params.pop("response_format", None)
                can_use_json_schema = False
                response = client.chat.completions.create(**api_params)
            else:
                raise
        
        # レスポンスからJSON文字列を抽出
        content = response.choices[0].message.content.strip()
        
        # JSON Schemaを使用している場合、通常は純粋なJSONが返ってくる
        # ただし、念のためコードブロックで囲まれている場合を考慮
        if content.startswith("```"):
            lines = content.split("\n")
            # 最初と最後の行（コードブロックのマーカー）を除去
            if len(lines) > 2:
                content = "\n".join(lines[1:-1])
            else:
                content = content.replace("```", "").replace("json", "").strip()
        
        # JSONをパース
        try:
            analysis_result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON解析エラー: {e}")
            print(f"レスポンス内容: {content[:500]}...")  # 最初の500文字のみ表示
            raise ValueError(f"Azure OpenAIからのレスポンスをJSONとして解析できませんでした: {e}")
        
        # Pydanticモデルでバリデーション（型チェックとデータ検証）
        try:
            validated_result = AnalysisResult(**analysis_result)
            print("✅ レスポンスがPydanticモデルで検証されました")
            return validated_result.model_dump()
        except Exception as e:
            print(f"⚠️  Pydanticバリデーションエラー: {e}")
            print("⚠️  生のJSONデータを返します")
            # バリデーションに失敗しても、最低限のチェックは行う
            required_keys = ["summary", "risk_points", "attract_points", "notes_for_interviewer"]
            missing_keys = [key for key in required_keys if key not in analysis_result]
            if missing_keys:
                raise ValueError(f"解析結果に必要なキーが含まれていません: {missing_keys}")
            return analysis_result
        
    except Exception as e:
        if isinstance(e, (ValueError, FileNotFoundError)):
            raise
        raise ValueError(f"Azure OpenAI APIの呼び出しに失敗しました: {e}")

