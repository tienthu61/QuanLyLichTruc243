import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cấu hình thứ tự ưu tiên của Vinken
UU_TIEN = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# --- HÀM HỖ TRỢ ĐỌC DỮ LIỆU AN TOÀN ---
def safe_read(sheet_name, default_cols):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(columns=default_cols)
        return df
    except:
        return pd.DataFrame(columns=default_cols)

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

# --- TAB 2: QUẢN LÝ NHÂN VIÊN ---
with tab2:
    # Nếu chưa có tab NhanVien, app sẽ tự tạo bảng trống với các cột ưu tiên
    df_nv = safe_read("NhanVien", UU_TIEN)
    
    # Đảm bảo các cột ưu tiên luôn nằm đầu tiên
    existing_cols = [c for c in UU_TIEN if c in df_nv.columns]
    other_cols = [c for c in df_nv.columns if c not in UU_TIEN]
    df_nv = df_nv[existing_cols + other_cols]
    
    st.info("Nhập tên nhân viên vào các cột bên dưới (mỗi dòng 1 người):")
    edited_df = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
    
    if st.button("Lưu danh sách nhân viên"):
        conn.update(worksheet="NhanVien", data=edited_df)
        st.success("✅ Đã cập nhật danh sách!")
        st.cache_data.clear()
        st.rerun()

# --- TAB 1: NHẬP BÁO CÁO ---
with tab1:
    # Cột mặc định cho Sheet1
    cols_main = ["Ngày", "Bộ Phận", "Trực Trưa", "Trực Đêm", "Nghỉ (Off)"]
    df_main = safe_read("Sheet1", cols_main)
    
    with st.form("entry_form"):
        date_col = st.date_input("Chọn Ngày", datetime.now(), format="DD/MM/YYYY")
        
        # Lấy danh sách bộ phận từ dữ liệu nhân viên
        df_nv_current = safe_read("NhanVien", UU_TIEN)
        available_depts = [bp for bp in UU_TIEN if bp in df_nv_current.columns]
        
        if not available_depts:
            st.warning("⚠️ Hãy qua tab 'Quản Lý Nhân Viên' để thiết lập trước.")
            st.stop()
            
        dept = st.selectbox("Chọn Bộ Phận", available_depts)
        
        # Lấy danh sách nhân viên của bộ phận đó, loại bỏ ô trống
        list_nv = df_nv_current[dept].dropna().astype(str).tolist()
        list_nv = [n.strip() for n in list_nv if n.strip() != "" and n.lower() != "nan"]

        truc_trua = st.multiselect("Nhân viên Trực Trưa", list_nv)
        truc_dem = st.multiselect("Nhân viên Trực Đêm", list_nv)
        off = st.multiselect("Nhân viên Nghỉ (Off)", list_nv)
        
        if st.form_submit_button("Gửi báo cáo"):
            new_row = pd.DataFrame([{
                "Ngày": date_col.strftime("%d/%m/%Y"),
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Nghỉ (Off)": ", ".join(off)
            }])
            # Kết hợp dữ liệu cũ và mới
            final_df = pd.concat([df_main, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=final_df)
            st.success("✅ Đã lưu báo cáo thành công!")
            st.cache_data.clear()
            st.rerun()

# --- PHẦN NHẬT KÝ ---
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực (10 dòng mới nhất)")
# Hiển thị an toàn, nếu chưa có dữ liệu thì hiện bảng trống
df_history = safe_read("Sheet1", cols_main)
st.dataframe(df_history.tail(10), use_container_width=True)
