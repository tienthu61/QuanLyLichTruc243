import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Thứ tự bộ phận ưu tiên của sếp Vinh
UU_TIEN = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

# Hàm đọc dữ liệu an toàn để tránh lỗi "Đang đợi dữ liệu"
def get_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except:
        return pd.DataFrame()

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

# --- TAB 2: QUẢN LÝ NHÂN VIÊN ---
with tab2:
    df_nv = get_data("NhanVien")
    
    # Nếu sheet trống, tạo khung mặc định
    if df_nv.empty:
        df_nv = pd.DataFrame(columns=UU_TIEN)
    
    # Sắp xếp lại cột theo thứ tự ưu tiên
    cols = [c for c in UU_TIEN if c in df_nv.columns] + [c for c in df_nv.columns if c not in UU_TIEN]
    df_nv = df_nv[cols]
    
    st.info("💡 Nhập tên nhân viên vào cột tương ứng (mỗi dòng 1 tên).")
    edited_df = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True, key="editor_nv")
    
    if st.button("Lưu danh sách nhân viên"):
        conn.update(worksheet="NhanVien", data=edited_df)
        st.success("✅ Đã cập nhật danh sách thành công!")
        st.cache_data.clear()
        st.rerun()

# --- TAB 1: NHẬP BÁO CÁO ---
with tab1:
    df_nv_read = get_data("NhanVien")
    
    if not df_nv_read.empty:
        available_depts = [bp for bp in UU_TIEN if bp in df_nv_read.columns]
        
        with st.form("form_bao_cao"):
            date_sel = st.date_input("Ngày", datetime.now(), format="DD/MM/YYYY")
            dept_sel = st.selectbox("Chọn Bộ Phận", available_depts)
            
            # Lấy danh sách NV của bộ phận đã chọn
            list_names = df_nv_read[dept_sel].dropna().astype(str).tolist()
            list_names = [n.strip() for n in list_names if n.strip() != "" and n.lower() != "nan"]
            
            t_trua = st.multiselect("Nhân viên Trực Trưa", list_names)
            t_dem = st.multiselect("Nhân viên Trực Đêm", list_names)
            off_list = st.multiselect("Nhân viên Nghỉ (Off)", list_names)
            
            if st.form_submit_button("Gửi báo cáo"):
                df_main = get_data("Sheet1")
                new_row = pd.DataFrame([{
                    "Ngày": date_sel.strftime("%d/%m/%Y"),
                    "Bộ Phận": dept_sel,
                    "Trực Trưa": ", ".join(t_trua),
                    "Trực Đêm": ", ".join(t_dem),
                    "Nghỉ (Off)": ", ".join(off_list)
                }])
                final_main = pd.concat([df_main, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=final_main)
                st.success("✅ Đã gửi báo cáo!")
                st.cache_data.clear()
                st.rerun()
    else:
        st.warning("⚠️ Vui lòng sang tab 'Quản Lý Nhân Viên' nhập tên nhân viên trước!")

# --- PHẦN NHẬT KÝ ---
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
df_log = get_data("Sheet1")
if not df_log.empty:
    st.dataframe(df_log.tail(10), use_container_width=True)
else:
    st.write("Chưa có dữ liệu nhật ký.")
