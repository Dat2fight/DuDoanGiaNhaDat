"""Module huấn luyện, đánh giá và dự đoán giá bất động sản với Linear Regression và Random Forest."""

import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

base_project_dir = Path(__file__).resolve().parent.parent
if str(base_project_dir) not in sys.path:
    sys.path.insert(0, str(base_project_dir))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.stats import load_clean_data

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


NUMERIC_FEATURES = [
    "dien_tich",
    "so_phong_ngu",
    "so_phong_tam",
    "nam_xay_dung",
    "so_tang",
]

CATEGORICAL_FEATURES = [
    "quan_huyen",
    "phuong_xa",
]

TARGET = "gia_ban"


def build_preprocessor() -> ColumnTransformer:
    """Xây dựng bộ tiền xử lý với ColumnTransformer (Imputer + Scaler / OneHotEncoder)."""
    num_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Khác")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERIC_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
        ]
    )
    return preprocessor


def train_and_evaluate_models(
    df: pd.DataFrame, models_dir: Path, figures_dir: Path
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Huấn luyện Linear Regression và Random Forest:
    - Chia 80% train / 20% test (random_state=42).
    - Đánh giá MAE, RMSE, R² trên cả Train và Test để nhận xét overfitting.
    - Lưu pipeline vào models/*.joblib và metrics.json.
    - Xuất biểu đồ Top đặc trưng quan trọng vào figures/.
    """
    models_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. Chuẩn bị tập dữ liệu X, y
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    y = df[TARGET].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"[*] Tập huấn luyện: {len(X_train)} mẫu; Tập kiểm thử: {len(X_test)} mẫu.")

    # 2. Định nghĩa 2 Pipeline
    preprocessor = build_preprocessor()

    pipe_lr = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", LinearRegression()),
        ]
    )

    pipe_rf = Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100, max_depth=12, random_state=42, n_jobs=-1
                ),
            ),
        ]
    )

    # 3. Huấn luyện và đánh giá từng mô hình
    metrics: Dict[str, Any] = {}
    fitted_models = {"Linear Regression": pipe_lr, "Random Forest": pipe_rf}

    for name, pipe in fitted_models.items():
        print(f"[*] Đang huấn luyện {name}...")
        pipe.fit(X_train, y_train)

        # Dự đoán
        y_train_pred = pipe.predict(X_train)
        y_test_pred = pipe.predict(X_test)

        # Tính toán độ đo
        mae_train = float(mean_absolute_error(y_train, y_train_pred))
        rmse_train = float(np.sqrt(mean_squared_error(y_train, y_train_pred)))
        r2_train = float(r2_score(y_train, y_train_pred))

        mae_test = float(mean_absolute_error(y_test, y_test_pred))
        rmse_test = float(np.sqrt(mean_squared_error(y_test, y_test_pred)))
        r2_test = float(r2_score(y_test, y_test_pred))

        metrics[name] = {
            "train": {
                "MAE": round(mae_train, 2),
                "RMSE": round(rmse_train, 2),
                "R2": round(r2_train, 3),
            },
            "test": {
                "MAE": round(mae_test, 2),
                "RMSE": round(rmse_test, 2),
                "R2": round(r2_test, 3),
            },
        }

    # 4. Trích xuất Feature Importance từ Random Forest
    rf_regressor = pipe_rf.named_steps["regressor"]
    rf_prep = pipe_rf.named_steps["preprocessor"]

    feature_names = []
    # Thuộc tính số
    feature_names.extend(NUMERIC_FEATURES)
    # Thuộc tính One-hot
    cat_encoder = rf_prep.named_transformers_["cat"].named_steps["onehot"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES)
    feature_names.extend(cat_names.tolist())

    importances = rf_regressor.feature_importances_
    fi_df = pd.DataFrame({"feature": feature_names, "importance": importances})
    fi_df = fi_df.sort_values(by="importance", ascending=False).reset_index(drop=True)

    # Gộp tên hiển thị thân thiện
    label_map = {
        "dien_tich": "Diện tích (m²)",
        "so_phong_ngu": "Phòng ngủ",
        "so_phong_tam": "Phòng tắm",
        "nam_xay_dung": "Năm xây dựng",
        "so_tang": "Số tầng",
    }
    fi_df["display_name"] = fi_df["feature"].apply(
        lambda f: label_map.get(
            f, f.replace("quan_huyen_", "Quận ").replace("phuong_xa_", "Phường ")
        )
    )

    top_fi = fi_df.head(10).to_dict(orient="records")
    metrics["top_features_rf"] = top_fi

    # Nhận xét yếu tố ảnh hưởng lớn nhất
    top_factor = top_fi[0]["display_name"]
    top_score = top_fi[0]["importance"] * 100
    second_factor = top_fi[1]["display_name"]
    comment_fi = (
        f"'{top_factor}' là yếu tố ảnh hưởng mạnh nhất đến giá bán nhà (chiếm {top_score:.1f}% mức độ quan trọng), "
        f"tiếp theo là '{second_factor}'. Vị trí quận/huyện và quy mô công trình đóng vai trò quyết định trong việc định giá."
    )
    metrics["importance_comment"] = comment_fi

    # 5. Lưu mô hình và metrics
    joblib.dump(pipe_lr, models_dir / "model_lr.joblib")
    joblib.dump(pipe_rf, models_dir / "model_rf.joblib")
    with open(models_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"[+] Đã lưu mô hình vào: {models_dir}")
    print(f"[+] Metrics so sánh:\n{json.dumps(metrics, indent=2, ensure_ascii=False)}")

    # 6. Xuất biểu đồ Top đặc trưng quan trọng
    plt.figure(figsize=(9, 5))
    top_10 = fi_df.head(8).iloc[::-1]  # Đảo chiều để thanh cao nhất ở trên
    plt.barh(top_10["display_name"], top_10["importance"] * 100, color="#2563eb", edgecolor="#1d4ed8")
    plt.xlabel("Mức độ quan trọng (%)", fontweight="bold")
    plt.title("Top đặc trưng ảnh hưởng lớn nhất đến Giá nhà (Random Forest)", fontsize=12, fontweight="bold")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(figures_dir / "feature_importance.png", dpi=300)
    plt.close()
    print(f"[+] Đã xuất biểu đồ độ quan trọng đặc trưng: {figures_dir / 'feature_importance.png'}")

    return metrics, fitted_models


def predict_single_house(
    model: Pipeline,
    house_dict: Dict[str, Any],
    rmse_uncertainty: float = 0.0,
) -> Dict[str, Any]:
    """Dự đoán giá của một căn nhà với khoảng dao động gợi ý."""
    input_df = pd.DataFrame([house_dict])
    pred_val = float(model.predict(input_df)[0])

    # Giới hạn giá trị dương
    pred_val = max(100.0, pred_val)

    # Đổi sang tỷ VNĐ
    pred_ty = pred_val / 1000
    rmse_ty = rmse_uncertainty / 1000

    lower_bound = max(0.1, pred_ty - rmse_ty)
    upper_bound = pred_ty + rmse_ty

    return {
        "gia_trieu": round(pred_val, 2),
        "gia_ty_str": f"{pred_ty:.2f} tỷ VNĐ",
        "khoang_dao_dong_str": f"khoảng: {lower_bound:.2f} – {upper_bound:.2f} tỷ VNĐ",
        "lower_bound_ty": round(lower_bound, 2),
        "upper_bound_ty": round(upper_bound, 2),
    }


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    houses_csv = base_dir / "houses.csv"
    if not houses_csv.exists():
        print(f"[!] Lỗi: Chưa tìm thấy {houses_csv}")
        sys.exit(1)

    df_clean = load_clean_data(houses_csv)
    train_and_evaluate_models(
        df_clean, base_dir / "models", base_dir / "figures"
    )

