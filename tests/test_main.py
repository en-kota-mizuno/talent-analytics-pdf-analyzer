"""
CLI（main.py）のテスト
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from ta_interview_briefing.main import main


class TestMain:
    """main関数のテスト"""
    
    @patch('ta_interview_briefing.main.analyze_ta_pdf_with_azure')
    @patch('ta_interview_briefing.main.generate_interview_pdf_from_azure')
    def test_main_success(self, mock_generate, mock_analyze):
        """正常な実行のテスト"""
        # モックの設定
        mock_analyze.return_value = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        
        # 一時PDFファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"%PDF-1.4\n")
            tmp_path = tmp.name
        
        try:
            # sys.argvをモック
            with patch.object(sys, 'argv', ['main.py', tmp_path, '-n', 'テスト候補者']):
                main()
            
            # モックが呼ばれたことを確認
            mock_analyze.assert_called_once()
            mock_generate.assert_called_once()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @patch('ta_interview_briefing.main.analyze_ta_pdf_with_azure')
    @patch('ta_interview_briefing.main.generate_interview_pdf_from_azure')
    def test_main_with_output_path(self, mock_generate, mock_analyze):
        """出力パスを指定した場合のテスト"""
        mock_analyze.return_value = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_input:
            tmp_input.write(b"%PDF-1.4\n")
            input_path = tmp_input.name
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_output:
            output_path = tmp_output.name
            os.unlink(output_path)  # ファイルを削除してから使用
        
        try:
            with patch.object(sys, 'argv', ['main.py', input_path, '-o', output_path, '-n', 'テスト候補者']):
                main()
            
            mock_analyze.assert_called_once()
            mock_generate.assert_called_once()
            # 出力パスが正しく渡されたことを確認
            assert mock_generate.call_args[0][0] == output_path
        finally:
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_main_file_not_found(self):
        """ファイルが見つからない場合のテスト"""
        with patch.object(sys, 'argv', ['main.py', 'nonexistent.pdf']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    @patch('ta_interview_briefing.main.analyze_ta_pdf_with_azure')
    def test_main_analysis_error(self, mock_analyze):
        """解析エラーのテスト"""
        mock_analyze.side_effect = Exception("解析エラー")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"%PDF-1.4\n")
            tmp_path = tmp.name
        
        try:
            with patch.object(sys, 'argv', ['main.py', tmp_path]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @patch('ta_interview_briefing.main.analyze_ta_pdf_with_azure')
    @patch('ta_interview_briefing.main.generate_interview_pdf_from_azure')
    def test_main_generation_error(self, mock_generate, mock_analyze):
        """PDF生成エラーのテスト"""
        mock_analyze.return_value = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        mock_generate.side_effect = Exception("生成エラー")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"%PDF-1.4\n")
            tmp_path = tmp.name
        
        try:
            with patch.object(sys, 'argv', ['main.py', tmp_path]):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    @patch('ta_interview_briefing.main.analyze_ta_pdf_with_azure')
    @patch('ta_interview_briefing.main.generate_interview_pdf_from_azure')
    def test_main_default_candidate_name(self, mock_generate, mock_analyze):
        """候補者名が指定されていない場合のデフォルト値のテスト"""
        mock_analyze.return_value = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b"%PDF-1.4\n")
            tmp_path = tmp.name
        
        try:
            with patch.object(sys, 'argv', ['main.py', tmp_path]):
                main()
            
            # デフォルトの候補者名が使用されたことを確認
            assert mock_generate.call_args[0][1] == "候補者"
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

