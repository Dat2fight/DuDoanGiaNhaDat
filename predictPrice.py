"""CLI dự đoán giá nhà từ dòng lệnh sử dụng mô hình ML đã huấn luyện."""

import argparse
import json
from pathlib import Path
import sys
import joblib

from src.model import predict_single_house

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    parser = argparse.ArgumentParser(description="Dự đoán giá nhà tại Hà Nội bằng mô hình Machine Learning.")
    parser.add_argument("--area", type=float, required=True, help="Diện tích căn nhà (m²)")
    parser.add_argument("--district", type=str, required=True, help="Quận/Huyện tại Hà Nội")
    parser.add_argument("--ward", type=str, default="Khác", help="Phường/Xã (tùy chọn)")
    parser.add_argument("--bedrooms", type=float, default=3.0, help="Số phòng ngủ (mặc định: 3)")
    parser.add_argument("--bathrooms", type=float, default=2.0, help="Số phòng tắm (mặc định: 2)")
    parser.add_argument("--floors", type=float, default=4.0, help="Số tầng (mặc định: 4)")
    parser.add_argument("--year", type=float, default=2018.0, help="Năm xây dựng (mặc định: 2018)")
    parser.add_argument("--model", type=str, choices=["rf", "lr"], default="rf", help="Mô hình: rf (Random Forest) hoặc lr (Linear Regression)")

    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    models_dir = base_dir / "models"
    model_file = models_dir / ("model_rf.joblib" if args.model == "rf" else "model_lr.joblib")
    metrics_file = models_dir / "metrics.json"

    if not model_file.exists():
        print(f"[!] Lỗi: Chưa tìm thấy file mô hình {model_file}. Vui lòng chạy huấn luyện mô hình trước.")
        sys.exit(1)

    # Nạp mô hình
    model = joblib.load(model_file)
    model_name = "Random Forest" if args.model == "rf" else "Linear Regression"

    rmse = 0.0
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
            rmse = metrics_data.get(model_name, {}).get("test", {}).get("RMSE", 0.0)

    house_info = {
        "dien_tich": args.area,
        "so_phong_ngu": args.bedrooms,
        "so_phong_tam": args.bathrooms,
        "nam_xay_dung": args.year,
        "so_tang": args.floors,
        "quan_huyen": args.district,
        "phuong_xa": args.ward,
    }

    res = predict_single_house(model, house_info, rmse_uncertainty=rmse)

    print("\n" + "=" * 55)
    print(" KẾT QUẢ DỰ ĐOÁN GIÁ BẤT ĐỘNG SẢN")
    print("=" * 55)
    print(f"Mô hình sử dụng : {model_name}")
    print(f"Vị trí          : {args.district} (Phường/Xã: {args.ward})")
    print(f"Diện tích       : {args.area} m² | {args.floors} tầng | {args.bedrooms} PN | {args.bathrooms} PT")
    print("-" * 55)
    print(f"Giá dự đoán     : {res['gia_ty_str']}")
    print(f"Khoảng dao động : {res['khoang_dao_dong_str']}")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()

