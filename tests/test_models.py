"""
データモデルのテスト
"""

import pytest
from ta_interview_briefing.models import AnalysisResult


class TestAnalysisResult:
    """AnalysisResultモデルのテスト"""
    
    def test_valid_analysis_result(self):
        """有効な解析結果の作成"""
        data = {
            "summary": "テスト候補者の総合的な特徴",
            "risk_points": ["リスク1", "リスク2"],
            "attract_points": ["強み1", "強み2"],
            "notes_for_interviewer": ["メモ1", "メモ2"]
        }
        result = AnalysisResult(**data)
        
        assert result.summary == data["summary"]
        assert result.risk_points == data["risk_points"]
        assert result.attract_points == data["attract_points"]
        assert result.notes_for_interviewer == data["notes_for_interviewer"]
    
    def test_missing_required_fields(self):
        """必須フィールドが欠けている場合のエラー"""
        with pytest.raises(Exception):  # pydanticのValidationError
            AnalysisResult(
                summary="テスト",
                # risk_pointsが欠けている
                attract_points=["強み1"],
                notes_for_interviewer=["メモ1"]
            )
    
    def test_empty_lists(self):
        """空のリストが許可されるか"""
        data = {
            "summary": "テスト",
            "risk_points": [],
            "attract_points": [],
            "notes_for_interviewer": []
        }
        result = AnalysisResult(**data)
        
        assert result.risk_points == []
        assert result.attract_points == []
        assert result.notes_for_interviewer == []
    
    def test_json_serialization(self):
        """JSONシリアライゼーションのテスト"""
        data = {
            "summary": "テスト",
            "risk_points": ["リスク1"],
            "attract_points": ["強み1"],
            "notes_for_interviewer": ["メモ1"]
        }
        result = AnalysisResult(**data)
        json_data = result.model_dump()
        
        assert json_data["summary"] == data["summary"]
        assert json_data["risk_points"] == data["risk_points"]
        assert isinstance(json_data, dict)

