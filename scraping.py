import requests
from bs4 import BeautifulSoup
import chardet

def scrape_rental_items_from_url(url):
    print(f"Fetching content from URL: {url}")
    response = requests.get(url)
    response.raise_for_status()
    
    # コンテンツのエンコーディングを検出
    raw_content = response.content
    detected_encoding = chardet.detect(raw_content)['encoding']
    print(f"Detected encoding: {detected_encoding}")

    # 検出されたエンコーディングでデコード
    html_content = raw_content.decode(detected_encoding)
    print(f"Total content length: {len(html_content)} characters")

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # ページ構造の分析
    analyze_page_structure(soup)
    
    # ジャンルとアイテムの検索
    genres = soup.select('.genre-buttons button') or soup.select('.genre-button')
    print(f"Found {len(genres)} genres")
    
    all_items = []
    
    for genre in genres:
        genre_name = genre.text.strip()
        print(f"Processing genre: {genre_name}")
        
        # 複数の可能性のあるコンテナ構造を試す
        genre_containers = [
            soup.find('div', id=f"{genre_name}-items"),
            soup.find('div', {'data-genre': genre_name}),
            soup.find('div', class_=f"{genre_name.lower()}-items")
        ]
        
        genre_container = next((container for container in genre_containers if container), None)
        
        if genre_container:
            items = genre_container.find_all('div', class_='item')
            print(f"Found {len(items)} items in {genre_name}")
            
            for item in items:
                item_name = item.find(['h3', 'div'], class_='item-name')
                item_quantity = item.find(['span', 'div'], class_='item-quantity')
                
                if item_name and item_quantity:
                    name = item_name.text.strip()
                    quantity = ''.join(filter(str.isdigit, item_quantity.text.strip()))
                    
                    all_items.append({
                        'genre': genre_name,
                        'name': name,
                        'quantity': int(quantity) if quantity else 0
                    })
                    print(f"Added item: {name} (Quantity: {quantity})")
                else:
                    print(f"Warning: Incomplete item data found in {genre_name}")
        else:
            print(f"Warning: No container found for genre {genre_name}")
    
    return all_items

def analyze_page_structure(soup):
    print("\nAnalyzing page structure:")
    print(f"Title: {soup.title.string if soup.title else 'No title found'}")
    print(f"Number of <div> tags: {len(soup.find_all('div'))}")
    print(f"Number of <script> tags: {len(soup.find_all('script'))}")
    print(f"Number of <style> tags: {len(soup.find_all('style'))}")
    
    main_content = soup.find('main') or soup.find('div', id='main-content') or soup.find('div', class_='container')
    if main_content:
        print(f"Main content container found with {len(main_content.find_all())} child elements")
    else:
        print("No main content container found")
    
    # JavaScriptコードの分析
    scripts = soup.find_all('script')
    for i, script in enumerate(scripts):
        print(f"\nAnalyzing <script> tag {i+1}:")
        print(script.string[:100] if script.string else "No inline script")

url = "http://sou319b.tplinkdns.com/sou319b/item-list4.html"
try:
    print("Starting scraping process...")
    rental_items = scrape_rental_items_from_url(url)

    print(f"\nTotal items found: {len(rental_items)}")
    for item in rental_items:
        print(f"団体: {item['genre']}, 品名: {item['name']}, 個数: {item['quantity']}")

    if len(rental_items) == 0:
        print("\nNo items found. Saving full HTML content for debugging:")
        with open('debug_output.html', 'w', encoding='utf-8') as f:
            f.write(requests.get(url).content.decode('utf-8'))
        print("Full HTML content has been saved to 'debug_output.html'")

except requests.RequestException as e:
    print(f"エラーが発生しました: {e}")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {e}")

print("Script execution completed.")