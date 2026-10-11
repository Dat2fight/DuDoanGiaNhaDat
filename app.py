"""Trang chủ ứng dụng HouseInsight - Phân tích và dự đoán giá nhà tại Hà Nội."""

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.ui import apply_custom_css, render_sidebar_info

st.set_page_config(
    page_title="HouseInsight - Trang chủ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
render_sidebar_info()


@st.cache_data
def load_overview_data():
    """Nạp dữ liệu tổng quan cho trang chủ."""
    base_dir = Path(__file__).resolve().parent
    houses_csv = base_dir / "houses.csv"
    metrics_json = base_dir / "models" / "metrics.json"

    df = pd.read_csv(houses_csv, na_values=["N/a", "NaN"], encoding="utf-8-sig")

    best_r2 = 0.75
    if metrics_json.exists():
        with open(metrics_json, "r", encoding="utf-8") as f:
            m_data = json.load(f)
            best_r2 = m_data.get("Random Forest", {}).get("test", {}).get("R2", 0.75)

    return df, best_r2


df, best_r2 = load_overview_data()

# 1. Hero Banner
st.markdown(
    """
    <div class="hero-banner">
        <h1>Phân tích dữ liệu và Dự đoán giá nhà<br>tại Hà Nội</h1>
        <p>Ứng dụng sử dụng dữ liệu thực tế, các phương pháp thống kê, phân cụm và học máy để giúp bạn hiểu rõ thị trường bất động sản và đưa ra quyết định thông minh hơn.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. 4 Thẻ chỉ số chính (Key Metrics Cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: #eff6ff; color: #2563eb;">🏠</div>
            <div>
                <div class="metric-label">Tổng số căn nhà</div>
                <div class="metric-value">{len(df):,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    num_districts = df["quan_huyen"].nunique()
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: #f0fdf4; color: #16a34a;">🏢</div>
            <div>
                <div class="metric-label">Số khu vực</div>
                <div class="metric-value">{num_districts}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    median_price_ty = df["gia_ban"].median() / 1000
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: #fff7ed; color: #ea580c;">🪙</div>
            <div>
                <div class="metric-label">Giá trung vị</div>
                <div class="metric-value">{median_price_ty:.2f} tỷ VNĐ</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon" style="background: #faf5ff; color: #9333ea;">📈</div>
            <div>
                <div class="metric-label">R² mô hình tốt nhất</div>
                <div class="metric-value">{best_r2:.2f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# 3. Khối Hướng dẫn sử dụng
st.markdown(
    """
    <div class="hi-card">
        <h3 style="font-size: 17px; font-weight: 700; color: #0f172a; margin-bottom: 16px;">
            🧭 Hướng dẫn sử dụng hệ thống
        </h3>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
            <div class="guide-step">
                <div class="guide-step-num">1</div>
                <div class="guide-step-title">Dữ liệu</div>
                <div class="guide-step-desc">Xem, tra cứu, áp dụng bộ lọc theo quận, khoảng giá, diện tích và tải file <code>houses.csv</code>.</div>
            </div>
            <div class="guide-step">
                <div class="guide-step-num">2</div>
                <div class="guide-step-title">Thống kê</div>
                <div class="guide-step-desc">Khám phá Mean, Median, Std, so sánh giá giữa các quận huyện và phân tích phân bố Skewness.</div>
            </div>
            <div class="guide-step">
                <div class="guide-step-num">3</div>
                <div class="guide-step-title">Phân cụm</div>
                <div class="guide-step-desc">Khám phá các phân khúc nhà tương đồng với thuật toán K-Means, Elbow, Silhouette và không gian PCA 2D.</div>
            </div>
            <div class="guide-step">
                <div class="guide-step-num">4</div>
                <div class="guide-step-title">Dự đoán giá</div>
                <div class="guide-step-desc">Định giá căn nhà tự động dựa trên học máy (Random Forest & Linear Regression) kèm khoảng dao động tin cậy.</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Ghi chú chân trang
st.markdown(
    """
    <div class="footer-note">
        <div>🔵 <b>Nguồn dữ liệu:</b> <i>alonhadat.com.vn & VN Housing Dataset (Hà Nội)</i></div>
        <div>⚠️ <b>Lưu ý:</b> <i>Giá dự đoán chỉ mang tính tham khảo, không phải giá giao dịch chính thức ngoài thị trường.</i></div>
    </div>
    """,
    unsafe_allow_html=True,
)

