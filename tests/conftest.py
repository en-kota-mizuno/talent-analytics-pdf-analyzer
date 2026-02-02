"""
pytestの共通設定とフィクスチャ
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def sample_pdf_path():
    """サンプルPDFファイルのパス（ダミー）"""
    # 実際のPDFファイルではなく、ダミーファイルを作成
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(b"%PDF-1.4\n")
        tmp_path = tmp.name
    
    yield tmp_path
    
    # クリーンアップ
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture
def sample_analysis_data():
    """サンプルの解析結果データ"""
    return {
        "summary": "テスト候補者の総合的な特徴の説明です。",
        "risk_points": ["リスクポイント1", "リスクポイント2"],
        "attract_points": ["強みポイント1", "強みポイント2"],
        "notes_for_interviewer": ["面接メモ1", "面接メモ2"]
    }


@pytest.fixture
def temp_output_path():
    """一時的な出力ファイルパス"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp_path = tmp.name
    
    yield tmp_path
    
    # クリーンアップ
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@pytest.fixture(autouse=True)
def reset_env():
    """テスト前後で環境変数をリセット（必要に応じて）"""
    # テスト前の環境変数を保存
    original_env = os.environ.copy()
    
    yield
    
    # テスト後の環境変数を復元
    os.environ.clear()
    os.environ.update(original_env)

