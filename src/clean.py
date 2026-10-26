"""Module làm sạch và chuẩn hóa dữ liệu bất động sản."""

import json
from pathlib import Path
import sys
from typing import Any, Dict, Tuple
import numpy as np
import pandas as pd

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def clean_house_data(
    raw_file: Path,
    output_csv: Path,
    min_area: float = 10.0,
    max_area: float = 800.0,
    min_price_per_m2: float = 15.0,  # 15 triệu/m2
    max_price_per_m2: float = 600.0,  # 600 triệu/m2
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Làm sạch dữ liệu bất động sản thô:
    1. Kiểm tra cấu trúc cột và kiểu dữ liệu.
    2. Loại bỏ bản ghi thiếu giá bán hoặc diện tích.
    3. Loại bỏ trùng lặp.
    4. Lọc giá trị bất thường (diện tích phi lý, đơn giá/m2 ngoại lai).
    5. Gán 'N/a' cho các ô bị thiếu của các cột còn lại.
    6. Sắp xếp: gia_ban tăng dần, nếu bằng thì dien_tich giảm dần.
    7. Lưu ra file houses.csv với encoding 'utf-8-sig'.
    """
    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    df_raw = pd.DataFrame(data)
    initial_count = len(df_raw)

    log_stats: Dict[str, Any] = {
        "tong_ban_dau": initial_count,
        "thieu_gia_dien_tich": 0,
        "trung_lap": 0,
        "dien_tich_phi_ly": 0,
        "don_gia_ngoai_lai": 0,
        "thieu_quan_huyen": 0,
        "so_luong_sau_lam_sach": 0,
    }

    # 1. Ép kiểu số cho gia_ban và dien_tich
    df = df_raw.copy()
    df["gia_ban"] = pd.to_numeric(df["gia_ban"], errors="coerce")
    df["dien_tich"] = pd.to_numeric(df["dien_tich"], errors="coerce")

    # Loại bỏ bản ghi thiếu giá hoặc diện tích hoặc <= 0
    valid_base = (df["gia_ban"] > 0) & (df["dien_tich"] > 0)
    log_stats["thieu_gia_dien_tich"] = int((~valid_base).sum())
    df = df[valid_base].copy()

    # Loại bỏ bản ghi không có thông tin quận/huyện
    valid_district = df["quan_huyen"].notna() & (df["quan_huyen"].str.strip() != "")
    log_stats["thieu_quan_huyen"] = int((~valid_district).sum())
    df = df[valid_district].copy()

    # 2. Loại bỏ trùng lặp
    dup_cols = ["quan_huyen", "phuong_xa", "duong_pho", "dien_tich", "gia_ban"]
    before_dup = len(df)
    df = df.drop_duplicates(subset=dup_cols, keep="first")
    log_stats["trung_lap"] = before_dup - len(df)

    # 3. Lọc diện tích phi lý
    valid_area = (df["dien_tich"] >= min_area) & (df["dien_tich"] <= max_area)
    log_stats["dien_tich_phi_ly"] = int((~valid_area).sum())
    df = df[valid_area].copy()

    # 4. Lọc đơn giá ngoại lai (triệu VNĐ / m2)
    df["don_gia_m2"] = df["gia_ban"] / df["dien_tich"]
    
    # Tính IQR cho đơn giá
    q1 = df["don_gia_m2"].quantile(0.02)
    q3 = df["don_gia_m2"].quantile(0.98)
    iqr = q3 - q1
    lower_bound = max(min_price_per_m2, q1 - 1.5 * iqr)
    upper_bound = min(max_price_per_m2, q3 + 1.5 * iqr)

    valid_price_m2 = (df["don_gia_m2"] >= lower_bound) & (df["don_gia_m2"] <= upper_bound)
    log_stats["don_gia_ngoai_lai"] = int((~valid_price_m2).sum())
    df = df[valid_price_m2].copy()

    # Xóa cột tạm
    df = df.drop(columns=["don_gia_m2"])
    if "title" in df.columns:
        df = df.drop(columns=["title"])

    # 5. Đảm bảo đúng 9 thuộc tính quy định
    columns_order = [
        "gia_ban",
        "dien_tich",
        "so_phong_ngu",
        "so_phong_tam",
        "quan_huyen",
        "phuong_xa",
        "duong_pho",
        "nam_xay_dung",
        "so_tang",
    ]
    df = df[columns_order]

    # 6. Điền giá trị thiếu bằng trung bình của cùng loại dữ liệu (Mean Imputation)
    # Các cột số: điền bằng trung bình toàn cột; làm tròn về dạng nguyên nếu phù hợp
    numeric_cols = ["so_phong_ngu", "so_phong_tam", "nam_xay_dung", "so_tang"]
    impute_stats: Dict[str, Any] = {}
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        col_mean = df[col].mean()
        missing_count = int(df[col].isna().sum())
        if missing_count > 0 and not np.isnan(col_mean):
            # Làm tròn về số nguyên gần nhất nếu cột là đếm số lượng phòng/tầng
            fill_val = round(col_mean) if col in ("so_phong_ngu", "so_phong_tam", "so_tang") else round(col_mean, 1)
            df[col] = df[col].fillna(fill_val)
            impute_stats[col] = {"so_o_thieu": missing_count, "gia_tri_dien": fill_val}
            print(f"[i] Điền {missing_count} ô thiếu cột '{col}' bằng trung bình = {fill_val}")

    # Các cột chuỗi không bắt buộc (duong_pho): giữ trống nếu thiếu — ghi 'N/a' khi lưu CSV
    log_stats["impute_stats"] = impute_stats

    # 7. Sắp xếp: gia_ban tăng dần, dien_tich giảm dần
    df = df.sort_values(by=["gia_ban", "dien_tich"], ascending=[True, False]).reset_index(drop=True)

    log_stats["so_luong_sau_lam_sach"] = len(df)
    print(f"[*] Thống kê làm sạch: {log_stats}")

    # 8. Chỉ thay 'N/a' cho cột chuỗi bị thiếu (duong_pho) — cột số đã được điền ở trên
    df_csv = df.copy()
    for col in df_csv.columns:
        if df_csv[col].dtype == object:
            df_csv[col] = df_csv[col].apply(lambda x: "N/a" if pd.isna(x) or str(x).strip() in ("", "None", "nan") else x)

    # Lưu UTF-8 with BOM (utf-8-sig)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_csv.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[+] Đã lưu file sạch vào: {output_csv} ({len(df_csv)} dòng)")

    # Lưu log thống kê làm sạch ra JSON để hiển thị trên web và báo cáo
    clean_meta_path = output_csv.parent / "clean_meta.json"
    with open(clean_meta_path, "w", encoding="utf-8") as f:
        json.dump(log_stats, f, ensure_ascii=False, indent=2)

    return df_csv, log_stats


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    raw_path = base_dir / "data" / "raw_houses.json"
    houses_csv = base_dir / "houses.csv"

    if raw_path.exists():
        clean_house_data(raw_path, houses_csv)
    else:
        print(f"[!] Chưa tìm thấy {raw_path}. Vui lòng chạy crawl.py trước.")
