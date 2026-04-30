import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Cấu hình giao diện
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# 2. Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(index):
    try:
        return conn.read(worksheet=index, ttl=0)
    except:
        return pd.DataFrame()

df_nv = get_data(0)  # Sheet Nhân viên
df_history = get_data(1)  # Sheet Nhật ký

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

with tab1:
    # --- PHẦN CHỌN BỘ PHẬN (ĐƯA RA NGOÀI FORM ĐỂ CẬP NHẬT TỨC THÌ) ---
    col_date, col_dept = st.columns(2)
    with col_date:
        date_input = st.date_input("📅 Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
    with col_dept:
        available_depts = df_nv.columns.tolist() if not df_nv.empty else ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        # Khi chọn bộ phận ở đây, cả trang web sẽ load lại danh sách nhân viên tương ứng
        dept_selected = st.selectbox("🏢 Chọn bộ phận", available_depts)

    # Lấy danh sách nhân viên theo bộ phận đã chọn
    ds_nv = []
    if not df_nv.empty and dept_selected in df_nv.columns:
        ds_nv = df_nv[dept_selected].dropna().astype(str).tolist()
        ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "none" and n.lower() != "nan"]

    # --- PHẦN NHẬP CHI TIẾT (NẰM TRONG FORM) ---
    with st.form("entry_form", clear_on_submit=True):
        st.markdown(f"### 📋 Đang lập báo cáo cho: **{dept_selected}**")
        
        truc_trua = st.multiselect("☀️ Trực Trưa", ds_nv)
        truc_dem = st.multiselect("🌙 Trực Đêm", ds_nv)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            di_tre = st.multiselect("⏰ Đi Trễ", ds_nv)
        with col_b:
            ve_som = st.multiselect("🏃 Về Sớm", ds_nv)
        with col_c:
            off = st.multiselect("🏖️ Nghỉ (Off)", ds_nv)
        
        submit = st.form_submit_button("🚀 GỬI BÁO CÁO")
        
        if submit:
            new_entry = pd.DataFrame([{
                "Ngày": date_input.strftime("%d/%m/%Y"),
                "Bộ Phận": dept_selected,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre),
                "Về Sớm": ", ".join(ve_som),
                "Nghỉ (Off)": ", ".join(off)
            }])
            updated_data = pd.concat([df_history, new_entry], ignore_index=True)
            conn.update(worksheet=1, data=updated_data)
            st.success(f"✅ Đã lưu báo cáo {dept_selected} thành công!")
            st.balloons()
            st.cache_data.clear()

with tab2:
    if not df_nv.empty:
        st.write("✅ Dữ liệu nhân viên hiện tại:")
        st.dataframe(df_nv, use_container_width=True)
    
    if st.button("🔄 Làm mới dữ liệu từ Sheets"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.subheader("🔍 Nhật ký gần đây")
if not df_history.empty:
    st.table(df_history.tail(5))
