import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- GIAO DIỆN TAB ---
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    st.subheader("Cài đặt danh sách nhân viên")
    try:
        # Đọc danh sách NV từ sheet "NhanVien"
        df_nv = conn.read(worksheet="NhanVien")
        st.info("Nhập tên NV vào cột tương ứng. Để xóa NV, chỉ cần xóa tên trong ô đó.")
        
        # Đảm bảo thứ tự cột ở Tab quản lý cũng chuẩn theo ý bạn
        cols_order = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        # Chỉ lấy những cột tồn tại trong sheet để tránh lỗi
        available_cols = [c for c in cols_order if c in df_nv.columns]
        other_cols = [c for c in df_nv.columns if c not in cols_order]
        df_nv = df_nv[available_cols + other_cols]
        
        # Cho phép sửa trực tiếp
        edited_nv = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách nhân viên"):
            conn.update(worksheet="NhanVien", data=edited_nv)
            st.success("✅ Đã cập nhật danh sách nhân viên thành công!")
            st.rerun() 
    except Exception as e:
        st.error("Chưa tìm thấy tab 'NhanVien'. Vui lòng tạo Sheet 'NhanVien' trên Google Sheets với các cột: Bán hàng, Dịch vụ, Phụ tùng, Hành chính.")

with tab1:
    # Đọc dữ liệu báo cáo từ Sheet1
    try:
        existing_data = conn.read(worksheet="Sheet1")
        existing_data = existing_data.dropna(how="all")
    except:
        existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form"):
        # Ép hiển thị format ngày dd/mm/yyyy
        today = datetime.now()
        date_input = st.date_input("Ngày báo cáo", today, format="DD/MM/YYYY")
        date_str = date_input.strftime("%d/%m/%Y")
        
        # Sắp xếp thứ tự bộ phận ưu tiên
        uu_tien_bophan = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        
        try:
            df_nv_current = conn.read(worksheet="NhanVien")
            # Lọc lấy các bộ phận có trong sheet nhưng ưu tiên theo danh sách của sếp
            all_bophan = list(df_nv_current.columns)
            list_bophan = [bp for bp in uu_tien_bophan if bp in all_bophan] + [bp for bp in all_bophan if bp not in uu_tien_bophan]
            
            dept = st.selectbox("Chọn bộ phận báo cáo", list_bophan)
            
            # Lọc danh sách NV theo bộ phận đã chọn
            ds_nhan_vien = [str(x) for x in df_nv_current[dept].tolist() if str(x) != 'nan' and str(x).strip() != '']
        except:
            st.warning("Vui lòng thiết lập danh sách nhân viên ở tab bên cạnh.")
            ds_nhan_vien = []
            dept = "Chưa xác định"

        st.markdown(f"**Danh sách nhân viên {dept}:**")
        
        # Nhập liệu theo thứ tự yêu cầu
        truc_trua = st.multiselect("Trực Trưa", ds_nhan_vien)
        truc_dem = st.multiselect("Trực Đêm", ds_nhan_vien)
        di_tre = st.multiselect("Đi Trễ", ds_nhan_vien)
        ve_som = st.multiselect("Về Sớm", ds_nhan_vien)
        off = st.multiselect("Nghỉ Chế Độ (Off)", ds_nhan_vien)
            
        submit_button = st.form_submit_button("Gửi báo cáo lên hệ thống")

        if submit_button:
            new_row = pd.DataFrame([{
                "Ngày": date_str,
                "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua),
                "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre),
                "Về Sớm": ", ".join(ve_som),
                "Nghỉ (Off)": ", ".join(off)
            }])
            
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(f"✅ Đã lưu xong báo cáo ngày {date_str}!")
            st.rerun()

# Khu vực tra cứu lịch sử
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
search_query = st.text_input("Gõ tên nhân viên hoặc ngày (dd/mm/yyyy) để tìm nhanh...")

if search_query:
    filtered_df = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
    st.dataframe(filtered_df, use_container_width=True)
else:
    # Hiện 10 dòng mới nhất cho gọn màn hình điện thoại
    st.dataframe(existing_data.tail(10), use_container_width=True)
