"""
FastAPIアプリケーション
PDFをアップロードするとブリーフィングPDFを返すAPI
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .azure_client import analyze_ta_pdf_with_azure
from .pdf_builder import generate_interview_pdf_from_azure
from .models import AnalysisResult

app = FastAPI(
    title="Talent Analytics PDF Analyzer API",
    description="Talent Analytics PDFを解析して面接官向けブリーフィングPDFを生成するAPI",
    version="1.0.0"
)

# CORS設定（必要に応じて調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "Talent Analytics PDF Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze": "PDFをアップロードして解析結果をJSONで取得",
            "POST /generate_pdf": "PDFをアップロードしてブリーフィングPDFを生成",
            "GET /health": "ヘルスチェック"
        }
    }


@app.get("/health")
async def health():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_pdf(
    file: UploadFile = File(..., description="Talent Analytics PDFファイル")
):
    """
    PDFをアップロードして解析結果をJSONで返す
    
    Args:
        file: アップロードされたPDFファイル
        
    Returns:
        AnalysisResult: 解析結果（summary, risk_points, attract_points, notes_for_interviewer）
        
    Raises:
        HTTPException: エラーが発生した場合
    """
    # ファイルタイプの確認
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="PDFファイルをアップロードしてください"
        )
    
    tmp_input_path = None
    
    try:
        # 入力PDFを一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            content = await file.read()
            tmp_input.write(content)
            tmp_input_path = tmp_input.name
        
        # PDFを解析
        try:
            analysis = analyze_ta_pdf_with_azure(tmp_input_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF解析に失敗しました: {str(e)}"
            )
        
        # Pydanticモデルに変換して返す
        return AnalysisResult(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"予期しないエラーが発生しました: {str(e)}"
        )
    finally:
        # 一時ファイルをクリーンアップ
        if tmp_input_path and os.path.exists(tmp_input_path):
            try:
                os.unlink(tmp_input_path)
            except Exception:
                pass


@app.post("/generate_pdf")
async def generate_pdf(
    file: UploadFile = File(..., description="Talent Analytics PDFファイル"),
    candidate_name: Optional[str] = Form(default="候補者", description="候補者名")
):
    """
    PDFをアップロードして面接官向けブリーフィングPDFを生成する
    
    Args:
        file: アップロードされたPDFファイル
        candidate_name: 候補者名（オプション、デフォルト: "候補者"）
        
    Returns:
        生成されたブリーフィングPDFファイル
        
    Raises:
        HTTPException: エラーが発生した場合
    """
    # ファイルタイプの確認
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="PDFファイルをアップロードしてください"
        )
    
    # 一時ファイルに保存
    tmp_input_path = None
    tmp_output_path = None
    
    try:
        # 入力PDFを一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_input:
            content = await file.read()
            tmp_input.write(content)
            tmp_input_path = tmp_input.name
        
        # 出力PDFの一時ファイルパス
        output_filename = f"{Path(file.filename).stem}_interview_briefing.pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_output:
            tmp_output_path = tmp_output.name
        
        # PDFを解析
        try:
            analysis = analyze_ta_pdf_with_azure(tmp_input_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF解析に失敗しました: {str(e)}"
            )
        
        # ブリーフィングPDFを生成
        try:
            generate_interview_pdf_from_azure(
                tmp_output_path,
                candidate_name,
                analysis
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF生成に失敗しました: {str(e)}"
            )
        
        # 生成されたPDFを返す
        return FileResponse(
            tmp_output_path,
            media_type="application/pdf",
            filename=output_filename,
            background=None  # レスポンス送信後にファイルを削除
        )
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
    except Exception as e:
        # 予期しないエラー
        raise HTTPException(
            status_code=500,
            detail=f"予期しないエラーが発生しました: {str(e)}"
        )
    finally:
        # 一時ファイルをクリーンアップ
        if tmp_input_path and os.path.exists(tmp_input_path):
            try:
                os.unlink(tmp_input_path)
            except Exception:
                pass
        # 出力ファイルはFileResponseが削除するため、ここでは削除しない

