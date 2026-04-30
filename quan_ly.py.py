import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="Vinken 243", layout="centered")

st.title("📋 Quản Lý Lịch Trực Tiến Thu 243")

# Kết nối với Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HÀM LẤY DỮ LIỆU THÔNG MINH ---
def get_data(sheet_name):
    try:
        # Thử đọc tên chuẩn
        return conn.read(worksheet=sheet_name, ttl=0)
    except:
        try:
            # Thử đọc nếu sếp lỡ tay gõ thừa dấu cách ở tên tab
            return conn.read(worksheet=f"{sheet_name} ", ttl=0)
        except:
            return None

# --- GIAO DIỆN TAB ---
tab1, tab2 = st.tabs(["📝 Nhập Báo Cáo", "👥 Quản Lý Nhân Viên"])

with tab2:
    st.subheader("Cài đặt danh sách nhân viên")
    df_nv = get_data("NhanVien")
    
    if df_nv is not None:
        st.info("Nhập tên NV vào cột tương ứng. Nhớ nhấn 'Lưu' sau khi nhập.")
        
        # Thứ tự bộ phận theo yêu cầu của Vinken
        uu_tien_cols = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        actual_cols = [c for c in uu_tien_cols if c in df_nv.columns] + [c for c in df_nv.columns if c not in uu_tien_cols]
        df_nv = df_nv[actual_cols]
        
        edited_nv = st.data_editor(df_nv, num_rows="dynamic", use_container_width=True)
        
        if st.button("Lưu danh sách nhân viên"):
            # Lưu vào đúng tên tab hiện tại
            worksheet_target = "NhanVien " if "NhanVien " in str(df_nv) else "NhanVien"
            conn.update(worksheet=worksheet_target, data=edited_nv)
            st.success("✅ Đã cập nhật! Đang làm mới dữ liệu...")
            st.cache_data.clear()
            st.rerun() 
    else:
        st.error("Hệ thống chưa tìm thấy tab 'NhanVien'.")
        st.info("Mẹo: Vinken hãy kiểm tra lại tên Tab dưới cùng của Google Sheets, đảm bảo không có dấu cách thừa nhé!")

with tab1:
    # Đọc dữ liệu báo cáo (Sheet1)
    existing_data = get_data("Sheet1")
    if existing_data is None:
        existing_data = pd.DataFrame(columns=['Ngày', 'Bộ Phận', 'Trực Trưa', 'Trực Đêm', 'Đi Trễ', 'Về Sớm', 'Nghỉ (Off)'])
    else:
        existing_data = existing_data.dropna(how="all")

    with st.form("entry_form"):
        today = datetime.now()
        date_input = st.date_input("Ngày báo cáo", today, format="DD/MM/YYYY")
        date_str = date_input.strftime("%d/%m/%Y")
        
        uu_tien_bp = ["Bán hàng", "Dịch vụ", "Phụ tùng", "Hành chính"]
        df_nv_now = get_data("NhanVien")
        
        if df_nv_now is not None:
            list_bp = [bp for bp in uu_tien_bp if bp in df_nv_now.columns]
            dept = st.selectbox("Chọn bộ phận báo cáo", list_bp)
            ds_nv = [str(x) for x in df_nv_now[dept].tolist() if str(x) != 'nan' and str(x).strip() != '']
        else:
            dept = "Chưa có dữ liệu"
            ds_nv = []

        st.markdown(f"**Chọn nhân viên bộ phận: {dept}**")
        
        truc_trua = st.multiselect("Trực Trưa", ds_nv)
        truc_dem = st.multiselect("Trực Đêm", ds_nv)
        di_tre = st.multiselect("Đi Trễ", ds_nv)
        ve_som = st.multiselect("Về Sớm", ds_nv)
        off = st.multiselect("Nghỉ Chế Độ (Off)", ds_nv)
            
        if st.form_submit_button("Gửi báo cáo"):
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

# Tra cứu nhật ký
st.markdown("---")
st.subheader("🔍 Nhật Ký Lịch Trực")
query = st.text_input("Tìm nhanh tên nhân viên hoặc ngày...")
if query:
    result = existing_data[existing_data.astype(str).apply(lambda x: x.str.contains(query, case=False)).any(axis=1)]
    st.dataframe(result, use_container_width=True)
else:
    st.dataframe(existing_data.tail(10), use_container_width=True)
