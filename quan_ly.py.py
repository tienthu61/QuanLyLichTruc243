import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken Management", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")
st.markdown("---")

# Kết nối với Google Sheets
# Bạn sẽ dán link Google Sheet vào phần cấu hình sau
conn = st.connection("gsheets", type=GSheetsConnection)

# Đọc dữ liệu hiện có
try:
    existing_data = conn.read(worksheet="Sheet1", usecols=list(range(7)))
    existing_data = existing_data.dropna(how="all")
except:
    existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Off'])

# Khu vực nhập liệu (Giao diện cột để tiết kiệm không gian trên ĐT)
with st.expander("➕ Nhập Báo Cáo Mới", expanded=True):
    with st.form("entry_form"):
        date = st.date_input("Ngày báo cáo", datetime.now())
        dept = st.selectbox("Bộ phận", ["Bán hàng", "Kỹ thuật", "Hành chính", "Kho"])
        
        col1, col2 = st.columns(2)
        with col1:
            truc_trua = st.text_input("Trực trưa")
            truc_dem = st.text_input("Trực đêm")
            di_tre = st.text_input("Đi trễ")
        with col2:
            ve_som = st.text_input("Về sớm")
            off = st.text_input("Nghỉ (Off)")
            
        submit_button = st.form_submit_button("Lưu dữ liệu lên hệ thống")

        if submit_button:
            new_row = pd.DataFrame([{
                "Ngày": date.strftime("%d/%m/%Y"),
                "Bộ Phận": dept,
                "Trực Trưa": truc_trua,
                "Trực Đêm": truc_dem,
                "Đi Trễ": di_tre,
                "Về Sớm": ve_som,
                "Off": off
            }])
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ Đã lưu dữ liệu thành công!")
            st.balloons()

# Khu vực tra cứu
st.markdown("---")
st.subheader("🔍 Lịch Sử Trực")
search_query = st.text_input("Tìm kiếm (Nhập tên NV hoặc Tháng/Năm)")

if search_query:
    filtered_df = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(existing_data.tail(10), use_container_width=True)