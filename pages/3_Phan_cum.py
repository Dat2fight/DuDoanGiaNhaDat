"""Trang 3: Phân cụm - Nhóm các căn nhà có đặc điểm tương đồng (K-Means + PCA)."""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.clustering import (
    VALID_FEATURES,
    compute_pca_2d,
    evaluate_k_range,
    prepare_clustering_data,
    run_kmeans,
    summarize_clusters,
)
from src.stats import load_clean_data
from src.ui import apply_custom_css, render_sidebar_info

st.set_page_config(
    page_title="HouseInsight - Phân cụm",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
render_sidebar_info()

# Tiêu đề trang
st.markdown(
    """
    <div class="page-header">
        <div class="page-title"><span>🗂️</span> Phân cụm</div>
        <div class="page-subtitle">Nhóm các căn nhà có đặc điểm tương đồng bằng thuật toán K-Means và trực quan hóa PCA 2D</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_dataset():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "houses.csv"
    return load_clean_data(csv_path)


df_clean = get_dataset()

# ----------------- BỘ ĐIỀU KHIỂN ĐẶC TRƯNG & THAM SỐ K -----------------
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)

FEATURE_DISPLAY_MAP = {
    "gia_ban": "Giá bán",
    "dien_tich": "Diện tích",
    "so_phong_ngu": "Phòng ngủ",
    "so_phong_tam": "Phòng tắm",
    "nam_xay_dung": "Năm xây dựng",
    "so_tang": "Số tầng",
}
REV_FEATURE_MAP = {v: k for k, v in FEATURE_DISPLAY_MAP.items()}

ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([3, 2, 1.2])

with ctrl_col1:
    selected_display_features = st.multiselect(
        "Chọn đặc trưng đưa vào phân cụm:",
        options=list(FEATURE_DISPLAY_MAP.values()),
        default=list(FEATURE_DISPLAY_MAP.values()),
    )
    chosen_features = [REV_FEATURE_MAP[f] for f in selected_display_features]

with ctrl_col2:
    selected_k = st.slider("Số cụm (k):", min_value=2, max_value=10, value=3, step=1)

with ctrl_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    run_cluster_btn = st.button("🚀 Chạy phân cụm", use_container_width=True, type="primary")

st.markdown(
    """
    <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
        ⚙️ <i>Tiền xử lý tự động: Giá trị thiếu được điền bằng <b>Median</b> (trung vị); các đặc trưng được chuẩn hóa bằng <b>StandardScaler</b> trước khi chạy K-Means.</i>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

if len(chosen_features) < 2:
    st.warning("⚠️ Vui lòng chọn tối thiểu 2 đặc trưng để thực hiện phân cụm K-Means và trực quan hóa PCA.")
    st.stop()


# ----------------- CHẠY TIỀN XỬ LÝ & ĐÁNH GIÁ K -----------------
@st.cache_data
def cached_k_evaluation(df_encoded_str: str, feat_cols: list):
    X_scaled, imputer, scaler, df_imputed = prepare_clustering_data(df_clean, feat_cols)
    k_list, inertias, silhouettes, best_k, expl = evaluate_k_range(X_scaled, range(2, 11))
    return X_scaled, df_imputed, k_list, inertias, silhouettes, best_k, expl


# Hashable representation
X_scaled, df_imputed, k_list, inertias, silhouettes, best_k, expl = cached_k_evaluation(
    str(len(df_clean)), chosen_features
)

# ----------------- HÀNG 1: BIỂU ĐỒ ELBOW, SILHOUETTE & GỢI Ý K -----------------
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
c_col1, c_col2, c_col3 = st.columns([1.5, 1.5, 1.3])

with c_col1:
    fig_elbow = go.Figure()
    fig_elbow.add_trace(
        go.Scatter(
            x=k_list,
            y=inertias,
            mode="lines+markers",
            name="Inertia",
            line=dict(color="#2563eb", width=2.5),
            marker=dict(size=7, color="#1e40af"),
        )
    )
    fig_elbow.update_layout(
        title="Phương pháp khuỷu tay (Elbow Method)",
        xaxis_title="Số cụm (k)",
        yaxis_title="Inertia",
        height=280,
        margin=dict(l=10, r=10, t=35, b=30),
        plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_elbow, use_container_width=True)

with c_col2:
    fig_sil = go.Figure()
    fig_sil.add_trace(
        go.Scatter(
            x=k_list,
            y=silhouettes,
            mode="lines+markers",
            name="Silhouette",
            line=dict(color="#10b981", width=2.5),
            marker=dict(size=7, color="#047857"),
        )
    )
    # Highlight best k
    best_sil_val = silhouettes[k_list.index(best_k)]
    fig_sil.add_trace(
        go.Scatter(
            x=[best_k],
            y=[best_sil_val],
            mode="markers",
            name=f"Tốt nhất (k={best_k})",
            marker=dict(size=12, color="#ef4444", symbol="star"),
        )
    )
    fig_sil.update_layout(
        title="Điểm Silhouette (Silhouette Score)",
        xaxis_title="Số cụm (k)",
        yaxis_title="Silhouette Score",
        height=280,
        margin=dict(l=10, r=10, t=35, b=30),
        plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_sil, use_container_width=True)

with c_col3:
    st.markdown(
        f"""
        <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 18px; height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-size: 20px;">💡</span>
                <span style="font-size: 13px; font-weight: 700; color: #b45309; text-transform: uppercase;">Kết quả gợi ý</span>
            </div>
            <div style="font-size: 24px; font-weight: 800; color: #78350f; margin-bottom: 8px;">
                k = {best_k} <span style="font-size: 13px; font-weight: 500; color: #92400e;">(theo Silhouette Score = {best_sil_val:.3f})</span>
            </div>
            <div style="font-size: 12px; color: #92400e; line-height: 1.5;">
                {expl}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)


# ----------------- HÀNG 2: BẢNG MÔ TẢ CỤM & BIỂU ĐỒ PCA 2D -----------------
labels, km_model = run_kmeans(X_scaled, selected_k)
summary_clusters_df = summarize_clusters(df_clean, labels, selected_k)
coords, var_ratios, pca_comment = compute_pca_2d(X_scaled)

st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
p_col1, p_col2 = st.columns([1.1, 1.3])

with p_col1:
    st.markdown(
        f"<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>Bảng mô tả các cụm (k = {selected_k})</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        summary_clusters_df,
        use_container_width=True,
        hide_index=True,
        height=320,
    )

with p_col2:
    st.markdown(
        "<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>Trực quan hóa không gian PCA 2D</div>",
        unsafe_allow_html=True,
    )

    plot_df = pd.DataFrame({
        "PC1": coords[:, 0],
        "PC2": coords[:, 1],
        "Cụm": [f"Cụm {lbl + 1}" for lbl in labels],
        "Quận": df_clean["quan_huyen"],
        "Giá bán (tr)": df_clean["gia_ban"],
        "Diện tích (m²)": df_clean["dien_tich"],
    })

    fig_pca = px.scatter(
        plot_df,
        x="PC1",
        y="PC2",
        color="Cụm",
        hover_data=["Quận", "Giá bán (tr)", "Diện tích (m²)"],
        title="",
        color_discrete_sequence=["#2563eb", "#f97316", "#10b981", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#6366f1"],
    )
    fig_pca.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=30),
        xaxis_title=f"PC1 ({var_ratios[0]*100:.1f}%)",
        yaxis_title=f"PC2 ({var_ratios[1]*100:.1f}%)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #334155; line-height: 1.6;">
            📊 <b>Tỷ lệ phương sai giải thích:</b> PC1 = <b>{var_ratios[0]*100:.1f}%</b>, PC2 = <b>{var_ratios[1]*100:.1f}%</b>.<br>
            💬 <b>Nhận xét mức độ tách biệt:</b> {pca_comment}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)