"""
データモデル定義
"""

from typing import List
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """Azure OpenAIによる解析結果のデータモデル"""
    
    summary: str = Field(..., description="候補者の総合的な特徴の要約")
    risk_points: List[str] = Field(..., description="見定めポイント（リスク）のリスト")
    attract_points: List[str] = Field(..., description="アトラクトポイント（強み）のリスト")
    notes_for_interviewer: List[str] = Field(..., description="面接官向けの進め方メモのリスト")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "候補者の総合的な特徴の要約（200-300文字程度）",
                "risk_points": [
                    "見定めポイント（リスク）1",
                    "見定めポイント（リスク）2",
                    "見定めポイント（リスク）3"
                ],
                "attract_points": [
                    "アトラクトポイント（強み）1",
                    "アトラクトポイント（強み）2",
                    "アトラクトポイント（強み）3"
                ],
                "notes_for_interviewer": [
                    "面接官向けの進め方メモ1",
                    "面接官向けの進め方メモ2",
                    "面接官向けの進め方メモ3"
                ]
            }
        }

