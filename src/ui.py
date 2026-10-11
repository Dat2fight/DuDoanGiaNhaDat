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

        /* Sidebar màu navy đậm */
        [data-testid="stSidebar"] {
            background-color: #0f172a !important;
            color: #f8fafc !important;
        }
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span {
            color: #cbd5e1 !important;
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


def render_top_badge(title: str = "Bài tập lớn môn Khoa học Dữ liệu"):
    """Hiển thị huy hiệu góc phải phía trên."""
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
            <div class="top-badge">
                <span>🎓</span> {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

