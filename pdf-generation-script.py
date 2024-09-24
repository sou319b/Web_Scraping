import requests
import re
import csv
from io import StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 明示的に日本語フォントを指定
FONT_PATH = r"C:\Windows\Fonts\msgothic.ttc"

if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('MSGothic', FONT_PATH))
    print(f"フォントを登録しました: {FONT_PATH}")
else:
    print(f"警告: 指定されたフォントファイルが見つかりません: {FONT_PATH}")
    print("システムにインストールされている別の日本語フォントを使用してください。")

def extract_csv_data(url):
    response = requests.get(url)
    response.raise_for_status()
    content = response.text

    csv_match = re.search(r'const rentalItemsCsv = `\n([\s\S]*?)`', content)
    if not csv_match:
        print("CSV data not found in the JavaScript")
        return None

    csv_data = csv_match.group(1)
    print(f"抽出されたCSVデータ（最初の100文字）: {csv_data[:100]}")
    return csv_data

def parse_csv_data(csv_data):
    # CSVデータをUTF-8としてデコード
    csv_data = csv_data.encode('utf-8').decode('utf-8')
    csv_reader = csv.DictReader(StringIO(csv_data))
    items = list(csv_reader)
    
    categorized_items = {}
    for item in items:
        genre = item.get('genre', 'その他')
        if genre not in categorized_items:
            categorized_items[genre] = []
        categorized_items[genre].append(item)
    
    print(f"解析されたアイテム数: {sum(len(items) for items in categorized_items.values())}")
    print("最初の数項目:")
    for genre, items in list(categorized_items.items())[:2]:
        print(f"  ジャンル: {genre}")
        for item in items[:3]:
            print(f"    名前: {item['name']}, 個数: {item.get('quantity', 'N/A')}")
    return categorized_items

def create_pdf(genre, items, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontName='MSGothic',
        fontSize=18,
        leading=22,
        alignment=1  # センター揃え
    )
    
    # タイトル（団体名）を追加
    elements.append(Paragraph(genre, title_style))

    # テーブルデータの作成
    data = [['レンタル品', '個数']]
    for item in items:
        data.append([item['name'], item.get('quantity', 'N/A')])

    # テーブルスタイルの設定
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'MSGothic'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # テーブルの作成と追加
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)

    # PDFの生成
    doc.build(elements)

def main():
    url = "http://sou319b.tplinkdns.com/sou319b/item-list4.html"
    csv_data = extract_csv_data(url)
    
    if csv_data:
        categorized_items = parse_csv_data(csv_data)
        
        for genre, items in categorized_items.items():
            filename = f"{genre}_rental_items.pdf"
            create_pdf(genre, items, filename)
            print(f"PDFを作成しました: {filename}")
        
        print(f"\n作成されたPDFの総数: {len(categorized_items)}")
    else:
        print("ページからCSVデータを抽出できませんでした。")

if __name__ == "__main__":
    main()