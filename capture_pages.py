import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
figures_dir = Path("figures")
figures_dir.mkdir(parents=True, exist_ok=True)

pages_to_test = [
    {"url": "http://localhost:8501", "name": "web_home.png", "title": "Trang Chủ"},
    {"url": "http://localhost:8501/Du_lieu", "name": "web_data.png", "title": "Dữ liệu"},
    {"url": "http://localhost:8501/Thong_ke", "name": "web_stats.png", "title": "Thống kê"},
    {"url": "http://localhost:8501/Phan_cum", "name": "web_clustering.png", "title": "Phân cụm"},
    {"url": "http://localhost:8501/Du_doan_gia", "name": "web_predict.png", "title": "Dự đoán giá"},
]

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=chrome_path, headless=True)
    page = browser.new_page(viewport={"width": 1366, "height": 900})
    
    for item in pages_to_test:
        print(f"Opening {item['title']}: {item['url']}...")
        page.goto(item["url"], wait_until="networkidle")
        time.sleep(3) # Đợi Streamlit render hoàn chỉnh
        
        # Nếu là trang dự đoán, thử bấm nút Dự đoán để thấy kết quả
        if "Du_doan_gia" in item["url"]:
            try:
                btn = page.locator("button:has-text('Dự đoán giá ngay')")
                if btn.count() > 0:
                    btn.click()
                    time.sleep(2)
            except Exception as e:
                print(f"Click predict error: {e}")
                
        out_path = figures_dir / item["name"]
        page.screenshot(path=str(out_path), full_page=True)
        print(f"Saved {out_path} (full page)")
        
    browser.close()

print("All screenshots captured successfully!")
