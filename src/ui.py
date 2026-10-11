"""Module chứa các hàm tiện ích giao diện UI/UX và CSS theo mockup HouseInsight."""

import streamlit as st


def apply_custom_css():
    """Áp dụng CSS tùy chỉnh để giao diện bám sát mockup thiết kế."""
    st.markdown(
        """
        <style>
        /* Toàn bộ phông chữ và nền */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Ẩn header mặc định của Streamlit nhưng giữ menu nếu cần */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
            z-index: 1;
        }

        /* Sidebar màu navy đậm & toàn bộ chữ mặc định */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stMarkdown span {
            color: #cbd5e1 !important;
        }

        /* Chuyển các chữ trong menu điều hướng Sidebar thành màu trắng rõ nét */
        [data-testid="stSidebarNav"] {
            background-color: transparent !important;
            padding-top: 8px !important;
        }
        [data-testid="stSidebarNav"] ul {
            padding: 0 !important;
        }
        [data-testid="stSidebarNav"] li {
            margin-bottom: 4px !important;
        }
        [data-testid="stSidebarNav"] a,
        [data-testid="stSidebarNav"] a span,
        [data-testid="stSidebarNavItems"] a,
        [data-testid="stSidebarNavItems"] a span,
        [data-testid="stSidebarNavLink"],
        [data-testid="stSidebarNavLink"] span,
        section[data-testid="stSidebar"] nav a,
        section[data-testid="stSidebar"] nav a span,
        section[data-testid="stSidebar"] nav ul li a,
        section[data-testid="stSidebar"] nav ul li a span {
            color: #ffffff !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
        }

        /* Hiệu ứng hover menu */
        [data-testid="stSidebarNav"] a:hover,
        [data-testid="stSidebarNav"] a:hover span,
        [data-testid="stSidebarNavLink"]:hover,
        [data-testid="stSidebarNavLink"]:hover span,
        section[data-testid="stSidebar"] nav ul li a:hover {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.12) !important;
            border-radius: 8px !important;
        }

        /* Tab trang đang được chọn (Active) */
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a[aria-current="page"] span,
        [data-testid="stSidebarNavLink"][aria-current="page"],
        [data-testid="stSidebarNavLink"][aria-current="page"] span,
        section[data-testid="stSidebar"] nav ul li a[aria-current="page"],
        section[data-testid="stSidebar"] nav ul li a[aria-current="page"] span {
            color: #ffffff !important;
            font-weight: 700 !important;
            background-color: #2563eb !important;
            border-radius: 8px !important;
        }

        /* Icon SVG trong sidebar nav */
        [data-testid="stSidebarNav"] svg,
        [data-testid="stSidebarNavLink"] svg {
            fill: #ffffff !important;
            color: #ffffff !important;
        }

        /* Định kiểu ô Selectbox: nền trắng, chữ đen, viền rõ nét */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            color: #0f172a !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }

        /* Chữ bên trong ô Selectbox */
        div[data-baseweb="select"] * {
            color: #0f172a !important;
        }

        /* Mũi tên góc phải của Selectbox */
        div[data-baseweb="select"] svg {
            fill: #475569 !important;
        }

        /* Danh sách dropdown khi bấm mở ô chọn */
        ul[data-testid="stSelectboxVirtualDropdown"],
        div[data-baseweb="popover"] {
            background-color: #ffffff !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li,
        div[data-baseweb="menu"] li {
            background-color: #ffffff !important;
            color: #0f172a !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
        div[data-baseweb="menu"] li:hover {
            background-color: #f1f5f9 !important;
            color: #2563eb !important;
        }

        /* Nhãn Label của các widget / selectbox */
        div[data-testid="stWidgetLabel"] p,
        label[data-testid="stWidgetLabel"] {
            color: #0f172a !important;
            font-weight: 600 !important;
        }

        /* Thẻ Card bo góc */
        .hi-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        }

        /* Thẻ Metric */
        .metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            align-items: center;
            gap: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        .metric-icon {
            width: 48px;
            height: 48px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }
        .metric-label {
            font-size: 13px;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 2px;
        }
        .metric-value {
            font-size: 22px;
            font-weight: 700;
            color: #0f172a;
        }

        /* Badge góc trên phải */
        .top-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            background: #e0f2fe;
            color: #0369a1;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            float: right;
        }

        /* Tiêu đề trang */
        .page-header {
            margin-bottom: 20px;
        }
        .page-title {
            font-size: 24px;
            font-weight: 700;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }
        .page-subtitle {
            font-size: 14px;
            color: #64748b;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #0369a1 100%);
            border-radius: 16px;
            padding: 36px 32px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(30, 58, 138, 0.2);
            position: relative;
            overflow: hidden;
        }
        .hero-banner h1 {
            font-size: 28px;
            font-weight: 800;
            color: #ffffff !important;
            margin-bottom: 12px;
        }
        .hero-banner p {
            font-size: 15px;
            color: #e2e8f0 !important;
            max-width: 650px;
            line-height: 1.6;
            margin-bottom: 0;
        }

        /* Khối hướng dẫn sử dụng */
        .guide-step {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 16px;
            height: 100%;
        }
        .guide-step-num {
            display: inline-flex;
            width: 28px;
            height: 28px;
            background: #dbeafe;
            color: #2563eb;
            border-radius: 50%;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            margin-bottom: 10px;
        }
        .guide-step-title {
            font-weight: 600;
            font-size: 15px;
            color: #0f172a;
            margin-bottom: 4px;
        }
        .guide-step-desc {
            font-size: 13px;
            color: #64748b;
        }

        /* Footer ghi chú */
        .footer-note {
            font-size: 12px;
            color: #64748b;
            padding: 16px 0;
            border-top: 1px solid #e2e8f0;
            margin-top: 32px;
            display: flex;
            justify-content: space-between;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_info():
    """Hiển thị logo, thông tin khu vực và footer trong sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 20px 0; border-bottom: 1px solid #334155;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">🏠</span>
                    <div>
                        <div style="font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px;">HouseInsight</div>
                        <div style="font-size: 11px; color: #94a3b8;">Phân tích & Dự đoán giá nhà Hà Nội</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="position: fixed; bottom: 20px; left: 16px; width: calc(var(--sidebar-width) - 32px); font-size: 12px; color: #94a3b8; border-top: 1px solid #334155; padding-top: 12px;">
                <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
                    <span>📍</span> <b style="color: #f1f5f9;">Hà Nội</b>
                </div>
                <div>Nguồn: <i>alonhadat.com.vn</i></div>
                <div>Thu thập: <i>11/10/2026</i></div>
            </div>
            """,
            unsafe_allow_html=True,
        )