# PDFテキスト抽出について

## 現在の実装（PyPDF2）

### ✅ 動作確認済み
- Talent Analytics PDFから**3,766文字**（日本語2,878文字）を正常に抽出
- テキストベースのPDFには有効

### ⚠️ PyPDF2の限界

1. **画像ベースのPDF（スキャンPDF）**
   - テキスト抽出不可
   - OCR（光学文字認識）が必要

2. **複雑なレイアウト**
   - テキストの順序が正しくない場合がある
   - 表や複数カラムの処理が苦手

3. **フォント埋め込みの問題**
   - 一部のフォントで文字化けする可能性
   - 特殊なエンコーディングに対応できない場合がある

4. **パフォーマンス**
   - 大きなPDFファイルで処理が遅い
   - メモリ使用量が多い

## より良い代替手段

### 1. pdfplumber（推奨）
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
```

**メリット:**
- 表の抽出に強い
- レイアウト情報を保持
- テキストの位置情報も取得可能

**デメリット:**
- PyPDF2よりやや重い

### 2. PyMuPDF (fitz)
```python
import fitz  # PyMuPDF

doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text()
```

**メリット:**
- 非常に高速
- 画像抽出も可能
- レンダリング機能あり

**デメリット:**
- インストールがやや複雑（Cライブラリ依存）

### 3. Azure OpenAI Vision API（画像ベースPDF用）
- PDFを画像に変換してVision APIに送信
- OCR機能が内蔵されている
- ただし、コストが高い

## 推奨される改善

### オプション1: pdfplumberに切り替え（簡単）
```bash
pip install pdfplumber
```

### オプション2: フォールバック機能を追加
PyPDF2で失敗した場合、pdfplumberを試す

### オプション3: ハイブリッド方式
- まずPyPDF2を試す（軽量）
- 失敗したらpdfplumberを試す
- それでも失敗したらエラーを返す

## 現在の実装で十分な場合

Talent Analytics PDFが**テキストベース**で、**レイアウトが比較的シンプル**な場合は、現在のPyPDF2実装で十分です。

実際のテスト結果：
- ✅ 正常にテキスト抽出できている
- ✅ 日本語も正しく抽出されている
- ✅ Azure OpenAIでの解析も成功している

## 判断基準

以下の場合は現在の実装で問題ありません：
- PDFがテキストベース（画像スキャンではない）
- レイアウトが比較的シンプル
- 表が複雑でない

以下の場合は改善を検討：
- スキャンPDF（画像のみ）
- 複雑な表やレイアウト
- テキスト抽出が不完全
- パフォーマンスが問題

