import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Cấu hình
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# 2. Kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HÀM LẤY DỮ LIỆU TỰ ĐỘNG THEO VỊ TRÍ (Không cần tên Tab chính xác) ---
def get_data_by_index(index):
    try:
        # Lấy danh sách tất cả các sheet có trong file
        all_sheets = conn.read(ttl=0) 
        # Nếu sếp chỉ có 1-2 sheet, ta sẽ đọc theo số thứ tự
        df = conn.read(worksheet=index, ttl=0)
        return df
    except:
        return pd.DataFrame()

# Tải dữ liệu: Sheet đầu tiên là Nhân viên, Sheet thứ hai là Báo cáo
df_nv = get_data_by_index(0) # Số 0 là Sheet nằm bên trái nhất (NhanVien)
df_history = get_data_by_index(1) # Số 1 là Sheet tiếp theo (Sheet1)

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

with tab1:
    with st.form("entry_form", clear_on_submit=True):
        col_date, col_dept = st.columns(2)
        with col_date:
            date_input = st.date_input("📅 Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
        with col_dept:
            # Lấy danh sách cột thực tế đang có trên Sheets của sếp
            available_depts = df_nv.columns.tolist() if not df_nv.empty else ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
            dept = st.selectbox("🏢 Chọn bộ phận", available_depts)
        
        ds_nv = []
        if not df_nv.empty and dept in df_nv.columns:
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
                "Ngày": date_input.strftime("%d/%m/%Y"),
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua), "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre), "Về Sớm": ", ".join(ve_som), "Nghỉ (Off)": ", ".join(off)
            }])
            updated_data = pd.concat([df_history, new_entry], ignore_index=True)
            conn.update(worksheet=1, data=updated_data) # Ghi vào sheet thứ 2
            st.success("✅ Đã lưu thành công!")
            st.balloons()
            st.cache_data.clear()

with tab2:
    if not df_nv.empty:
        st.write("✅ Đã kết nối dữ liệu thành công!")
        st.dataframe(df_nv, use_container_width=True)
    else:
        st.error("❌ Vẫn chưa thấy dữ liệu. Vinken kiểm tra lại file Sheets xem có nội dung chưa nhé.")
    
    if st.button("🔄 Cập nhật danh sách"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.subheader("🔍 Nhật ký gần đây")
if not df_history.empty:
    st.table(df_history.tail(5))
