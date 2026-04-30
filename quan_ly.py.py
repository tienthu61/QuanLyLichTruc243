import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối với Google Sheets - Thêm TTL để xóa bộ nhớ đệm sau 10 giây
conn = st.connection("gsheets", type=GSheetsConnection)

# --- GIAO DIỆN TAB ---
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    st.subheader("Cài đặt danh sách nhân viên")
    try:
        # Ép buộc đọc dữ liệu mới nhất (không dùng cache cũ)
        df_nv = conn.read(worksheet="NhanVien", ttl=0) 
        st.info("Nhập tên NV vào cột tương ứng. Nhớ nhấn 'Lưu' sau khi nhập.")
        
        # Sắp xếp cột theo ý sếp
        uu_tien_cols = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        actual_cols = [c for c in uu_tien_cols if c in df_nv.columns] + [c for c in df_nv.columns if c not in uu_tien_cols]
        df_nv = df_nv[actual_cols]
        
        edited_nv = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách nhân viên"):
            conn.update(worksheet="NhanVien", data=edited_nv)
            st.success("✅ Đã cập nhật! Vui lòng chờ 2 giây để hệ thống đồng bộ...")
            st.cache_data.clear() # Xóa sạch bộ nhớ tạm
            st.rerun() 
    except Exception as e:
        st.error("Hệ thống chưa tìm thấy tab 'NhanVien'.")
        st.write("Mẹo: Bạn hãy kiểm tra xem file Google Sheets đã được chia sẻ ở chế độ ' Anyone with the link can EDIT' chưa nhé.")

with tab1:
    try:
        # Đọc dữ liệu báo cáo (Sheet1)
        existing_data = conn.read(worksheet="Sheet1", ttl=0)
        existing_data = existing_data.dropna(how="all")
    except:
        existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])

    with st.form("entry_form"):
        # Ngày dd/mm/yyyy
        today = datetime.now()
        date_input = st.date_input("Ngày báo cáo", today, format="DD/MM/YYYY")
        date_str = date_input.strftime("%d/%m/%Y")
        
        uu_tien_bp = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        
        try:
            df_nv_now = conn.read(worksheet="NhanVien", ttl=0)
            list_bp = [bp for bp in uu_tien_bp if bp in df_nv_now.columns]
            
            dept = st.selectbox("Chọn bộ phận báo cáo", list_bp)
            # Lọc NV và xóa các ô trống
            ds_nv = [str(x) for x in df_nv_now[dept].tolist() if str(x) != 'nan' and str(x).strip() != '']
        except:
            st.warning("Đang tải danh sách nhân viên hoặc tab 'NhanVien' bị trống...")
            ds_nv = []
            dept = "Đang tải..."

        st.markdown(f"**Chọn nhân viên bộ phận: {dept}**")
        
        truc_trua = st.multiselect("Trực Trưa", ds_nv)
        truc_dem = st.multiselect("Trực Đêm", ds_nv)
        di_tre = st.multiselect("Đi Trễ", ds_nv)
        ve_som = st.multiselect("Về Sớm", ds_nv)
        off = st.multiselect("Nghỉ Chế Độ (Off)", ds_nv)
            
        submit = st.form_submit_button("Gửi báo cáo")

        if submit:
            new_entry = pd.DataFrame([{
                "Ngày": date_str, "Bộ Phận": dept,
                "Trực Trưa": ", ".join(truc_trua), "Trực Đêm": ", ".join(truc_dem),
                "Đi Trễ": ", ".join(di_tre), "Về Sớm": ", ".join(ve_som), "Nghỉ (Off)": ", ".join(off)
            }])
            updated = pd.concat([existing_data, new_entry], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated)
            st.success(f"✅ Đã lưu báo cáo ngày {date_str}")
            st.cache_data.clear()
            st.rerun()

# Tra cứu
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
query = st.text_input("Tìm nhanh (Tên hoặc Ngày)...")

if query:
    result = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)]
    st.dataframe(result, use_container_width=True)
else:
    st.dataframe(existing_data.tail(10), use_container_width=True)
