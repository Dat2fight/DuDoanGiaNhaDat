"""Module tính toán thống kê mô tả, so sánh khu vực và phân tích phân bố."""

from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# Cấu hình font tiếng Việt và giao diện cho Matplotlib
plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


NUMERIC_COLS_MAP = {
    "gia_ban": "Giá",
    "dien_tich": "Diện tích",
    "so_phong_ngu": "Phòng ngủ",
    "so_phong_tam": "Phòng tắm",
    "nam_xay_dung": "Năm xây dựng",
    "so_tang": "Số tầng",
}


def load_clean_data(houses_csv: Path) -> pd.DataFrame:
    """Đọc dữ liệu sạch houses.csv, chuyển 'N/a' thành NaN và ép kiểu số."""
    df = pd.read_csv(houses_csv, na_values=["N/a", "na", "NaN", ""], encoding="utf-8-sig")
    for col in NUMERIC_COLS_MAP.keys():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def calculate_descriptive_stats(df: pd.DataFrame, group_col: str = "quan_huyen") -> pd.DataFrame:
    """
    Tính Mean, Median, Std cho từng thuộc tính số:
    - Toàn bộ dữ liệu (dòng 0 là 'all').
    - Từng khu vực (các dòng sau).
    Tạo các cột theo mẫu:
    'Mean của Giá', 'Median của Giá', 'Std của Giá', ...
    """
    numeric_cols = list(NUMERIC_COLS_MAP.keys())

    def get_stats_for_subset(sub_df: pd.DataFrame) -> Dict[str, float]:
        row_dict: Dict[str, float] = {}
        for col, col_name in NUMERIC_COLS_MAP.items():
            s = sub_df[col].dropna()
            mean_val = round(float(s.mean()), 2) if len(s) > 0 else np.nan
            median_val = round(float(s.median()), 2) if len(s) > 0 else np.nan
            std_val = round(float(s.std()), 2) if len(s) > 1 else (0.0 if len(s) == 1 else np.nan)

            row_dict[f"Mean của {col_name}"] = mean_val
            row_dict[f"Median của {col_name}"] = median_val
            row_dict[f"Std của {col_name}"] = std_val
        return row_dict

    # 1. Dòng 'all'
    all_stats = get_stats_for_subset(df)
    rows: List[Dict[str, Any]] = [{"Khu vực": "all", **all_stats}]

    # 2. Từng khu vực
    districts = sorted(df[group_col].dropna().unique())
    for dist in districts:
        dist_df = df[df[group_col] == dist]
        dist_stats = get_stats_for_subset(dist_df)
        rows.append({"Khu vực": dist, **dist_stats})

    res_df = pd.DataFrame(rows)
    return res_df


def save_results2_csv(df: pd.DataFrame, output_csv: Path) -> pd.DataFrame:
    """Tính và lưu file results2.csv theo đúng đặc tả."""
    stats_df = calculate_descriptive_stats(df)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    stats_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[+] Đã lưu results2.csv vào: {output_csv}")
    return stats_df


def get_top_cheapest_and_most_expensive(df: pd.DataFrame, n: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Lấy top n căn rẻ nhất và đắt nhất."""
    cols_display = ["quan_huyen", "phuong_xa", "duong_pho", "dien_tich", "gia_ban"]
    cheapest = df.nsmallest(n, "gia_ban")[cols_display].copy()
    most_expensive = df.nlargest(n, "gia_ban")[cols_display].copy()
    return cheapest, most_expensive


def compare_districts(df: pd.DataFrame, min_samples: int = 5) -> Tuple[pd.DataFrame, str, str]:
    """
    So sánh giá trung bình và giá/m2 giữa các quận huyện có >= min_samples căn.
    Trả về DataFrame thống kê, quận đắt nhất và rẻ nhất.
    """
    df_calc = df.dropna(subset=["gia_ban", "dien_tich", "quan_huyen"]).copy()
    df_calc["don_gia_m2"] = df_calc["gia_ban"] / df_calc["dien_tich"]

    district_counts = df_calc["quan_huyen"].value_counts()
    valid_districts = district_counts[district_counts >= min_samples].index

    filtered = df_calc[df_calc["quan_huyen"].isin(valid_districts)]

    summary = (
        filtered.groupby("quan_huyen")
        .agg(
            so_can=("gia_ban", "count"),
            gia_tb=("gia_ban", "mean"),
            gia_median=("gia_ban", "median"),
            don_gia_tb=("don_gia_m2", "mean"),
            don_gia_median=("don_gia_m2", "median"),
        )
        .reset_index()
    )

    summary["gia_tb_ty"] = (summary["gia_tb"] / 1000).round(2)
    summary["don_gia_tb"] = summary["don_gia_tb"].round(2)
    summary = summary.sort_values(by="don_gia_tb", ascending=False).reset_index(drop=True)

    most_expensive_dist = str(summary.iloc[0]["quan_huyen"])
    cheapest_dist = str(summary.iloc[-1]["quan_huyen"])

    return summary, most_expensive_dist, cheapest_dist


def analyze_distribution(series: pd.Series) -> Dict[str, Any]:
    """Phân tích hình dạng phân bố: skewness, ngoại lai, nhận xét."""
    s = series.dropna()
    if len(s) == 0:
        return {"skewness": 0, "outliers_count": 0, "comment": "Không đủ dữ liệu"}

    skew = round(float(s.skew()), 2)
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = int(((s < lower) | (s > upper)).sum())

    comment = ""
    if skew > 1.0:
        comment = f"Phân bố lệch phải mạnh (skewness = {skew} > 1.0), phần lớn giá trị tập trung ở phân khúc thấp/trung bình, có một số bất động sản ngoại lai giá trị cao kéo dài đuôi bên phải."
    elif skew > 0.5:
        comment = f"Phân bố lệch phải vừa phải (skewness = {skew}), xu hướng bất động sản giá cao xuất hiện nhưng không quá cực đoan."
    elif skew < -0.5:
        comment = f"Phân bố lệch trái (skewness = {skew}), tập trung nhiều hơn ở phân khúc trên."
    else:
        comment = f"Phân bố tương đối đối xứng quanh giá trị trung tâm (skewness = {skew})."

    if outliers > 0:
        comment += f" Phát hiện {outliers} điểm ngoại lai (nằm ngoài khoảng [{lower:.1f}, {upper:.1f}])."
    else:
        comment += " Không có điểm ngoại lai đáng kể theo tiêu chuẩn IQR."

    return {
        "skewness": skew,
        "outliers_count": outliers,
        "comment": comment,
        "q1": q1,
        "q3": q3,
        "median": float(s.median()),
        "mean": float(s.mean()),
    }


def export_figures(df: pd.DataFrame, figures_dir: Path) -> None:
    """Xuất các biểu đồ phân tích tĩnh chất lượng cao ra figures/ phục vụ báo cáo."""
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. So sánh khu vực
    summary, _, _ = compare_districts(df, min_samples=5)
    plt.figure(figsize=(10, 5))
    x = np.arange(len(summary))
    width = 0.35

    plt.bar(x - width / 2, summary["don_gia_tb"], width, label="Đơn giá TB (triệu/m²)", color="#2563eb")
    plt.bar(x + width / 2, summary["gia_tb_ty"] * 10, width, label="Giá TB (x100 triệu VNĐ)", color="#f97316")

    plt.xlabel("Quận / Huyện", fontweight="bold")
    plt.ylabel("Giá trị", fontweight="bold")
    plt.title("So sánh Đơn giá và Giá trung bình theo khu vực tại Hà Nội", fontsize=13, fontweight="bold")
    plt.xticks(x, summary["quan_huyen"], rotation=35, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "bar_comparison.png", dpi=300)
    plt.close()

    # 2. Boxplot giá theo khu vực
    df_calc = df.dropna(subset=["gia_ban", "quan_huyen"]).copy()
    top_dists = summary["quan_huyen"].tolist()[:8]
    box_data = [df_calc[df_calc["quan_huyen"] == d]["gia_ban"] / 1000 for d in top_dists]

    plt.figure(figsize=(11, 5))
    plt.boxplot(box_data, tick_labels=top_dists, patch_artist=True, boxprops=dict(facecolor="#93c5fd", color="#1d4ed8"))
    plt.xlabel("Quận / Huyện", fontweight="bold")
    plt.ylabel("Giá bán (tỷ VNĐ)", fontweight="bold")
    plt.title("Phân bố Giá bán (Boxplot) theo các khu vực tiêu biểu tại Hà Nội", fontsize=13, fontweight="bold")
    plt.xticks(rotation=25)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "boxplot_price.png", dpi=300)
    plt.close()

    # 3. Histogram giá
    plt.figure(figsize=(8, 4.5))
    prices_ty = df["gia_ban"].dropna() / 1000
    plt.hist(prices_ty, bins=30, color="#3b82f6", edgecolor="#1e3a8a", alpha=0.8)
    plt.title("Phân bố Giá bán toàn bộ dữ liệu (tỷ VNĐ)", fontsize=12, fontweight="bold")
    plt.xlabel("Giá bán (tỷ VNĐ)")
    plt.ylabel("Số lượng căn nhà")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "hist_price.png", dpi=300)
    plt.close()

    # 4. Histogram diện tích
    plt.figure(figsize=(8, 4.5))
    areas = df["dien_tich"].dropna()
    plt.hist(areas, bins=30, color="#10b981", edgecolor="#065f46", alpha=0.8)
    plt.title("Phân bố Diện tích toàn bộ dữ liệu (m²)", fontsize=12, fontweight="bold")
    plt.xlabel("Diện tích (m²)")
    plt.ylabel("Số lượng căn nhà")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "hist_area.png", dpi=300)
    plt.close()

    print(f"[+] Đã xuất toàn bộ biểu đồ thống kê ra thư mục: {figures_dir}")


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    houses_csv = base_dir / "houses.csv"
    results2_csv = base_dir / "results2.csv"
    figures_dir = base_dir / "figures"

    if not houses_csv.exists():
        print(f"[!] Lỗi: Chưa tìm thấy {houses_csv}")
        sys.exit(1)

    df_clean = load_clean_data(houses_csv)
    save_results2_csv(df_clean, results2_csv)
    export_figures(df_clean, figures_dir)
