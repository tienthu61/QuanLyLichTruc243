import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")
st.markdown("---")

# --- PHÂN LOẠI NHÂN VIÊN THEO BỘ PHẬN ---
# Bạn hãy cập nhật tên nhân viên vào đúng bộ phận bên dưới nhé
NHAN_VIEN_THEO_BOPHAN = {
    "Bán hàng": ["Đức", "Thông", "Huệ", "Hy", "Nhi", "Ngọc Anh", "Thơm"],
    "Kỹ thuật": ["Chiến", "Thành", "Thịnh", "Hùng", "Dũng"],
    "Hành chính": ["My", "Lan", "Cúc"],
    "Kho": ["Nam", "Việt"]
}

# Kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Đọc dữ liệu hiện có
try:
    existing_data = conn.read(worksheet="Sheet1")
    existing_data = existing_data.dropna(how="all")
except:
    existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

# Khu vực nhập liệu
with st.expander("➕ Nhập Báo Cáo Mới", expanded=True):
    with st.form("entry_form"):
        # 1. Định dạng Ngày dd/mm/yyyy
        date_input = st.date_input("Ngày báo cáo", datetime.now())
        date_str = date_input.strftime("%d/%m/%Y")
        
        # 2. Chọn bộ phận trước
        dept = st.selectbox("Bộ phận", list(NHAN_VIEN_THEO_BOPHAN.keys()))
        
        # 3. Lấy danh sách nhân viên tương ứng với bộ phận đã chọn
        ds_nhan_vien = NHAN_VIEN_THEO_BOPHAN[dept]
        
        # 4. Hiển thị các ô chọn nhân viên (Sắp xếp theo thứ tự yêu cầu)
        truc_trua = st.multiselect("Trực Trưa", ds_nhan_vien)
        truc_dem = st.multiselect("Trực Đêm", ds_nhan_vien)
        di_tre = st.multiselect("Đi Trễ", ds_nhan_vien)
        ve_som = st.multiselect("Về Sớm", ds_nhan_vien)
        off = st.multiselect("Nghỉ Chế Độ (Off)", ds_nhan_vien)
            
        submit_button = st.form_submit_button("Lưu dữ liệu lên hệ thống")

        if submit_button:
            new_row = pd.DataFrame([{
                "Ngày": date_str,
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre),
                "Về Sớm": ", ".join(ve_som),
                "Nghỉ (Off)": ", ".join(off)
            }])
            
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"✅ Đã lưu báo cáo ngày {date_str} cho bộ phận {dept}!")
            st.balloons()

# Khu vực tra cứu
st.markdown("---")
st.subheader("🔍 Tra Cứu Lịch Sử")
search_query = st.text_input("Tìm kiếm theo tên nhân viên hoặc ngày (vd: 30/04/2026)")

if search_query:
    filtered_df = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(existing_data.tail(10), use_container_width=True)
