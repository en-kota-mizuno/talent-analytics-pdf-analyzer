"""
FastAPIサーバー起動スクリプト
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "ta_interview_briefing.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 開発時のみ。本番環境ではFalseに
    )

