"""
ReportLabを使用したPDF生成
面接官向けブリーフィングPDFを生成する
"""

import html
from typing import Dict, Any
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib import colors


def _register_japanese_font():
    """
    日本語フォントを登録する
    ReportLabのCIDFont（HeiseiKakuGo-W5）を使用
    Docker環境では fonts-noto-cjk がインストールされているため利用可能
    """
    font_name = 'HeiseiKakuGo-W5'
    
    # 既に登録されている場合はスキップ
    if font_name in pdfmetrics.getRegisteredFontNames():
        return font_name
    
    # CIDFontを登録（日本語フォントを内蔵）
    pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    print(f"✅ 日本語フォントを登録しました: {font_name}")
    return font_name


def generate_interview_pdf_from_azure(
    output_path: str,
    candidate_name: str,
    analysis: Dict[str, Any]
) -> None:
    """
    Azure OpenAIの解析結果から面接官向けブリーフィングPDFを生成する
    
    Args:
        output_path: 出力PDFファイルのパス
        candidate_name: 候補者名
        analysis: 解析結果の辞書（summary, risk_points, attract_points, notes_for_interviewer）
        
    Raises:
        Exception: PDF生成に失敗した場合
    """
    # 日本語フォントを登録
    japanese_font = _register_japanese_font()
    
    # PDFドキュメントの設定
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # スタイルシートを取得
    styles = getSampleStyleSheet()
    
    # カスタムスタイルを定義
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=japanese_font,
        fontSize=20,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=0  # 左揃え
    )
    
    candidate_style = ParagraphStyle(
        'Candidate',
        parent=styles['BodyText'],
        fontName=japanese_font,
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=10
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=japanese_font,
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName=japanese_font,
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8,
        leading=16,
        alignment=4  # 両端揃え
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['BodyText'],
        fontName=japanese_font,
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        leading=14,
        leftIndent=20,
        firstLineIndent=-10,
        alignment=0  # 左揃えを明示
    )
    
    # ストーリー（PDFの内容）を構築
    elements = []
    
    # タイトル
    elements.append(Paragraph("Talent Analytics 面接ブリーフィング", title_style))
    elements.append(Spacer(1, 5*mm))
    
    # 候補者名
    elements.append(Paragraph(f"候補者名: {candidate_name}", candidate_style))
    elements.append(Spacer(1, 8*mm))
    
    # 【総合特徴】
    elements.append(Paragraph("【総合特徴】", heading_style))
    summary = analysis.get("summary", "")
    if summary:
        elements.append(Paragraph(summary, body_style))
    else:
        elements.append(Paragraph("（情報なし）", body_style))
    elements.append(Spacer(1, 5*mm))
    
    # 【見定めポイント】
    elements.append(Paragraph("【見定めポイント】", heading_style))
    risk_points = analysis.get("risk_points", [])
    if risk_points:
        for point in risk_points:
            # テキストをエスケープして、改行を削除
            clean_point = html.escape(str(point).strip().replace('\n', ' ').replace('\r', ' '))
            clean_point = ' '.join(clean_point.split())
            elements.append(Paragraph(f"・ {clean_point}", bullet_style))
    else:
        elements.append(Paragraph("（情報なし）", body_style))
    elements.append(Spacer(1, 5*mm))
    
    # 【アトラクトポイント】
    elements.append(Paragraph("【アトラクトポイント】", heading_style))
    attract_points = analysis.get("attract_points", [])
    if attract_points:
        for point in attract_points:
            # テキストをエスケープして、改行を削除
            clean_point = html.escape(str(point).strip().replace('\n', ' ').replace('\r', ' '))
            clean_point = ' '.join(clean_point.split())
            elements.append(Paragraph(f"・ {clean_point}", bullet_style))
    else:
        elements.append(Paragraph("（情報なし）", body_style))
    elements.append(Spacer(1, 5*mm))
    
    # 【面接の進め方メモ】
    elements.append(Paragraph("【面接の進め方メモ】", heading_style))
    notes = analysis.get("notes_for_interviewer", [])
    if notes:
        for note in notes:
            # テキストをエスケープして、改行を削除
            clean_note = html.escape(str(note).strip().replace('\n', ' ').replace('\r', ' '))
            # 複数の空白を1つに
            clean_note = ' '.join(clean_note.split())
            elements.append(Paragraph(f"・ {clean_note}", bullet_style))
    else:
        elements.append(Paragraph("（情報なし）", body_style))
    
    # PDFを生成
    doc.build(elements)
    print(f"PDFを生成しました: {output_path}")
