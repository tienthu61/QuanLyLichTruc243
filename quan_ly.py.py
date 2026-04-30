import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# Kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

DEPARTMENTS = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# Tab
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

with tab1:
    # Đọc trực tiếp từ tab NhanVien
    try:
        df_nv = conn.read(worksheet="NhanVien", ttl=0)
    except:
        df_nv = pd.DataFrame(columns=DEPARTMENTS)

    # Đọc lịch sử từ Sheet1
    try:
        df_history = conn.read(worksheet="Sheet1", ttl=0)
    except:
        df_history = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form", clear_on_submit=True):
        dept = st.selectbox("Chọn bộ phận báo cáo", DEPARTMENTS)
        
        # Lấy danh sách tên
        ds_nv = []
        if dept in df_nv.columns:
            ds_nv = df_nv[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != ""]
        
        st.markdown("---")
        truc_trua = st.multiselect("☀️ Trực Trưa", ds_nv)
        truc_dem = st.multiselect("🌙 Trực Đêm", ds_nv)
        di_tre = st.multiselect("⏰ Đi Trễ", ds_nv)
        ve_som = st.multiselect("🏃 Về Sớm", ds_nv)
        off = st.multiselect("🏖️ Nghỉ (Off)", ds_nv)
        
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")
        
        if submit:
            new_entry = pd.DataFrame([{
                "Ngày": datetime.now().strftime("%d/%m/%Y"),
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre),
                "Về Sớm": ", ".join(ve_som),
                "Nghỉ (Off)": ", ".join(off)
            }])
            updated_data = pd.concat([df_history, new_entry], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_data)
            st.success("✅ Đã gửi báo cáo thành công!")
            st.balloons()

with tab2:
    st.info("💡 Vinken sửa tên nhân viên trên Google Sheets rồi nhấn 'Làm mới' nhé.")
    st.dataframe(df_nv)
    if st.button("🔄 Làm mới danh sách"):
        st.cache_data.clear()
        st.rerun()
