import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Cấu hình
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# 2. Kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HÀM LẤY DỮ LIỆU ---
def get_data_by_index(index):
    try:
        return conn.read(worksheet=index, ttl=0)
    except:
        return pd.DataFrame()

df_nv = get_data_by_index(0) # Tab Nhân viên
df_history = get_data_by_index(1) # Tab Sheet1

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        col_date, col_dept = st.columns(2)
        with col_date:
            date_input = st.date_input("📅 Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
        with col_dept:
            # Tự động lấy danh sách bộ phận từ tiêu đề cột của sếp
            available_depts = df_nv.columns.tolist() if not df_nv.empty else ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
            dept = st.selectbox("🏢 Chọn bộ phận", available_depts)
        
        # Lấy danh sách nhân viên CHÍNH XÁC theo bộ phận đã chọn
        ds_nv = []
        if not df_nv.empty and dept in df_nv.columns:
            # Loại bỏ các ô trống (None/NaN)
            ds_nv = df_nv[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "none" and n.lower() != "nan"]
        
        st.markdown("---")
        # THÊM KEY ĐỂ ÉP APP CẬP NHẬT DANH SÁCH MỚI KHI ĐỔI BỘ PHẬN
        truc_trua = st.multiselect("☀️ Trực Trưa", ds_nv, key=f"trua_{dept}")
        truc_dem = st.multiselect("🌙 Trực Đêm", ds_nv, key=f"dem_{dept}")
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            di_tre = st.multiselect("⏰ Đi Trễ", ds_nv, key=f"tre_{dept}")
        with col_b:
            ve_som = st.multiselect("🏃 Về Sớm", ds_nv, key=f"som_{dept}")
        with col_c:
            off = st.multiselect("🏖️ Nghỉ (Off)", ds_nv, key=f"off_{dept}")
        
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")
        
        if submit:
            new_entry = pd.DataFrame([{
                "Ngày": date_input.strftime("%d/%m/%Y"),
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre),
                "Về Sớm": ", ".join(ve_som),
                "Nghỉ (Off)": ", ".join(off)
            }])
            updated_data = pd.concat([df_history, new_entry], ignore_index=True)
            conn.update(worksheet=1, data=updated_data)
            st.success(f"✅ Đã lưu báo cáo bộ phận {dept} thành công!")
            st.balloons()
            st.cache_data.clear()

with tab2:
    if not df_nv.empty:
        st.write("✅ Đã kết nối dữ liệu thành công!")
        st.dataframe(df_nv, use_container_width=True)
    
    if st.button("🔄 Cập nhật danh sách mới nhất"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.subheader("🔍 Nhật ký gần đây")
if not df_history.empty:
    st.table(df_history.tail(5))
