import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Cấu hình giao diện chuẩn Vinken 243
st.set_page_config(page_title="Vinken 243 - Lịch Trực", layout="centered")

# Thêm logo hoặc tiêu đề có icon
st.markdown("<h1 style='text-align: center;'>📋 Quản Lý Lịch Trực Tiến Thu 243</h1>", unsafe_allow_html=True)

# 2. Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Danh mục bộ phận tại trạm 243
DEPARTMENTS = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# --- HÀM ĐỌC DỮ LIỆU TỐI ƯU ---
def load_data(sheet_name, default_cols):
    try:
        # ttl=0 để luôn lấy dữ liệu mới nhất mỗi khi tải lại App
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df.empty:
            return pd.DataFrame(columns=default_cols)
        return df
    except:
        return pd.DataFrame(columns=default_cols)

# Khởi tạo Tabs
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Danh Sách Nhân Viên"])

# --- TAB 1: NHẬP BÁO CÁO (Trọng tâm) ---
with tab1:
    # Đọc danh sách nhân viên từ tab NhanVien
    df_nv = load_data("NhanVien", DEPARTMENTS)
    
    # Đọc lịch sử báo cáo để lưu nối tiếp
    df_history = load_data("Sheet1", ['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
        with col2:
            dept = st.selectbox("Chọn bộ phận báo cáo", DEPARTMENTS)
        
        # Lấy danh sách tên từ cột bộ phận tương ứng trên Sheets
        ds_nv = []
        if dept in df_nv.columns:
            # Lọc bỏ các dòng trống (None/NaN)
            ds_nv = df_nv[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "nan"]
        
        if not ds_nv:
            st.warning(f"⚠️ Bộ phận {dept} chưa có tên nhân viên trên Sheets.")
        
        st.markdown("---")
        # Các mục nhập liệu chính
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
            if not ds_nv:
                st.error("Không có dữ liệu nhân viên để gửi!")
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
                # Lưu dữ liệu
                updated_data = pd.concat([df_history, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_data)
                st.success("✅ Đã gửi báo cáo thành công lên Google Sheets!")
                st.balloons()
                st.cache_data.clear()

# --- TAB 2: QUẢN LÝ NHÂN VIÊN (Đơn giản hóa) ---
with tab2:
    st.subheader("Cài đặt nhân viên trạm 243")
    st.info("💡 Vinken hãy nhập tên nhân viên trực tiếp vào file Google Sheets, sau đó quay lại đây nhấn 'Làm mới'.")
    
    # Hiển thị bảng nhân viên hiện tại (chỉ đọc)
    current_nv = load_data("NhanVien", DEPARTMENTS)
    st.dataframe(current_nv, use_container_width=True)
    
    # Nút bấm mở nhanh file Sheets và nút làm mới
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.link_button("📂 Mở file Google Sheets", "https://docs.google.com/spreadsheets/d/10EkGJvALUo7KWIRToY7L7h-dKA7HKG3D1WCzD7SOH-g/edit")
    with col_btn2:
        if st.button("🔄 Làm mới danh sách"):
            st.cache_data.clear()
            st.rerun()

# --- PHẦN NHẬT KÝ (Luôn hiện ở cuối) ---
st.markdown("---")
st.subheader("🔍 Nhật Ký 10 Báo Cáo Gần Nhất")
df_log = load_data("Sheet1", ['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])
if not df_log.empty:
    st.table(df_log.tail(10))
else:
    st.write("Chưa có báo cáo nào được ghi nhận.")
