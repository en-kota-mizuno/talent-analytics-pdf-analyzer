"""
PDFテキスト抽出のテストスクリプト
実際にPDFからテキストが抽出できているか確認する
"""

import sys
from pathlib import Path
from ta_interview_briefing.azure_client import extract_text_from_pdf

def test_pdf_extraction(pdf_path: str):
    """PDFからテキストを抽出して表示"""
    try:
        print("=" * 60)
        print(f"PDFファイル: {pdf_path}")
        print("=" * 60)
        
        # テキスト抽出
        text = extract_text_from_pdf(pdf_path)
        
        print(f"\n✅ テキスト抽出成功")
        print(f"抽出された文字数: {len(text)} 文字")
        print(f"抽出された行数: {len(text.splitlines())} 行")
        
        print("\n" + "=" * 60)
        print("抽出されたテキスト（全文字）:")
        print("=" * 60)
        print(text)
        
        # 日本語文字が含まれているか確認
        japanese_chars = [c for c in text if '\u3040' <= c <= '\u309F' or '\u30A0' <= c <= '\u30FF' or '\u4E00' <= c <= '\u9FAF']
        print(f"\n日本語文字数: {len(japanese_chars)} 文字")
        
        if len(japanese_chars) == 0:
            print("⚠️  警告: 日本語文字が検出されませんでした。")
            print("   可能性:")
            print("   - PDFが画像ベース（スキャンPDF）の可能性")
            print("   - フォント埋め込みの問題")
            print("   - PyPDF2の限界")
        
        return text
        
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python test_pdf_extraction.py <PDFファイルのパス>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    test_pdf_extraction(pdf_path)

