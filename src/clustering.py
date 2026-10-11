"""Module phân cụm K-Means, giảm chiều PCA và đánh giá Elbow, Silhouette."""

from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

plt.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


VALID_FEATURES = [
    "gia_ban",
    "dien_tich",
    "so_phong_ngu",
    "so_phong_tam",
    "nam_xay_dung",
    "so_tang",
]


def prepare_clustering_data(
    df: pd.DataFrame, feature_cols: List[str]
) -> Tuple[np.ndarray, SimpleImputer, StandardScaler, pd.DataFrame]:
    """
    Tiền xử lý đặc trưng cho K-Means:
    - Xử lý giá trị thiếu bằng Median.
    - Chuẩn hóa bằng StandardScaler.
    """
    # Lấy các cột đặc trưng hợp lệ
    sub_df = df[feature_cols].copy()

    # Điền giá trị thiếu bằng median
    imputer = SimpleImputer(strategy="median")
    imputed_data = imputer.fit_transform(sub_df)

    # Chuẩn hóa StandardScaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(imputed_data)

    df_imputed = pd.DataFrame(imputed_data, columns=feature_cols, index=sub_df.index)
    return scaled_data, imputer, scaler, df_imputed


def evaluate_k_range(
    X_scaled: np.ndarray, k_range: range = range(2, 11)
) -> Tuple[List[int], List[float], List[float], int, str]:
    """
    Tính Elbow (Inertia) và Silhouette Score cho dãy số cụm k.
    Gợi ý k tối ưu dựa trên Silhouette Score lớn nhất.
    """
    inertias: List[float] = []
    silhouette_scores: List[float] = []
    k_list = list(k_range)

    for k in k_list:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(float(km.inertia_))
        score = float(silhouette_score(X_scaled, labels))
        silhouette_scores.append(round(score, 4))

    # Tìm k tốt nhất
    best_idx = int(np.argmax(silhouette_scores))
    best_k = k_list[best_idx]
    best_score = silhouette_scores[best_idx]

    explanation = (
        f"Giá trị k = {best_k} đạt Silhouette Score cao nhất ({best_score:.4f}), "
        f"cho thấy các cụm có độ cố kết nội bộ tốt và phân tách rõ ràng nhất giữa các nhóm."
    )

    return k_list, inertias, silhouette_scores, best_k, explanation


def run_kmeans(X_scaled: np.ndarray, k: int) -> Tuple[np.ndarray, KMeans]:
    """Chạy mô hình K-Means với k cụm cố định."""
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    return labels, km


def summarize_clusters(df: pd.DataFrame, labels: np.ndarray, k: int) -> pd.DataFrame:
    """
    Tạo bảng mô tả chi tiết từng cụm:
    Số mẫu, Giá TB, Diện tích TB, Khu vực chiếm ưu thế, Tên nhãn cụm tự động.
    """
    df_temp = df.copy()
    df_temp["cluster"] = labels

    cluster_info: List[Dict[str, Any]] = []
    for c in range(k):
        c_sub = df_temp[df_temp["cluster"] == c]
        count = len(c_sub)
        avg_price = float(c_sub["gia_ban"].mean()) if count > 0 else 0.0
        avg_area = float(c_sub["dien_tich"].mean()) if count > 0 else 0.0

        # Khu vực chiếm ưu thế
        dist_mode = c_sub["quan_huyen"].mode()
        dominant_area = str(dist_mode.iloc[0]) if len(dist_mode) > 0 else "N/A"

        cluster_info.append(
            {
                "Cụm": c + 1,
                "Số mẫu": count,
                "Giá TB (triệu)": round(avg_price, 1),
                "Diện tích TB (m²)": round(avg_area, 1),
                "Khu vực chiếm ưu thế": dominant_area,
                "_raw_price": avg_price,
            }
        )

    res_df = pd.DataFrame(cluster_info)

    # Đặt tên cụm tự động dựa trên phân vị giá TB
    sorted_indices = res_df.sort_values(by="_raw_price").index.tolist()
    names = ["Giá thấp", "Giá trung bình", "Giá cao", "Giá rất cao", "Phân khúc cao cấp"]
    cluster_names = {}
    for rank, idx in enumerate(sorted_indices):
        name_idx = min(rank, len(names) - 1)
        cluster_names[idx] = names[name_idx]

    res_df["Tên cụm"] = [cluster_names[i] for i in range(len(res_df))]
    res_df = res_df.drop(columns=["_raw_price"])
    return res_df


def compute_pca_2d(X_scaled: np.ndarray) -> Tuple[np.ndarray, Tuple[float, float], str]:
    """Giảm chiều dữ liệu xuống 2 chiều PC1 và PC2, trả về tỷ lệ phương sai giải thích."""
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    var1, var2 = float(pca.explained_variance_ratio_[0]), float(pca.explained_variance_ratio_[1])
    total_var = var1 + var2

    comment = (
        f"Hai thành phần chính PC1 ({var1*100:.1f}%) và PC2 ({var2*100:.1f}%) "
        f"giải thích tổng cộng {total_var*100:.1f}% phương sai dữ liệu."
    )
    return coords, (var1, var2), comment


def export_cluster_figure(
    coords: np.ndarray,
    labels: np.ndarray,
    k: int,
    var_ratios: Tuple[float, float],
    output_png: Path,
) -> None:
    """Vẽ và lưu biểu đồ PCA 2D ra file PNG."""
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 6))

    colors = ["#2563eb", "#f97316", "#10b981", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#6366f1", "#84cc16", "#06b6d4"]
    for c in range(k):
        mask = labels == c
        color = colors[c % len(colors)]
        plt.scatter(
            coords[mask, 0],
            coords[mask, 1],
            label=f"Cụm {c + 1}",
            color=color,
            alpha=0.75,
            edgecolors="none",
            s=45,
        )

    var1, var2 = var_ratios
    plt.xlabel(f"PC1 ({var1 * 100:.1f}%)", fontweight="bold")
    plt.ylabel(f"PC2 ({var2 * 100:.1f}%)", fontweight="bold")
    plt.title(f"Phân cụm bất động sản với K-Means (k={k}) trên không gian PCA 2D", fontsize=12, fontweight="bold")
    plt.legend(frameon=True)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()
    print(f"[+] Đã lưu biểu đồ phân cụm vào: {output_png}")

