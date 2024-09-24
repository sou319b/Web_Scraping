import requests
import re
import csv
from io import StringIO

def extract_csv_data(url):
    response = requests.get(url)
    response.raise_for_status()
    content = response.text

    # CSVデータを含む文字列を正規表現で抽出
    csv_match = re.search(r'const rentalItemsCsv = `\n([\s\S]*?)`', content)
    if not csv_match:
        print("CSV data not found in the JavaScript")
        return None

    csv_data = csv_match.group(1)
    return csv_data

def parse_csv_data(csv_data):
    # CSVデータをUTF-8としてデコード
    csv_data = csv_data.encode('utf-8').decode('utf-8')
    
    csv_reader = csv.DictReader(StringIO(csv_data))
    items = list(csv_reader)
    
    # ジャンルごとにアイテムを分類
    categorized_items = {}
    for item in items:
        genre = item.get('genre', 'その他')  # ジャンル情報がない場合は'その他'とする
        if genre not in categorized_items:
            categorized_items[genre] = []
        categorized_items[genre].append(item)
    
    return categorized_items

def main():
    url = "http://sou319b.tplinkdns.com/sou319b/item-list4.html"
    csv_data = extract_csv_data(url)
    
    if csv_data:
        categorized_items = parse_csv_data(csv_data)
        
        print("Extracted Rental Items:")
        for genre, items in categorized_items.items():
            print(f"\nGenre: {genre}")
            for item in items:
                if item['name'] and item['price']:  # Noneのアイテムをスキップ
                    print(f"  Name: {item['name']}, Price: {item['price']}")
        
        print(f"\nTotal number of items: {sum(len(items) for items in categorized_items.values())}")
    else:
        print("Failed to extract CSV data from the page.")

if __name__ == "__main__":
    main()