import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Cấu hình giao diện chuẩn Vinken 243
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# 2. Kết nối Google Sheets (Dùng cấu hình Secrets của sếp)
conn = st.connection("gsheets", type=GSheetsConnection)

DEPARTMENTS = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# --- HÀM LẤY DỮ LIỆU "ÉP BUỘC" (Để không bị empty) ---
def get_data(sheet_name):
    try:
        # ttl=0 ép App không được dùng bộ nhớ đệm, phải tải mới hoàn toàn
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception:
        return pd.DataFrame()

# Khởi tạo Tabs
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

# Đọc dữ liệu sẵn cho cả 2 tab
df_nv = get_data("NhanVien")
df_history = get_data("Sheet1")

# --- TAB 1: NHẬP BÁO CÁO ---
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        # ĐƯA NGÀY BÁO CÁO TRỞ LẠI ĐÂY RỒI SẾP NHÉ
        col_date, col_dept = st.columns(2)
        with col_date:
            date_input = st.date_input("📅 Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
        with col_dept:
            dept = st.selectbox("🏢 Chọn bộ phận báo cáo", DEPARTMENTS)
        
        # Lấy danh sách tên từ Sheets
        ds_nv = []
        if not df_nv.empty and dept in df_nv.columns:
            ds_nv = df_nv[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "nan"]
        
        if not ds_nv:
            st.warning(f"⚠️ Chưa thấy tên NV bộ phận {dept}. Sếp kiểm tra lại tab NhanVien trên Sheets nhé!")
        
        st.markdown("---")
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
            if not ds_nv and not truc_trua and not truc_dem:
                st.error("Chưa có thông tin để lưu sếp ơi!")
            else:
                new_entry = pd.DataFrame([{
                    "Ngày": date_input.strftime("%d/%m/%Y"),
                    "Bộ Phận": dept,
                    "Trực Trưa": ", ".join(truc_trua),
                    "Trực Đêm": ", ".join(truc_dem),
                    "Đi Trễ": ", ".join(di_tre),
                    "Về Sớm": ", ".join(ve_som),
                    "Nghỉ (Off)": ", ".join(off)
                }])
                # Lưu vào Sheet1
                updated_data = pd.concat([df_history, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_data)
                st.success(f"✅ Đã lưu báo cáo ngày {date_input.strftime('%d/%m/%Y')} thành công!")
                st.balloons()
                st.cache_data.clear()

# --- TAB 2: DANH SÁCH NHÂN VIÊN ---
with tab2:
    st.info("💡 Vinken sửa tên trên Sheets rồi nhấn nút bên dưới để App cập nhật nhé.")
    if not df_nv.empty:
        st.dataframe(df_nv, use_container_width=True)
    else:
        st.error("❌ App chưa đọc được dữ liệu. Sếp kiểm tra tên Tab trên Sheets có đúng là 'NhanVien' chưa?")
    
    if st.button("🔄 Cập nhật danh sách mới nhất"):
        st.cache_data.clear()
        st.rerun()

# --- NHẬT KÝ BÁO CÁO ---
st.markdown("---")
st.subheader("🔍 Nhật ký 5 báo cáo gần đây")
if not df_history.empty:
    st.table(df_history.tail(5))
