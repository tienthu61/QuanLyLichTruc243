import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Thứ tự bộ phận ưu tiên
DEPARTMENTS = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

# --- TAB 1: NHẬP BÁO CÁO ---
with tab1:
    try:
        # Luôn đọc dữ liệu mới nhất, nếu lỗi thì tạo DataFrame trống để không treo App
        df_nv = conn.read(worksheet="NhanVien", ttl=0)
        
        with st.form("form_entry"):
            date_col = st.date_input("Ngày trực", datetime.now(), format="DD/MM/YYYY")
            dept_col = st.selectbox("Chọn Bộ Phận", DEPARTMENTS)
            
            # Lấy danh sách tên từ cột tương ứng trong sheet NhanVien
            names_list = []
            if dept_col in df_nv.columns:
                names_list = df_nv[dept_col].dropna().astype(str).tolist()
                names_list = [n.strip() for n in names_list if n.strip() != "" and n.lower() != "nan"]
            
            truc_trua = st.multiselect("Nhân viên Trực Trưa", names_list)
            truc_dem = st.multiselect("Nhân viên Trực Đêm", names_list)
            nghi_off = st.multiselect("Nhân viên Nghỉ (Off)", names_list)
            
            if st.form_submit_button("Gửi báo cáo"):
                # Ghi vào Sheet1
                df_history = conn.read(worksheet="Sheet1", ttl=0)
                new_record = pd.DataFrame([{
                    "Ngày": date_col.strftime("%d/%m/%Y"),
                    "Bộ Phận": dept_col,
                    "Trực Trưa": ", ".join(truc_trua),
                    "Trực Đêm": ", ".join(truc_dem),
                    "Nghỉ (Off)": ", ".join(nghi_off)
                }])
                updated_history = pd.concat([df_history, new_record], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_history)
                st.success("✅ Đã gửi báo cáo thành công!")
                st.balloons()
    except Exception as e:
        st.error("Chưa tìm thấy dữ liệu. Vinken hãy kiểm tra Tab 'NhanVien' trên Sheets nhé.")

# --- TAB 2: QUẢN LÝ NHÂN VIÊN ---
with tab2:
    st.subheader("Danh sách nhân viên")
    try:
        df_edit = conn.read(worksheet="NhanVien", ttl=0)
        
        # Đảm bảo hiển thị đủ 4 cột bộ phận
        for col in DEPARTMENTS:
            if col not in df_edit.columns:
                df_edit[col] = None
        
        df_edit = df_edit[DEPARTMENTS] # Sắp xếp đúng thứ tự
        
        st.write("Vinken có thể sửa trực tiếp trong bảng dưới đây:")
        new_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách"):
            try:
                conn.update(worksheet="NhanVien", data=new_df)
                st.success("✅ Đã cập nhật danh sách nhân viên!")
                st.cache_data.clear()
            except:
                st.error("❌ Lỗi quyền ghi. Vinken hãy dùng link sạch (không có ?usp=sharing) trong Secrets nhé.")
    except:
        st.warning("Vui lòng tạo Tab 'NhanVien' trên Google Sheets.")

# --- NHẬT KÝ ---
st.markdown("---")
try:
    st.subheader("🔍 Nhật Ký Gần Đây")
    df_log = conn.read(worksheet="Sheet1", ttl=0)
    st.dataframe(df_log.tail(10), use_container_width=True)
except:
    st.write("Chưa có lịch sử báo cáo.")
