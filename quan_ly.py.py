import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Danh mục bộ phận cố định
DEPARTMENTS = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# --- HÀM ĐỌC DỮ LIỆU AN TOÀN ---
def safe_read(sheet_name, default_cols):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df.empty:
            return pd.DataFrame(columns=default_cols)
        return df
    except:
        # Nếu không tìm thấy sheet, trả về bảng trống với các cột chuẩn
        return pd.DataFrame(columns=default_cols)

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

# --- TAB 2: QUẢN LÝ NHÂN VIÊN (Sửa lỗi tại đây) ---
with tab2:
    st.subheader("Cài đặt danh sách nhân viên")
    # Đọc dữ liệu từ tab NhanVien
    df_nv = safe_read("NhanVien", DEPARTMENTS)
    
    # Đảm bảo bảng luôn có đủ 4 cột bộ phận dù trên Sheets có hay không
    for col in DEPARTMENTS:
        if col not in df_nv.columns:
            df_nv[col] = None
    
    # Chỉ hiển thị 4 cột chính theo thứ tự ưu tiên
    df_nv = df_nv[DEPARTMENTS]
    
    st.info("Nhập tên NV vào cột tương ứng. Nhấn 'Lưu' để cập nhật hệ thống.")
    
    # Giao diện chỉnh sửa bảng
    edited_nv = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True, key="nv_editor")
    
    if st.button("Lưu danh sách nhân viên"):
        try:
            conn.update(worksheet="NhanVien", data=edited_nv)
            st.success("✅ Đã cập nhật thành công!")
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error("Lỗi: Không thể ghi dữ liệu. Vui lòng kiểm tra quyền 'Editor' của link Sheets.")

# --- TAB 1: NHẬP BÁO CÁO ---
with tab1:
    df_nv_now = safe_read("NhanVien", DEPARTMENTS)
    
    # Đọc lịch sử báo cáo
    df_history = safe_read("Sheet1", ['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form"):
        date_input = st.date_input("Ngày báo cáo", datetime.now(), format="DD/MM/YYYY")
        dept = st.selectbox("Chọn bộ phận báo cáo", DEPARTMENTS)
        
        # Lấy danh sách nhân viên của bộ phận đó
        ds_nv = []
        if dept in df_nv_now.columns:
            ds_nv = df_nv_now[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "nan"]
        
        if not ds_nv:
            st.warning(f"Bộ phận {dept} chưa có nhân viên. Vui lòng thêm ở tab 'Quản Lý Nhân Viên'.")
        
        truc_trua = st.multiselect("Trực Trưa", ds_nv)
        truc_dem = st.multiselect("Trực Đêm", ds_nv)
        di_tre = st.multiselect("Đi Trễ", ds_nv)
        ve_som = st.multiselect("Về Sớm", ds_nv)
        off = st.multiselect("Nghỉ Chế Độ (Off)", ds_nv)
        
        if st.form_submit_button("Gửi báo cáo"):
            if not ds_nv:
                st.error("Không có nhân viên để báo cáo!")
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
                updated_data = pd.concat([df_history, new_entry], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_data)
                st.success("✅ Đã lưu báo cáo!")
                st.cache_data.clear()
                st.rerun()

# --- NHẬT KÝ ---
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
df_log = safe_read("Sheet1", ['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])
st.dataframe(df_log.tail(10), use_container_width=True)
