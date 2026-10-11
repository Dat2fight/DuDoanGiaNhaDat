"""Module thu thập dữ liệu bất động sản tại Hà Nội từ alonhadat.com.vn."""

from pathlib import Path
import json
import random
import re
import sys
import time
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
import requests

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_price(price_elem: Optional[Any]) -> Optional[float]:
    """Trích xuất giá bán theo đơn vị triệu VNĐ."""
    if not price_elem:
        return None

    # Ưu tiên lấy từ thuộc tính content (số nguyên VNĐ)
    content = price_elem.get("content")
    if content:
        try:
            val = float(content)
            if val > 0:
                return round(val / 1_000_000, 2)
        except (ValueError, TypeError):
            pass

    text = price_elem.get_text(strip=True).lower()
    text = text.replace(",", ".")
    # Mẫu "x.x tỷ" hoặc "x tỷ"
    ty_match = re.search(r"([\d\.]+)\s*tỷ", text)
    if ty_match:
        try:
            return round(float(ty_match.group(1)) * 1000, 2)
        except ValueError:
            pass

    # Mẫu "x triệu"
    trieu_match = re.search(r"([\d\.]+)\s*triệu", text)
    if trieu_match:
        try:
            return round(float(trieu_match.group(1)), 2)
        except ValueError:
            pass

    return None


def parse_area(area_elem: Optional[Any]) -> Optional[float]:
    """Trích xuất diện tích theo đơn vị m²."""
    if not area_elem:
        return None
    val_elem = area_elem.find("span", attrs={"itemprop": "value"})
    if val_elem:
        try:
            return float(val_elem.get_text(strip=True).replace(",", "."))
        except ValueError:
            pass

    text = area_elem.get_text(strip=True).replace(",", ".")
    m2_match = re.search(r"([\d\.]+)\s*(?:m²|m2)", text)
    if m2_match:
        try:
            return float(m2_match.group(1))
        except ValueError:
            pass
    return None


def parse_district(card: BeautifulSoup) -> Optional[str]:
    """Trích xuất Quận/Huyện từ địa chỉ."""
    old_addr = card.find("p", class_="old-address")
    addr_text = old_addr.get_text(strip=True) if old_addr else ""
    if not addr_text:
        new_addr = card.find("p", class_="new-address")
        addr_text = new_addr.get_text(strip=True) if new_addr else ""

    if addr_text:
        # Tìm các quận huyện quen thuộc tại Hà Nội
        districts = [
            "Ba Đình", "Hoàn Kiếm", "Tây Hồ", "Long Biên", "Cầu Giấy",
            "Đống Đa", "Hai Bà Trưng", "Hoàng Mai", "Thanh Xuân", "Sóc Sơn",
            "Đông Anh", "Gia Lâm", "Nam Từ Liêm", "Thanh Trì", "Bắc Từ Liêm",
            "Mê Linh", "Hà Đông", "Sơn Tây", "Ba Vì", "Phúc Thọ", "Đan Phượng",
            "Hoài Đức", "Quốc Oai", "Thạch Thất", "Chương Mỹ", "Thanh Oai",
            "Thường Tín", "Phú Xuyên", "Ứng Hòa", "Mỹ Đức"
        ]
        for d in districts:
            if re.search(rf"\b(?:Quận|Huyện|Thị xã)?\s*{re.escape(d)}\b", addr_text, re.IGNORECASE):
                return d
    return None


def extract_features_from_brief(brief_text: str) -> Dict[str, Optional[Any]]:
    """Trích xuất phòng tắm, năm xây dựng từ mô tả vắn tắt."""
    res: Dict[str, Optional[Any]] = {"so_phong_tam": None, "nam_xay_dung": None}
    if not brief_text:
        return res

    # Tìm phòng tắm / wc: "3wc", "3 wc", "3 phòng tắm", "3 vệ sinh", "3 toillet"
    wc_match = re.search(r"(\d+)\s*(?:wc|w\.c|phòng tắm|pt|nhà vệ sinh|phòng vệ sinh|vệ sinh)", brief_text, re.IGNORECASE)
    if wc_match:
        try:
            res["so_phong_tam"] = int(wc_match.group(1))
        except ValueError:
            pass

    # Tìm năm xây dựng: "xây năm 2020", "xây 2019", "hoàn thiện 2021"
    year_match = re.search(r"(?:xây\s*(?:năm)?|hoàn thiện\s*(?:năm)?)\s*(20[12]\d|19\d{2})", brief_text, re.IGNORECASE)
    if year_match:
        try:
            res["nam_xay_dung"] = int(year_match.group(1))
        except ValueError:
            pass

    return res


def crawl_hanoi_houses(max_pages: int = 38, delay_range: tuple = (1.2, 2.5)) -> List[Dict[str, Any]]:
    """
    Thu thập danh sách nhà bán tại Hà Nội từ alonhadat.com.vn.
    Tuân thủ robots.txt, User-Agent rõ ràng và sleep ngẫu nhiên.
    """
    base_url = "https://alonhadat.com.vn/can-ban-nha/ha-noi"
    headers = {
        "User-Agent": "HouseInsightBot/1.0 (Student Data Science Project; contact: student@example.edu.vn)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    session = requests.Session()
    session.headers.update(headers)

    records: List[Dict[str, Any]] = []
    print(f"[*] Bắt đầu thu thập dữ liệu bất động sản Hà Nội (tối đa {max_pages} trang)...")

    for page in range(1, max_pages + 1):
        page_url = base_url if page == 1 else f"{base_url}/trang-{page}"
        print(f"[*] Đang tải trang {page}/{max_pages}: {page_url}...")

        retries = 3
        resp = None
        while retries > 0:
            try:
                resp = session.get(page_url, timeout=15)
                if resp.status_code == 200:
                    break
                elif resp.status_code in (403, 429):
                    print(f"[!] Cảnh báo: HTTP {resp.status_code} tại trang {page}. Đợi 5s...")
                    time.sleep(5)
                retries -= 1
            except requests.RequestException as e:
                print(f"[!] Lỗi kết nối tại trang {page}: {e}. Đang thử lại...")
                retries -= 1
                time.sleep(2)

        if not resp or resp.status_code != 200:
            print(f"[X] Không thể tải trang {page}, bỏ qua.")
            continue

        soup = BeautifulSoup(resp.content, "lxml")
        articles = soup.find_all("article", class_="property-item")
        if not articles:
            print(f"[!] Không tìm thấy thẻ bài viết nào tại trang {page}. Kết thúc.")
            break

        for card in articles:
            try:
                # Tiêu đề
                title_elem = card.find("h3", class_="property-title")
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Giá bán
                price_elem = card.find("span", attrs={"itemprop": "offers"})
                if not price_elem:
                    price_elem = card.find("span", class_="price")
                gia_ban = parse_price(price_elem)

                # Diện tích
                area_elem = card.find("span", attrs={"itemprop": "floorSize"})
                if not area_elem:
                    area_elem = card.find("span", class_="area")
                dien_tich = parse_area(area_elem)

                # Số tầng
                floors_elem = card.find("span", class_="floors")
                so_tang = None
                if floors_elem:
                    floor_m = re.search(r"(\d+)\s*tầng", floors_elem.get_text())
                    if floor_m:
                        so_tang = int(floor_m.group(1))

                # Số phòng ngủ
                bedroom_elem = card.find("span", attrs={"itemprop": "numberOfBedrooms"})
                so_phong_ngu = None
                if bedroom_elem:
                    val_b = bedroom_elem.find("span", attrs={"itemprop": "value"})
                    if val_b:
                        try:
                            so_phong_ngu = int(val_b.get_text(strip=True))
                        except ValueError:
                            pass
                    else:
                        bm = re.search(r"(\d+)", bedroom_elem.get_text())
                        if bm:
                            so_phong_ngu = int(bm.group(1))

                # Đường phố, Phường xã
                street_elem = card.find("span", attrs={"itemprop": "streetAddress"})
                duong_pho = street_elem.get_text(strip=True) if street_elem else None

                locality_elem = card.find("span", attrs={"itemprop": "addressLocality"})
                phuong_xa = locality_elem.get_text(strip=True) if locality_elem else None

                # Quận huyện
                quan_huyen = parse_district(card)

                # Mô tả và các thuộc tính phụ
                brief_elem = card.find("p", class_="brief")
                brief_text = brief_elem.get_text(strip=True) if brief_elem else ""
                extra = extract_features_from_brief(brief_text)

                # Nếu trong brief có số tầng hoặc số phòng ngủ mà card chưa có
                if so_phong_ngu is None:
                    pn_match = re.search(r"(\d+)\s*(?:pn|phòng ngủ)", brief_text, re.IGNORECASE)
                    if pn_match:
                        so_phong_ngu = int(pn_match.group(1))

                if so_tang is None:
                    tang_match = re.search(r"(\d+)\s*tầng", brief_text, re.IGNORECASE)
                    if tang_match:
                        so_tang = int(tang_match.group(1))

                record = {
                    "title": title,
                    "gia_ban": gia_ban,
                    "dien_tich": dien_tich,
                    "so_phong_ngu": so_phong_ngu,
                    "so_phong_tam": extra.get("so_phong_tam"),
                    "quan_huyen": quan_huyen,
                    "phuong_xa": phuong_xa,
                    "duong_pho": duong_pho,
                    "nam_xay_dung": extra.get("nam_xay_dung"),
                    "so_tang": so_tang,
                }
                records.append(record)
            except Exception as e:
                continue

        print(f"[*] Trang {page}: Thu thập được {len(articles)} căn (Tổng tích lũy: {len(records)}).")
        sleep_sec = random.uniform(*delay_range)
        time.sleep(sleep_sec)

    print(f"[+] Hoàn tất thu thập: Tổng cộng {len(records)} bản ghi thô.")
    return records


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / "raw_houses.json"

    raw_data = crawl_hanoi_houses(max_pages=36)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print(f"[+] Đã lưu dữ liệu thô vào: {raw_path}")
