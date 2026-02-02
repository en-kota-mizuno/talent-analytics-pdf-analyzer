# テストディレクトリ

このディレクトリには、pytestを使用した自動テストが含まれています。

## テストの実行方法

### すべてのテストを実行

```bash
pytest
```

### カバレッジレポート付きで実行

```bash
pytest --cov=ta_interview_briefing --cov-report=html
```

カバレッジレポートは `htmlcov/index.html` で確認できます。

### 特定のテストファイルのみ実行

```bash
pytest tests/test_models.py
```

### マーカーでフィルタリング

```bash
# 単体テストのみ
pytest -m unit

# 統合テストのみ
pytest -m integration

# 環境変数が必要なテストをスキップ
pytest -m "not requires_env"
```

## テストファイルの説明

- `test_models.py`: データモデル（AnalysisResult）のテスト
- `test_azure_client.py`: Azure OpenAIクライアントのテスト（モック使用）
- `test_pdf_builder.py`: PDF生成機能のテスト
- `test_api.py`: FastAPIエンドポイントのテスト

## テストマーカー

- `@pytest.mark.unit`: 単体テスト
- `@pytest.mark.integration`: 統合テスト
- `@pytest.mark.api`: APIテスト
- `@pytest.mark.slow`: 実行に時間がかかるテスト
- `@pytest.mark.requires_env`: 環境変数が必要なテスト

## 注意事項

- 環境変数が必要なテスト（`@pytest.mark.requires_env`）は、`.env`ファイルが設定されている場合のみ実行されます
- Azure OpenAI APIを実際に呼び出すテストは、統合テストとして別途実装することを推奨します

