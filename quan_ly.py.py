import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Vinken 243", layout="centered")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

conn = st.connection("gsheets", type=GSheetsConnection)

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

# THỨ TỰ ƯU TIÊN CỦA VINKEN
UU_TIEN = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]

with tab2:
    try:
        df_nv = conn.read(worksheet="NhanVien", ttl=0)
        # Sắp xếp cột theo thứ tự ưu tiên
        cols = [c for c in UU_TIEN if c in df_nv.columns] + [c for c in df_nv.columns if c not in UU_TIEN]
        df_nv = df_nv[cols]
        
        st.info("Nhập tên nhân viên vào các cột bên dưới:")
        edited_df = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách"):
            conn.update(worksheet="NhanVien", data=edited_df)
            st.success("✅ Đã cập nhật danh sách nhân viên!")
            st.cache_data.clear()
            st.rerun()
    except:
        st.error("Lỗi: Không tìm thấy tab 'NhanVien'. Hãy kiểm tra lại tên tab trên Google Sheets (không để dấu cách thừa).")

with tab1:
    try:
        # Đọc dữ liệu từ Sheet1
        df_main = conn.read(worksheet="Sheet1", ttl=0)
        
        with st.form("entry_form"):
            date_col = st.date_input("Ngày", datetime.now(), format="DD/MM/YYYY")
            
            # Lấy danh sách bộ phận từ tab NhanVien
            df_nv_read = conn.read(worksheet="NhanVien", ttl=0)
            list_bp = [bp for bp in UU_TIEN if bp in df_nv_read.columns]
            
            dept = st.selectbox("Bộ phận", list_bp)
            
            # Lấy danh sách NV của bộ phận đó
            list_nv = df_nv_read[dept].dropna().astype(str).tolist()
            list_nv = [n for n in list_nv if n.strip() != ""]

            truc_trua = st.multiselect("Trực Trưa", list_nv)
            truc_dem = st.multiselect("Trực Đêm", list_nv)
            off = st.multiselect("Nghỉ (Off)", list_nv)
            
            if st.form_submit_button("Gửi báo cáo"):
                new_data = pd.DataFrame([{
                    "Ngày": date_col.strftime("%d/%m/%Y"),
                    "Bộ Phận": dept,
                    "Trực Trưa": ", ".join(truc_trua),
                    "Trực Đêm": ", ".join(truc_dem),
                    "Nghỉ (Off)": ", ".join(off)
                }])
                final_df = pd.concat([df_main, new_data], ignore_index=True)
                conn.update(worksheet="Sheet1", data=final_df)
                st.success("✅ Đã lưu!")
                st.cache_data.clear()
                st.rerun()
    except:
        st.warning("Vui lòng kiểm tra tab 'Sheet1' trên Google Sheets.")

st.markdown("---")
st.subheader("🔍 Nhật Ký")
st.dataframe(conn.read(worksheet="Sheet1", ttl=0).tail(10), use_container_width=True)
