"""Trang 2: Thống kê - Thống kê mô tả và so sánh giữa các khu vực."""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.stats import analyze_distribution, compare_districts, get_top_cheapest_and_most_expensive, load_clean_data
from src.ui import apply_custom_css, render_sidebar_info

st.set_page_config(
    page_title="HouseInsight - Thống kê",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_css()
render_sidebar_info()

# Tiêu đề trang
st.markdown(
    """
    <div class="page-header">
        <div class="page-title"><span>📊</span> Thống kê</div>
        <div class="page-subtitle">Phân tích thống kê mô tả và so sánh chi tiết giữa các khu vực tại Hà Nội</div>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_all_stats_data():
    base_dir = Path(__file__).resolve().parent.parent
    houses_csv = base_dir / "houses.csv"
    results2_csv = base_dir / "results2.csv"

    df_clean = load_clean_data(houses_csv)
    results2_df = pd.read_csv(results2_csv, encoding="utf-8-sig") if results2_csv.exists() else pd.DataFrame()

    return df_clean, results2_df


df_clean, results2_df = load_all_stats_data()

# ----------------- HÀNG 1: THỐNG KÊ MÔ TẢ & TOP 3 RẺ / ĐẮT NHẤT -----------------
row1_col1, row1_col2 = st.columns([1.1, 1.2])

with row1_col1:
    st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>1. Thống kê mô tả</div>", unsafe_allow_html=True)

    tab_all, tab_district = st.tabs(["Toàn bộ dữ liệu (all)", "Theo từng khu vực (results2.csv)"])

    with tab_all:
        if not results2_df.empty:
            all_row = results2_df[results2_df["Khu vực"] == "all"].iloc[0]
            desc_items = [
                {"Thuộc tính": "Giá bán (triệu VNĐ)", "Mean": f"{all_row['Mean của Giá']:,}", "Median": f"{all_row['Median của Giá']:,}", "Std": f"{all_row['Std của Giá']:,}"},
                {"Thuộc tính": "Diện tích (m²)", "Mean": f"{all_row['Mean của Diện tích']:,}", "Median": f"{all_row['Median của Diện tích']:,}", "Std": f"{all_row['Std của Diện tích']:,}"},
                {"Thuộc tính": "Phòng ngủ", "Mean": f"{all_row['Mean của Phòng ngủ']}", "Median": f"{all_row['Median của Phòng ngủ']}", "Std": f"{all_row['Std của Phòng ngủ']}"},
                {"Thuộc tính": "Phòng tắm", "Mean": f"{all_row['Mean của Phòng tắm']}", "Median": f"{all_row['Median của Phòng tắm']}", "Std": f"{all_row['Std của Phòng tắm']}"},
                {"Thuộc tính": "Năm xây dựng", "Mean": f"{all_row['Mean của Năm xây dựng']}", "Median": f"{all_row['Median của Năm xây dựng']}", "Std": f"{all_row['Std của Năm xây dựng']}"},
                {"Thuộc tính": "Số tầng", "Mean": f"{all_row['Mean của Số tầng']}", "Median": f"{all_row['Median của Số tầng']}", "Std": f"{all_row['Std của Số tầng']}"},
            ]
            st.dataframe(pd.DataFrame(desc_items), use_container_width=True, hide_index=True)

    with tab_district:
        if not results2_df.empty:
            dist_options = [k for k in results2_df["Khu vực"].tolist() if k != "all"]
            sel_d = st.selectbox("Chọn khu vực xem chi tiết:", dist_options, key="stat_dist_sel")
            d_row = results2_df[results2_df["Khu vực"] == sel_d].iloc[0]
            d_items = [
                {"Thuộc tính": "Giá bán (triệu VNĐ)", "Mean": f"{d_row['Mean của Giá']:,}", "Median": f"{d_row['Median của Giá']:,}", "Std": f"{d_row['Std của Giá']:,}"},
                {"Thuộc tính": "Diện tích (m²)", "Mean": f"{d_row['Mean của Diện tích']:,}", "Median": f"{d_row['Median của Diện tích']:,}", "Std": f"{d_row['Std của Diện tích']:,}"},
                {"Thuộc tính": "Phòng ngủ", "Mean": f"{d_row['Mean của Phòng ngủ']}", "Median": f"{d_row['Median của Phòng ngủ']}", "Std": f"{d_row['Std của Phòng ngủ']}"},
                {"Thuộc tính": "Phòng tắm", "Mean": f"{d_row['Mean của Phòng tắm']}", "Median": f"{d_row['Median của Phòng tắm']}", "Std": f"{d_row['Std của Phòng tắm']}"},
                {"Thuộc tính": "Năm xây dựng", "Mean": f"{d_row['Mean của Năm xây dựng']}", "Median": f"{d_row['Median của Năm xây dựng']}", "Std": f"{d_row['Std của Năm xây dựng']}"},
                {"Thuộc tính": "Số tầng", "Mean": f"{d_row['Mean của Số tầng']}", "Median": f"{d_row['Median của Số tầng']}", "Std": f"{d_row['Std của Số tầng']}"},
            ]
            st.dataframe(pd.DataFrame(d_items), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

with row1_col2:
    st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>2. 3 căn rẻ nhất và 3 căn đắt nhất</div>", unsafe_allow_html=True)

    cheapest_3, expensive_3 = get_top_cheapest_and_most_expensive(df_clean, n=3)

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #16a34a; margin-bottom: 6px;'>🟢 3 căn rẻ nhất</div>", unsafe_allow_html=True)
        ch_display = []
        for _, r in cheapest_3.iterrows():
            loc = f"{r['quan_huyen']}" if pd.isna(r['phuong_xa']) else f"{r['phuong_xa']}, {r['quan_huyen']}"
            ch_display.append({
                "Vị trí": loc,
                "Diện tích": f"{r['dien_tich']:.0f} m²",
                "Giá bán": f"{r['gia_ban']:.0f} tr" if r['gia_ban'] < 1000 else f"{r['gia_ban']/1000:.2f} tỷ",
            })
        st.dataframe(pd.DataFrame(ch_display), use_container_width=True, hide_index=True)

    with t_col2:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #ea580c; margin-bottom: 6px;'>🔴 3 căn đắt nhất</div>", unsafe_allow_html=True)
        ex_display = []
        for _, r in expensive_3.iterrows():
            loc = f"{r['quan_huyen']}" if pd.isna(r['phuong_xa']) else f"{r['phuong_xa']}, {r['quan_huyen']}"
            ex_display.append({
                "Vị trí": loc,
                "Diện tích": f"{r['dien_tich']:.0f} m²",
                "Giá bán": f"{r['gia_ban']/1000:.1f} tỷ",
            })
        st.dataframe(pd.DataFrame(ex_display), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------- HÀNG 2: SO SÁNH KHU VỰC (CỘT & BOXPLOT) -----------------
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
st.markdown("<div style='font-weight: 700; margin-bottom: 4px; color: #0f172a;'>3. So sánh khu vực</div>", unsafe_allow_html=True)
st.caption("Chỉ xét các quận/huyện có đủ số mẫu (≥ 5 căn nhà) để đảm bảo ý nghĩa thống kê.")

summary_dist, most_exp, cheapest_dist = compare_districts(df_clean, min_samples=5)

# Badge thông báo đắt nhất / rẻ nhất
b_col1, b_col2 = st.columns(2)
with b_col1:
    st.markdown(
        f"""
        <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #991b1b; margin-bottom: 12px;">
            🔥 Khu vực đắt nhất: <b>{most_exp}</b> (Đơn giá TB: <b>{summary_dist[summary_dist['quan_huyen']==most_exp]['don_gia_tb'].values[0]:.1f} tr/m²</b>)
        </div>
        """,
        unsafe_allow_html=True,
    )
with b_col2:
    st.markdown(
        f"""
        <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 8px 12px; border-radius: 4px; font-size: 13px; color: #065f46; margin-bottom: 12px;">
            💎 Khu vực mềm nhất: <b>{cheapest_dist}</b> (Đơn giá TB: <b>{summary_dist[summary_dist['quan_huyen']==cheapest_dist]['don_gia_tb'].values[0]:.1f} tr/m²</b>)
        </div>
        """,
        unsafe_allow_html=True,
    )

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=summary_dist["quan_huyen"],
            y=summary_dist["don_gia_tb"],
            name="Đơn giá TB (triệu/m²)",
            marker_color="#2563eb",
        )
    )
    fig_bar.add_trace(
        go.Bar(
            x=summary_dist["quan_huyen"],
            y=summary_dist["gia_tb_ty"],
            name="Giá TB (tỷ VNĐ)",
            marker_color="#f97316",
        )
    )
    fig_bar.update_layout(
        title="Đơn giá (tr/m²) & Giá TB (tỷ) theo khu vực",
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_tickangle=-30,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    # Boxplot giá bán theo khu vực
    top_dists_list = summary_dist["quan_huyen"].tolist()
    df_box = df_clean[df_clean["quan_huyen"].isin(top_dists_list)].copy()
    df_box["gia_ban_ty"] = df_box["gia_ban"] / 1000

    fig_box = px.box(
        df_box,
        x="quan_huyen",
        y="gia_ban_ty",
        title="Boxplot phân bố Giá bán (tỷ VNĐ) theo khu vực",
        color="quan_huyen",
    )
    fig_box.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=False,
        xaxis_tickangle=-30,
        xaxis_title="Quận / Huyện",
        yaxis_title="Giá bán (tỷ VNĐ)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ----------------- HÀNG 3: HISTOGRAM PHÂN BỐ GIÁ & DIỆN TÍCH -----------------
st.markdown("<div class='hi-card'>", unsafe_allow_html=True)
st.markdown("<div style='font-weight: 700; margin-bottom: 8px; color: #0f172a;'>4. Histogram giá và diện tích</div>", unsafe_allow_html=True)

h_col1, h_col2, h_col3 = st.columns([1, 1, 1.2])

with h_col1:
    fig_h_price = px.histogram(
        df_clean,
        x="gia_ban",
        nbins=35,
        title="Phân bố giá (toàn bộ dữ liệu)",
        color_discrete_sequence=["#3b82f6"],
    )
    fig_h_price.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=35, b=30),
        xaxis_title="Giá (triệu VNĐ)",
        yaxis_title="Số lượng",
        plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_h_price, use_container_width=True)
    res_price = analyze_distribution(df_clean["gia_ban"])
    st.caption(f"<b>Skewness:</b> {res_price['skewness']} | <b>Ngoại lai:</b> {res_price['outliers_count']}", unsafe_allow_html=True)

with h_col2:
    fig_h_area = px.histogram(
        df_clean,
        x="dien_tich",
        nbins=35,
        title="Phân bố diện tích (toàn bộ dữ liệu)",
        color_discrete_sequence=["#10b981"],
    )
    fig_h_area.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=35, b=30),
        xaxis_title="Diện tích (m²)",
        yaxis_title="Số lượng",
        plot_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_h_area, use_container_width=True)
    res_area = analyze_distribution(df_clean["dien_tich"])
    st.caption(f"<b>Skewness:</b> {res_area['skewness']} | <b>Ngoại lai:</b> {res_area['outliers_count']}", unsafe_allow_html=True)

with h_col3:
    st.markdown("<div style='font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 4px;'>Theo khu vực:</div>", unsafe_allow_html=True)
    sel_h_dist = st.selectbox("", sorted(summary_dist["quan_huyen"].unique()), key="h_dist_select")
    sub_dist_df = df_clean[df_clean["quan_huyen"] == sel_h_dist]

    dh_c1, dh_c2 = st.columns(2)
    with dh_c1:
        f_p_d = px.histogram(sub_dist_df, x="gia_ban", nbins=15, color_discrete_sequence=["#60a5fa"])
        f_p_d.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=20), xaxis_title="Giá", yaxis_title="")
        st.plotly_chart(f_p_d, use_container_width=True)
    with dh_c2:
        f_a_d = px.histogram(sub_dist_df, x="dien_tich", nbins=15, color_discrete_sequence=["#34d399"])
        f_a_d.update_layout(height=210, margin=dict(l=5, r=5, t=10, b=20), xaxis_title="Diện tích", yaxis_title="")
        st.plotly_chart(f_a_d, use_container_width=True)

    dist_p_stat = analyze_distribution(sub_dist_df["gia_ban"])
    st.caption(f"Khu vực <b>{sel_h_dist}</b>: Skewness = {dist_p_stat['skewness']}", unsafe_allow_html=True)

# Khối nhận xét tự sinh từ số liệu thật
st.markdown(
    f"""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 16px; margin-top: 12px; font-size: 13px; color: #334155; line-height: 1.6;">
        💡 <b>Nhận xét tự động từ số liệu thật:</b><br>
        • <b>Giá bán:</b> {res_price['comment']}<br>
        • <b>Diện tích:</b> {res_area['comment']}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

