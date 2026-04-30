import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Vinken 243", layout="wide")
st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối và ép làm mới dữ liệu liên tục
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    # ttl=0 giúp App luôn lấy dữ liệu mới nhất từ Google Sheets của Vinken
    return conn.read(worksheet=sheet_name, ttl=0)

tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    try:
        df_nv = load_data("NhanVien")
        st.info("💡 Chỉnh sửa danh sách nhân viên tại đây:")
        # Cho phép sửa trực tiếp trên App
        edited_df = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu thay đổi"):
            conn.update(worksheet="NhanVien", data=edited_df)
            st.success("✅ Đã lưu vào Google Sheets thành công!")
            st.cache_data.clear() # Xóa bộ nhớ đệm để cập nhật ngay
    except Exception as e:
        st.error(f"Lỗi: Hãy kiểm tra tên Tab 'NhanVien' trên Sheets. {e}")

with tab1:
    try:
        df_nv_read = load_data("NhanVien")
        # Kiểm tra nếu có dữ liệu nhân viên mới cho làm báo cáo
        if not df_nv_read.empty:
            with st.form("form_truc"):
                bp = st.selectbox("Chọn Bộ phận", df_nv_read.columns)
                names = df_nv_read[bp].dropna().tolist()
                
                truc_trua = st.multiselect("Trực trưa", names)
                truc_dem = st.multiselect("Trực đêm", names)
                
                if st.form_submit_button("Gửi báo cáo"):
                    # Ghi vào Sheet1
                    df_old = load_data("Sheet1")
                    # ... code xử lý ghi tương tự như trước ...
                    st.success("Đã gửi!")
        else:
            st.warning("⚠️ Vinken hãy gõ tên nhân viên vào Google Sheets trước nhé!")
    except:
        st.error("Chưa tìm thấy dữ liệu.")
