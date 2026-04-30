import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- PHẦN 1: QUẢN LÝ DANH SÁCH NHÂN VIÊN ---
# Đọc danh sách NV từ một sheet riêng tên là "NhanVien"
try:
    df_nv = conn.read(worksheet="NhanVien")
except:
    # Nếu chưa có sheet NhanVien, tạo mặc định
    df_nv = pd.DataFrame({
        "Bán hàng": ["Đức", "Thông", "Huệ", "Hy", "Nhi", "Ngọc Anh", "Thơm", ""],
        "Kỹ thuật": ["Chiến", "Thành", "Thịnh", "", "", "", "", ""],
        "Hành chính": ["My", "", "", "", "", "", "", ""],
        "Kho": ["Nam", "", "", "", "", "", "", ""]
    })

# --- GIAO DIỆN TAB ---
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    st.subheader("Cài đặt danh sách nhân viên theo bộ phận")
    st.info("Bạn nhập tên nhân viên vào các cột tương ứng bên dưới rồi nhấn Lưu.")
    edited_nv = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
    if st.button("Lưu danh sách nhân viên"):
        conn.update(worksheet="NhanVien", data=edited_nv)
        st.success("Đã cập nhật danh sách nhân viên mới!")

with tab1:
    # Đọc dữ liệu báo cáo
    try:
        existing_data = conn.read(worksheet="Sheet1")
        existing_data = existing_data.dropna(how="all")
    except:
        existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form"):
        # Ép hiển thị format ngày dd/mm/yyyy
        today = datetime.now()
        date_input = st.date_input("Ngày báo cáo", today, format="DD/MM/YYYY")
        date_str = date_input.strftime("%d/%m/%Y")
        
        # Chọn bộ phận
        list_bophan = list(df_nv.columns)
        dept = st.selectbox("Bộ phận", list_bophan)
        
        # Lấy danh sách NV ĐÚNG theo bộ phận đã chọn (loại bỏ ô trống)
        ds_nhan_vien = [x for x in df_nv[dept].tolist() if str(x) != 'nan' and str(x) != '']
        
        st.markdown(f"**Danh sách chọn cho bộ phận: {dept}**")
        
        # Các mục nhập liệu theo thứ tự bạn yêu cầu
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
            st.success(f"✅ Đã lưu báo cáo ngày {date_str} thành công!")

# Khu vực tra cứu
st.markdown("---")
st.subheader("🔍 Tra Cứu Lịch Sử")
search_query = st.text_input("Tìm kiếm (Tên NV hoặc Ngày dd/mm/yyyy)")

if search_query:
    filtered_df = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(existing_data.tail(10), use_container_width=True)
