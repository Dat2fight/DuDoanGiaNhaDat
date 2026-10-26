"""Trang 1: Dữ liệu - Xem, lọc và tải dữ liệu nhà ở đã thu thập."""

import json
from pathlib import Path
import pandas as pd
import streamlit as st

from src.ui import apply_custom_css, render_sidebar_info

st.set_page_config(
    page_title="HouseInsight - Dữ liệu",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
render_sidebar_info()

# Tiêu đề trang
col_title, col_btn = st.columns([3, 1])
with col_title:
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title"><span>📋</span> Dữ liệu</div>
            <div class="page-subtitle">Xem, lọc và tải dữ liệu nhà ở đã thu thập tại Hà Nội</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "houses.csv"
    meta_path = base_dir / "clean_meta.json"

    df_raw = pd.read_csv(csv_path, encoding="utf-8-sig")

    clean_meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            clean_meta = json.load(f)

    return df_raw, clean_meta, csv_path


df_houses, clean_meta, csv_path = load_data()

# Nút tải file CSV ở góc trên bên phải
with col_btn:
    with open(csv_path, "rb") as f:
        csv_bytes = f.read()
    st.download_button(
        label="📥 Tải xuống houses.csv",
        data=csv_bytes,
        file_name="houses.csv",
        mime="text/csv",
        use_container_width=True,
    )

# 1. Thanh công cụ lọc dữ liệu
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
st.markdown("<div style='font-weight: 700; margin-bottom: 12px; color: #0f172a;'>🔍 Bộ lọc tìm kiếm</div>", unsafe_allow_html=True)

f_col1, f_col2, f_col3 = st.columns([1.5, 2, 2])

# Danh sách quận huyện
all_districts = ["Tất cả"] + sorted([d for d in df_houses["quan_huyen"].unique() if d != "N/a"])

# Giá và diện tích dạng số thực tế để tính slider
df_numeric_temp = df_houses.copy()
df_numeric_temp["gia_ban_num"] = pd.to_numeric(df_numeric_temp["gia_ban"], errors="coerce")
df_numeric_temp["dien_tich_num"] = pd.to_numeric(df_numeric_temp["dien_tich"], errors="coerce")

min_price = int(df_numeric_temp["gia_ban_num"].min())
max_price = int(df_numeric_temp["gia_ban_num"].max())

min_area = int(df_numeric_temp["dien_tich_num"].min())
max_area = int(df_numeric_temp["dien_tich_num"].max())

with f_col1:
    selected_district = st.selectbox("Quận/Huyện", all_districts, index=0)

with f_col2:
    price_range = st.slider(
        "Khoảng giá (triệu VNĐ)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=100,
    )

with f_col3:
    area_range = st.slider(
        "Khoảng diện tích (m²)",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area),
        step=5,
    )

st.markdown("</div>", unsafe_allow_html=True)

# Lọc dữ liệu theo tiêu chí
filtered_df = df_houses.copy()
filtered_df["gia_ban_num"] = pd.to_numeric(filtered_df["gia_ban"], errors="coerce")
filtered_df["dien_tich_num"] = pd.to_numeric(filtered_df["dien_tich"], errors="coerce")

if selected_district != "Tất cả":
    filtered_df = filtered_df[filtered_df["quan_huyen"] == selected_district]

filtered_df = filtered_df[
    (filtered_df["gia_ban_num"] >= price_range[0])
    & (filtered_df["gia_ban_num"] <= price_range[1])
    & (filtered_df["dien_tich_num"] >= area_range[0])
    & (filtered_df["dien_tich_num"] <= area_range[1])
]

# 2. Khối Thông tin dữ liệu
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
st.markdown("<div style='font-weight: 700; margin-bottom: 12px; color: #0f172a;'>📊 Thông tin tập dữ liệu</div>", unsafe_allow_html=True)

info_col1, info_col3 = st.columns([1, 1])

with info_col1:
    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; text-align: center;">
            <div style="font-size: 13px; color: #64748b;">Tổng số dòng</div>
            <div style="font-size: 28px; font-weight: 800; color: #2563eb;">{len(df_houses)}</div>
            <div style="font-size: 12px; color: #10b981; margin-top: 4px;">Đang hiển thị: {len(filtered_df)} dòng</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 13px; color: #475569; line-height: 1.6;">
            <div>• <b>Nguồn:</b> <i>alonhadat.com.vn & Kaggle VN</i></div>
            <div>• <b>Ngày thu thập:</b> <i>11/10/2026</i></div>
            <div>• <b>Khu vực:</b> <i>TP. Hà Nội</i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with info_col3:
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 6px;'>Thống kê lọc khi làm sạch:</div>", unsafe_allow_html=True)
    if clean_meta:
        impute = clean_meta.get("impute_stats", {})
        impute_lines = ""
        col_vi = {
            "so_phong_ngu": "Phòng ngủ",
            "so_phong_tam": "Phòng tắm",
            "nam_xay_dung": "Năm xây dựng",
            "so_tang": "Số tầng",
            "duong_pho": "Đường/phố",
        }
        for k, v in impute.items():
            label = col_vi.get(k, k)
            val = v.get("trung_binh_chung", v.get("gia_tri_dien", "TB cùng dạng"))
            impute_lines += f"<div>• Điền TB <i>{label}</i>: <span style='color:#2563eb;'>{v['so_o_thieu']} ô (TB cùng quận: {val})</span></div>"
        st.markdown(
            f"""
            <div style="font-size: 12px; color: #475569; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; line-height: 1.8;">
                <div>• Bản ghi ban đầu: <b>{clean_meta.get('tong_ban_dau', 0)}</b></div>
                <div>• Trùng lặp đã xóa: <span style="color: #ef4444;">-{clean_meta.get('trung_lap', 0)}</span></div>
                <div>• Diện tích phi lý: <span style="color: #ef4444;">-{clean_meta.get('dien_tich_phi_ly', 0)}</span></div>
                <div>• Đơn giá ngoại lai (IQR): <span style="color: #ef4444;">-{clean_meta.get('don_gia_ngoai_lai', 0)}</span></div>
                <div>• Dữ liệu sạch nghiệm thu: <b style="color: #10b981;">{clean_meta.get('so_luong_sau_lam_sach', 0)}</b></div>
                <hr style="border:none;border-top:1px solid #e2e8f0;margin:6px 0;">
                <div style="font-weight:600;margin-bottom:2px;">Điền trung bình (Mean Imputation):</div>
                {impute_lines}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("</div>", unsafe_allow_html=True)

# 3. Bảng Danh sách nhà ở
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
st.markdown(
    f"<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>"
    f"<span style='font-weight: 700; color: #0f172a;'>Danh sách nhà ở ({len(filtered_df)} kết quả)</span>"
    f"</div>",
    unsafe_allow_html=True,
)

# Chuẩn bị bảng hiển thị đẹp mắt
display_df = filtered_df.drop(columns=["gia_ban_num", "dien_tich_num"]).copy()
display_df.insert(0, "STT", range(1, len(display_df) + 1))
display_df = display_df.rename(
    columns={
        "gia_ban": "Giá bán (triệu VNĐ)",
        "dien_tich": "Diện tích (m²)",
        "so_phong_ngu": "Phòng ngủ",
        "so_phong_tam": "Phòng tắm",
        "quan_huyen": "Quận/Huyện",
        "phuong_xa": "Phường/Xã",
        "duong_pho": "Đường/phố",
        "nam_xay_dung": "Năm xây dựng",
        "so_tang": "Số tầng",
    }
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=450,
)

st.markdown("</div>", unsafe_allow_html=True)

