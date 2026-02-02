"""
PDF生成のテスト
"""

import pytest
import os
import tempfile
from pathlib import Path
from ta_interview_briefing.pdf_builder import generate_interview_pdf_from_azure


class TestGenerateInterviewPdfFromAzure:
    """PDF生成のテスト"""
    
    def test_generate_pdf_success(self):
        """PDF生成の成功ケース"""
        analysis = {
            "summary": "テスト候補者の総合的な特徴の説明です。",
            "risk_points": ["リスクポイント1", "リスクポイント2"],
            "attract_points": ["強みポイント1", "強みポイント2"],
            "notes_for_interviewer": ["面接メモ1", "面接メモ2"]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            generate_interview_pdf_from_azure(
                output_path,
                "テスト候補者",
                analysis
            )
            
            # PDFファイルが生成されたか確認
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            # PDFファイルの拡張子を確認
            assert Path(output_path).suffix == '.pdf'
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_pdf_with_empty_lists(self):
        """空のリストを含む解析結果でのPDF生成"""
        analysis = {
            "summary": "テスト",
            "risk_points": [],
            "attract_points": [],
            "notes_for_interviewer": []
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            generate_interview_pdf_from_azure(
                output_path,
                "テスト候補者",
                analysis
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_pdf_with_long_text(self):
        """長文の解析結果でのPDF生成"""
        long_summary = "テスト" * 100  # 長いテキスト
        analysis = {
            "summary": long_summary,
            "risk_points": ["リスク1"] * 10,
            "attract_points": ["強み1"] * 10,
            "notes_for_interviewer": ["メモ1"] * 10
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            generate_interview_pdf_from_azure(
                output_path,
                "テスト候補者",
                analysis
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_generate_pdf_with_special_characters(self):
        """特殊文字を含む候補者名でのPDF生成"""
        analysis = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # 特殊文字を含む候補者名
            candidate_name = "山田 太郎（やまだ たろう）"
            generate_interview_pdf_from_azure(
                output_path,
                candidate_name,
                analysis
            )
            
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

