"""CLI thực hiện phân cụm K-Means và xuất biểu đồ PCA 2D ra thư mục figures/."""

import argparse
from pathlib import Path
import sys
import pandas as pd

from src.clustering import (
    VALID_FEATURES,
    compute_pca_2d,
    export_cluster_figure,
    prepare_clustering_data,
    run_kmeans,
    summarize_clusters,
)
from src.stats import load_clean_data

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description="Phân cụm dữ liệu nhà ở Hà Nội bằng K-Means và PCA.")
    parser.add_argument(
        "--k",
        type=int,
        required=True,
        help="Số lượng cụm k (yêu cầu k >= 2)",
    )
    parser.add_argument(
        "--features",
        type=str,
        default="gia_ban,dien_tich,so_phong_ngu,so_phong_tam,so_tang",
        help=f"Danh sách đặc trưng phân cách bằng dấu phẩy. Các đặc trưng hợp lệ: {', '.join(VALID_FEATURES)}",
    )
    parser.add_argument(
        "--data",
        type=str,
        default="houses.csv",
        help="Đường dẫn tới file dữ liệu sạch houses.csv (mặc định: houses.csv)",
    )

    args = parser.parse_args()

    # 1. Kiểm tra k >= 2
    if args.k < 2:
        print(f"[!] Lỗi: Số cụm k phải lớn hơn hoặc bằng 2. Giá trị đã nhập: {args.k}")
        sys.exit(1)

    # 2. Kiểm tra tên đặc trưng
    raw_feats = [f.strip() for f in args.features.split(",") if f.strip()]
    invalid_feats = [f for f in raw_feats if f not in VALID_FEATURES]
    if invalid_feats:
        print(f"[!] Lỗi: Tồn tại đặc trưng không hợp lệ: {invalid_feats}")
        print(f"[*] Các đặc trưng hợp lệ là: {', '.join(VALID_FEATURES)}")
        sys.exit(1)

    if len(raw_feats) < 2:
        print("[!] Lỗi: Cần tối thiểu 2 đặc trưng để phân cụm và trực quan hóa PCA.")
        sys.exit(1)

    # 3. Đọc dữ liệu
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / args.data
    if not data_path.exists():
        print(f"[!] Lỗi: Không tìm thấy file dữ liệu tại: {data_path}")
        sys.exit(1)

    df = load_clean_data(data_path)
    print(f"[*] Đã nạp {len(df)} căn nhà từ {data_path.name}")
    print(f"[*] Đặc trưng sử dụng ({len(raw_feats)}): {', '.join(raw_feats)}")
    print(f"[*] Số cụm k = {args.k}")

    # 4. Tiền xử lý dữ liệu và chạy K-Means
    X_scaled, imputer, scaler, df_imputed = prepare_clustering_data(df, raw_feats)
    labels, km = run_kmeans(X_scaled, args.k)

    # 5. Tóm tắt thông tin cụm
    summary_df = summarize_clusters(df, labels, args.k)
    print("\n" + "=" * 65)
    print(" BẢNG MÔ TẢ ĐẶC TRƯNG CÁC CỤM NHÀ Ở")
    print("=" * 65)
    print(summary_df.to_string(index=False))
    print("=" * 65 + "\n")

    # 6. Giảm chiều PCA 2D và xuất biểu đồ
    coords, var_ratios, comment = compute_pca_2d(X_scaled)
    print(f"[*] Tỷ lệ phương sai giải thích: PC1 = {var_ratios[0]*100:.2f}%, PC2 = {var_ratios[1]*100:.2f}%")
    print(f"[*] {comment}")

    fig_path = base_dir / "figures" / f"pca_clusters_k{args.k}.png"
    export_cluster_figure(coords, labels, args.k, var_ratios, fig_path)
    print(f"[+] Hoàn tất! Biểu đồ đã lưu tại: {fig_path}\n")


if __name__ == "__main__":
    main()

