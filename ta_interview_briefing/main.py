"""
CLI実行用のエントリーポイント
"""

import sys
import argparse
from pathlib import Path

from .azure_client import analyze_ta_pdf_with_azure
from .pdf_builder import generate_interview_pdf_from_azure


def main():
    """
    コマンドラインから実行されるメイン関数
    """
    parser = argparse.ArgumentParser(
        description="Talent Analytics PDFを解析して面接官向けブリーフィングPDFを生成"
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        help="入力となるTalent Analytics PDFファイルのパス"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="出力PDFファイルのパス（指定しない場合は入力ファイル名に基づいて自動生成）"
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        default="候補者",
        help="候補者名（デフォルト: 候補者）"
    )
    
    args = parser.parse_args()
    
    # 入力ファイルの存在確認
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}")
        sys.exit(1)
    
    # 出力ファイルパスの決定
    if args.output:
        output_path = Path(args.output)
    else:
        # 入力ファイル名から候補者IDを抽出（例: candidate_123.pdf -> candidate_123）
        candidate_id = pdf_path.stem
        output_path = pdf_path.parent / f"{candidate_id}_interview_briefing.pdf"
    
    try:
        # PDFを解析
        print("=" * 50)
        print("Talent Analytics PDF解析を開始します...")
        print("=" * 50)
        analysis = analyze_ta_pdf_with_azure(str(pdf_path))
        
        # ブリーフィングPDFを生成
        print("=" * 50)
        print("ブリーフィングPDFを生成します...")
        print("=" * 50)
        generate_interview_pdf_from_azure(
            str(output_path),
            args.name,
            analysis
        )
        
        print("=" * 50)
        print("処理が完了しました！")
        print(f"出力ファイル: {output_path}")
        print("=" * 50)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

