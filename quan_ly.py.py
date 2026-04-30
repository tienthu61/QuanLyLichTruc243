import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

conn = st.connection("gsheets", type=GSheetsConnection)

# Thứ tự bộ phận ưu tiên của sếp Vinh
UU_TIEN = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    try:
        # ttl=0 giúp app luôn đọc dữ liệu mới nhất từ Google Sheets
        df_nv = conn.read(worksheet="NhanVien", ttl=0)
        
        # Đảm bảo các cột đúng thứ tự sếp muốn
        cols = [c for c in UU_TIEN if c in df_nv.columns] + [c for c in df_nv.columns if c not in UU_TIEN]
        df_nv = df_nv[cols]
        
        st.info("Nhập tên nhân viên vào cột tương ứng:")
        edited_df = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách nhân viên"):
            try:
                conn.update(worksheet="NhanVien", data=edited_df)
                st.success("✅ Đã cập nhật thành công!")
                st.cache_data.clear() # Xóa cache để tab Nhập báo cáo thấy tên mới ngay
                st.rerun()
            except Exception as e:
                st.error("Lỗi: Bạn chưa chuyển quyền sang 'Editor' trên Google Sheets.")
    except:
        st.error("Không tìm thấy tab 'NhanVien'. Vui lòng kiểm tra lại tên tab trên Google Sheets.")

with tab1:
    try:
        df_nv_current = conn.read(worksheet="NhanVien", ttl=0)
        # Lấy danh sách bộ phận (cột)
        list_bp = [bp for bp in UU_TIEN if bp in df_nv_current.columns]
        
        with st.form("entry_form"):
            date_input = st.date_input("Ngày trực", datetime.now(), format="DD/MM/YYYY")
            dept = st.selectbox("Chọn Bộ Phận", list_bp)
            
            # Lấy tên NV từ cột tương ứng, bỏ các ô trống
            ds_nv = df_nv_current[dept].dropna().astype(str).tolist()
            ds_nv = [n.strip() for n in ds_nv if n.strip() != "" and n.lower() != "nan"]

            truc_trua = st.multiselect("Nhân viên Trực Trưa", ds_nv)
            truc_dem = st.multiselect("Nhân viên Trực Đêm", ds_nv)
            off = st.multiselect("Nhân viên Nghỉ (Off)", ds_nv)
            
            if st.form_submit_button("Gửi báo cáo"):
                # Đọc Sheet1 để nối tiếp dữ liệu
                df_main = conn.read(worksheet="Sheet1", ttl=0)
                new_row = pd.DataFrame([{
                    "Ngày": date_input.strftime("%d/%m/%Y"),
                    "Bộ Phận": dept,
                    "Trực Trưa": ", ".join(truc_trua),
                    "Trực Đêm": ", ".join(truc_dem),
                    "Nghỉ (Off)": ", ".join(off)
                }])
                final_df = pd.concat([df_main, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=final_df)
                st.success("✅ Đã lưu báo cáo!")
                st.cache_data.clear()
                st.rerun()
    except:
        st.warning("⚠️ Đang đợi dữ liệu từ tab NhanVien hoặc Sheet1...")

st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
try:
    st.dataframe(conn.read(worksheet="Sheet1", ttl=0).tail(10), use_container_width=True)
except:
    st.write("Chưa có dữ liệu nhật ký.")
