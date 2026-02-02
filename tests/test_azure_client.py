"""
Azure OpenAIクライアントのテスト
"""

import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ta_interview_briefing.azure_client import extract_text_from_pdf, analyze_ta_pdf_with_azure


class TestExtractTextFromPdf:
    """PDFテキスト抽出のテスト"""
    
    def test_file_not_found(self):
        """存在しないファイルの場合のエラー"""
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("nonexistent.pdf")
    
    @patch('ta_interview_briefing.azure_client.PdfReader')
    def test_extract_text_success(self, mock_pdf_reader):
        """テキスト抽出の成功ケース"""
        # モックの設定
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "ページ1のテキスト"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "ページ2のテキスト"
        
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        # 一時ファイルを作成
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = extract_text_from_pdf(tmp_path)
            assert "ページ1のテキスト" in result
            assert "ページ2のテキスト" in result
        finally:
            # クリーンアップ
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @patch('ta_interview_briefing.azure_client.PdfReader')
    def test_extract_text_empty(self, mock_pdf_reader):
        """テキストが抽出できない場合のエラー"""
        mock_reader = MagicMock()
        mock_reader.pages = []
        mock_pdf_reader.return_value = mock_reader
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="PDFからテキストを抽出できませんでした"):
                extract_text_from_pdf(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


class TestAnalyzeTaPdfWithAzure:
    """Azure OpenAIによるPDF解析のテスト"""
    
    @pytest.mark.requires_env
    def test_missing_env_variables(self):
        """環境変数が設定されていない場合のエラー"""
        # 環境変数を一時的に削除
        original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
        original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)
        
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(b"dummy pdf content")
            
            try:
                with pytest.raises(ValueError, match="環境変数が設定されていません"):
                    analyze_ta_pdf_with_azure(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        finally:
            # 環境変数を復元
            if original_endpoint:
                os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint
            if original_key:
                os.environ["AZURE_OPENAI_API_KEY"] = original_key
    
    @patch('ta_interview_briefing.azure_client.extract_text_from_pdf')
    @patch('ta_interview_briefing.azure_client.AzureOpenAI')
    def test_analyze_pdf_success(self, mock_azure_client, mock_extract_text):
        """PDF解析の成功ケース（モック使用）"""
        # 環境変数を設定
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o"
        
        # モックの設定
        mock_extract_text.return_value = "サンプルPDFテキスト"
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"summary": "テスト", "risk_points": ["リスク1"], "attract_points": ["強み1"], "notes_for_interviewer": ["メモ1"]}'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_client.return_value = mock_client
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = analyze_ta_pdf_with_azure(tmp_path)
            
            assert "summary" in result
            assert "risk_points" in result
            assert "attract_points" in result
            assert "notes_for_interviewer" in result
            assert isinstance(result["risk_points"], list)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
            # 環境変数をクリーンアップ
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
            os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)
    
    @patch('ta_interview_briefing.azure_client.extract_text_from_pdf')
    @patch('ta_interview_briefing.azure_client.AzureOpenAI')
    def test_analyze_pdf_long_text_truncation(self, mock_azure_client, mock_extract_text):
        """長いテキストの切り詰め処理のテスト"""
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o"
        
        # 長いテキストを生成（8000文字を超える）
        long_text = "テスト" * 3000  # 約9000文字
        mock_extract_text.return_value = long_text
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"summary": "テスト", "risk_points": ["リスク1"], "attract_points": ["強み1"], "notes_for_interviewer": ["メモ1"]}'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_client.return_value = mock_client
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = analyze_ta_pdf_with_azure(tmp_path)
            # API呼び出し時にテキストが切り詰められたことを確認
            call_args = mock_client.chat.completions.create.call_args
            user_message = call_args[1]["messages"][1]["content"]
            assert len(user_message) <= 8000 + 100  # 少し余裕を持たせる
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
            os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)
    
    @patch('ta_interview_briefing.azure_client.extract_text_from_pdf')
    @patch('ta_interview_briefing.azure_client.AzureOpenAI')
    def test_analyze_pdf_with_json_schema(self, mock_azure_client, mock_extract_text):
        """JSON Schemaを使用する場合のテスト"""
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o"
        os.environ["AZURE_OPENAI_API_VERSION"] = "2024-08-01-preview"
        
        mock_extract_text.return_value = "サンプルPDFテキスト"
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"summary": "テスト", "risk_points": ["リスク1"], "attract_points": ["強み1"], "notes_for_interviewer": ["メモ1"]}'
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_client.return_value = mock_client
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            result = analyze_ta_pdf_with_azure(tmp_path)
            # JSON Schemaが使用されたことを確認
            call_args = mock_client.chat.completions.create.call_args
            assert "response_format" in call_args[1]
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
            os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)
            os.environ.pop("AZURE_OPENAI_API_VERSION", None)
    
    @patch('ta_interview_briefing.azure_client.extract_text_from_pdf')
    @patch('ta_interview_briefing.azure_client.AzureOpenAI')
    def test_analyze_pdf_json_parse_error(self, mock_azure_client, mock_extract_text):
        """JSON解析エラーのテスト"""
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o"
        
        mock_extract_text.return_value = "サンプルPDFテキスト"
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "これは有効なJSONではありません"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_client.return_value = mock_client
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="JSONとして解析できませんでした"):
                analyze_ta_pdf_with_azure(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
            os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)
    
    @patch('ta_interview_briefing.azure_client.extract_text_from_pdf')
    @patch('ta_interview_briefing.azure_client.AzureOpenAI')
    def test_analyze_pdf_api_error(self, mock_azure_client, mock_extract_text):
        """API呼び出しエラーのテスト"""
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
        os.environ["AZURE_OPENAI_API_KEY"] = "test-key"
        os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "gpt-4o"
        
        mock_extract_text.return_value = "サンプルPDFテキスト"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("APIエラー")
        mock_azure_client.return_value = mock_client
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with pytest.raises(ValueError, match="Azure OpenAI APIの呼び出しに失敗しました"):
                analyze_ta_pdf_with_azure(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
            os.environ.pop("AZURE_OPENAI_API_KEY", None)
            os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)

