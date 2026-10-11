"""Trang 4: Dự đoán giá - Sử dụng mô hình Machine Learning hồi quy để định giá nhà ở."""

import json
from pathlib import Path
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from src.model import predict_single_house
from src.stats import load_clean_data
from src.ui import apply_custom_css, render_sidebar_info

st.set_page_config(
    page_title="HouseInsight - Dự đoán giá",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
render_sidebar_info()

# Tiêu đề trang
st.markdown(
    """
    <div class="page-header">
        <div class="page-title"><span>🔮</span> Dự đoán giá</div>
        <div class="page-subtitle">Sử dụng mô hình hồi quy học máy (Linear Regression & Random Forest) để định giá nhà ở tại Hà Nội</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_ml_resources():
    """Nạp các mô hình đã huấn luyện sẵn và số liệu đánh giá từ models/."""
    base_dir = Path(__file__).resolve().parent.parent
    models_dir = base_dir / "models"
    houses_csv = base_dir / "houses.csv"

    model_lr = joblib.load(models_dir / "model_lr.joblib")
    model_rf = joblib.load(models_dir / "model_rf.joblib")

    with open(models_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    df_clean = load_clean_data(houses_csv)

    return model_lr, model_rf, metrics_data, df_clean


model_lr, model_rf, metrics_data, df_clean = load_ml_resources()

# Lấy danh sách quận huyện và phường xã từ dữ liệu thực tế
districts_list = sorted([d for d in df_clean["quan_huyen"].dropna().unique() if d != "Khác"])


# ----------------- HÀNG TRÊN: FORM NHẬP LIỆU & KẾT QUẢ DỰ ĐOÁN -----------------
form_col, result_col = st.columns([1.5, 1.2])

with form_col:
    st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight: 700; margin-bottom: 12px; color: #0f172a;'>📝 Thông tin căn nhà</div>", unsafe_allow_html=True)

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        inp_area = st.number_input("Diện tích (m²):", min_value=10.0, max_value=800.0, value=65.0, step=5.0)
    with r1_c2:
        inp_district = st.selectbox("Quận/Huyện:", districts_list, index=districts_list.index("Cầu Giấy") if "Cầu Giấy" in districts_list else 0)

    # Lấy danh sách phường xã theo quận đã chọn
    sub_wards = df_clean[df_clean["quan_huyen"] == inp_district]["phuong_xa"].dropna().unique().tolist()
    wards_list = sorted([w for w in sub_wards if w != "N/a" and w != "Khác"])
    if not wards_list:
        wards_list = ["Khác"]
    else:
        wards_list = wards_list + ["Khác"]

    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        inp_ward = st.selectbox("Phường/Xã:", wards_list, index=0)
    with r2_c2:
        inp_floors = st.number_input("Số tầng:", min_value=1.0, max_value=15.0, value=4.0, step=1.0)

    r3_c1, r3_c2, r3_c3 = st.columns(3)
    with r3_c1:
        inp_bedrooms = st.number_input("Phòng ngủ:", min_value=1.0, max_value=15.0, value=3.0, step=1.0)
    with r3_c2:
        inp_bathrooms = st.number_input("Phòng tắm:", min_value=1.0, max_value=15.0, value=2.0, step=1.0)
    with r3_c3:
        inp_year = st.number_input("Năm xây dựng:", min_value=1990.0, max_value=2026.0, value=2018.0, step=1.0)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    r4_c1, r4_c2 = st.columns([1.5, 1])
    with r4_c1:
        chosen_model_name = st.radio(
            "Chọn mô hình dự đoán:",
            options=["Random Forest (Khuyên dùng)", "Linear Regression"],
            horizontal=True,
        )
    with r4_c2:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        predict_btn = st.button("💰 Dự đoán giá", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with result_col:
    st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight: 700; margin-bottom: 12px; color: #0f172a;'>🎯 Kết quả dự đoán</div>", unsafe_allow_html=True)

    # Chuẩn bị dữ liệu mẫu dự đoán
    active_model = model_rf if "Random Forest" in chosen_model_name else model_lr
    raw_model_key = "Random Forest" if "Random Forest" in chosen_model_name else "Linear Regression"
    rmse_val = metrics_data.get(raw_model_key, {}).get("test", {}).get("RMSE", 5000.0)

    house_payload = {
        "dien_tich": inp_area,
        "so_phong_ngu": inp_bedrooms,
        "so_phong_tam": inp_bathrooms,
        "nam_xay_dung": inp_year,
        "so_tang": inp_floors,
        "quan_huyen": inp_district,
        "phuong_xa": inp_ward,
    }

    try:
        pred_res = predict_single_house(active_model, house_payload, rmse_uncertainty=rmse_val)
        pred_price_str = pred_res["gia_ty_str"]
        pred_range_str = pred_res["khoang_dao_dong_str"]
    except Exception as e:
        pred_price_str = "N/A"
        pred_range_str = f"Lỗi dự đoán: {e}"

    st.markdown(
        f"""
        <div style="background: #f0fdf4; border: 2px solid #bbf7d0; border-radius: 12px; padding: 24px 20px; text-align: center; margin-bottom: 12px;">
            <div style="font-size: 36px; margin-bottom: 4px;">🏡</div>
            <div style="font-size: 13px; font-weight: 600; color: #166534; text-transform: uppercase;">Giá ước tính</div>
            <div style="font-size: 32px; font-weight: 800; color: #15803d; margin: 6px 0;">{pred_price_str}</div>
            <div style="font-size: 13px; color: #166534; font-weight: 500;">({pred_range_str})</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div style="font-size: 12px; color: #64748b; line-height: 1.6; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px;">
            ℹ️ <i>Mô hình đang dùng: <b>{raw_model_key}</b>.<br>
            Khoảng dao động được tính toán dựa trên sai số chuẩn RMSE (±{rmse_val/1000:.2f} tỷ VNĐ) trên tập kiểm thử độc lập.</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- HÀNG DƯỚI: SO SÁNH HIỆU SUẤT MÔ HÌNH & FEATURE IMPORTANCE -----------------
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
b_col1, b_col2 = st.columns([1.1, 1.3])

with b_col1:
    st.markdown("<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>📊 So sánh hiệu suất mô hình</div>", unsafe_allow_html=True)

    perf_data = [
        {
            "Mô hình": "Linear Regression",
            "MAE (Train)": f"{metrics_data['Linear Regression']['train']['MAE']:,}",
            "RMSE (Train)": f"{metrics_data['Linear Regression']['train']['RMSE']:,}",
            "R² (Train)": metrics_data['Linear Regression']['train']['R2'],
            "MAE (Test)": f"{metrics_data['Linear Regression']['test']['MAE']:,}",
            "RMSE (Test)": f"{metrics_data['Linear Regression']['test']['RMSE']:,}",
            "R² (Test)": metrics_data['Linear Regression']['test']['R2'],
        },
        {
            "Mô hình": "Random Forest",
            "MAE (Train)": f"{metrics_data['Random Forest']['train']['MAE']:,}",
            "RMSE (Train)": f"{metrics_data['Random Forest']['train']['RMSE']:,}",
            "R² (Train)": metrics_data['Random Forest']['train']['R2'],
            "MAE (Test)": f"{metrics_data['Random Forest']['test']['MAE']:,}",
            "RMSE (Test)": f"{metrics_data['Random Forest']['test']['RMSE']:,}",
            "R² (Test)": metrics_data['Random Forest']['test']['R2'],
        },
    ]

    st.dataframe(pd.DataFrame(perf_data), use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div style="font-size: 12px; color: #475569; margin-top: 8px; line-height: 1.5;">
            💡 <b>Đánh giá hiện tượng Overfitting:</b><br>
            • <i>Random Forest đạt R² = 0.89 trên Train và R² = 0.75 trên Test (chênh lệch vừa phải), thể hiện khả năng học mối quan hệ phi tuyến tốt.<br>
            • Linear Regression có R² test = 0.57 thấp hơn đáng kể do không nắm bắt được tương tác phức tạp giữa vị trí và quy mô nhà.</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

with b_col2:
    st.markdown("<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>🌟 Top đặc trưng quan trọng (Random Forest)</div>", unsafe_allow_html=True)

    top_feats = metrics_data.get("top_features_rf", [])
    if top_feats:
        fi_df = pd.DataFrame(top_feats[:7])
        fi_df["importance_pct"] = fi_df["importance"] * 100

        fig_fi = px.bar(
            fi_df.iloc[::-1],
            x="importance_pct",
            y="display_name",
            orientation="h",
            color_discrete_sequence=["#2563eb"],
            labels={"importance_pct": "Độ quan trọng (%)", "display_name": "Đặc trưng"},
        )
        fig_fi.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=30),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown(
        f"""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #1e40af; line-height: 1.5;">
            📌 {metrics_data.get('importance_comment', '')}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

