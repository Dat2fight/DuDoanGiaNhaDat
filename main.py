"""Entry point chính – dùng st.navigation() để đặt tên sidebar có dấu tiếng Việt."""

import streamlit as st

# set_page_config phải gọi TRƯỚC st.navigation() và chỉ 1 lần duy nhất
st.set_page_config(
    page_title="HouseInsight",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Khai báo navigation với tên hiển thị đầy đủ tiếng Việt + emoji
pages = st.navigation(
    [
        st.Page("app.py",               title="🏠 Trang chủ"),
        st.Page("pages/1_Du_lieu.py",   title="📂 Dữ liệu"),
        st.Page("pages/2_Thong_ke.py",  title="📊 Thống kê"),
        st.Page("pages/3_Phan_cum.py",  title="🧩 Phân cụm"),
        st.Page("pages/4_Du_doan_gia.py", title="🔮 Dự đoán giá"),
    ]
)
pages.run()
