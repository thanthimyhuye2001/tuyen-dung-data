# =============================================================================
# web.py
# Xây dựng trang web hiển thị dữ liệu việc làm bằng Streamlit
# =============================================================================

'''
── KHUNG CHÍNH (CẤU TRÚC FILE WEB.PY) ─────────────────────────────────────────

1. IMPORT                           Khai báo các thư viện/module (streamlit, pandas, logging)
2. LOGGING                          Thiết lập cấu hình ghi nhận nhật ký và lỗi hệ thống
3. CÁC HÀM CORE & XỬ LÝ DỮ LIỆU     Cấu hình trang, tải dữ liệu từ CSV, lọc dữ liệu (Filter)
4. CÁC HÀM RENDER GIAO DIỆN (UI)    Nhúng CSS, hiển thị Header, thanh lọc, và các thẻ Job Card
5. HÀM MAIN() (LUỒNG CHÍNH)         Điều phối toàn bộ logic: Load Data -> Lọc Data -> Render Web
6. ENTRY POINT                      Khối lệnh kích hoạt hàm main() -> chạy ứng dụng Streamlit
───────────────────────────────────────────────────────────────────────────────
'''

# ── 1. IMPORT ────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import logging
from datetime import datetime


# ── 2. LOGGING ───────────────────────────────────────────────────────────────────

# Thiết lập logging cơ bản để ghi nhận lỗi hệ thống
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ── 3. CÁC HÀM CORE & XỬ LÝ DỮ LIỆU ──────────────────────────────────────────────

def configure_page():
    """Cấu hình các thông số cơ bản cho trang web Streamlit."""
    st.set_page_config(page_title="Job Data", page_icon="💼", layout="wide")

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Đọc dữ liệu từ file CSV và xử lý các giá trị NaN.
    Sử dụng cache để tối ưu hóa tốc độ tải trang.
    """
    try:
        df = pd.read_csv(file_path)
        
        # Chỉ giữ lại các công việc liên quan đến Data (related_data == True)
        if 'related_data' in df.columns:
            df = df[df['related_data'] == True]
            
        df = df.fillna("Chưa cập nhật")
        return df
    except Exception as e:
        logging.error(f"Lỗi khi đọc file dữ liệu {file_path}: {e}")
        st.error("Không thể tải dữ liệu. Vui lòng kiểm tra lại đường dẫn file CSV.")
        return pd.DataFrame()

def get_unique_values(df: pd.DataFrame, column_name: str) -> list:
    """Lấy danh sách các giá trị duy nhất trong một cột để làm menu thả xuống."""
    if column_name in df.columns:
        return ["Tất cả"] + sorted([str(x) for x in df[column_name].unique() if str(x) != "Chưa cập nhật"])
    return ["Tất cả"]

def filter_dataframe(df: pd.DataFrame, search_query: str, selected_location: str, selected_pos: str, selected_type: str, selected_exp: str, selected_salary: str, selected_industry: str) -> pd.DataFrame:
    """Lọc dữ liệu Dataframe dựa trên các tham số đầu vào."""
    if df.empty:
        return df
        
    df_filtered = df.copy()
    
    if search_query and 'job_title' in df_filtered.columns:
        # Băm từ khóa thành các từ đơn và áp dụng logic tìm kiếm "chứa tất cả các từ" (AND logic)
        keywords = search_query.lower().split()
        job_titles_lower = df_filtered['job_title'].astype(str).str.lower()
        
        mask = pd.Series(True, index=df_filtered.index)
        for kw in keywords:
            mask = mask & job_titles_lower.str.contains(kw, na=False, regex=False)
            
        df_filtered = df_filtered[mask]
        
    if selected_location and selected_location != "Tất cả":
        if 'province' in df.columns:
            df_filtered = df_filtered[df_filtered['province'].astype(str) == selected_location]
        elif 'location' in df.columns:
            df_filtered = df_filtered[df_filtered['location'].astype(str) == selected_location]
    if selected_pos != "Tất cả" and 'job_position' in df.columns:
        df_filtered = df_filtered[df_filtered['job_position'].astype(str) == selected_pos]
    if selected_type != "Tất cả":
        if 'work_type' in df.columns:
            df_filtered = df_filtered[df_filtered['work_type'].astype(str) == selected_type]
        elif 'job_type' in df.columns:
            df_filtered = df_filtered[df_filtered['job_type'].astype(str) == selected_type]
    if selected_exp != "Tất cả" and 'min_experience' in df.columns:
        df_filtered = df_filtered[df_filtered['min_experience'].astype(str) == selected_exp]
    if selected_salary != "Tất cả" and 'salary_group' in df.columns:
        df_filtered = df_filtered[df_filtered['salary_group'].astype(str) == selected_salary]
    if selected_industry != "Tất cả" and 'job_industry' in df.columns:
        df_filtered = df_filtered[df_filtered['job_industry'].astype(str) == selected_industry]
        
    return df_filtered



# ── 4. CÁC HÀM RENDER GIAO DIỆN (UI) ─────────────────────────────────────────────

def apply_custom_css():
    """Nhúng mã CSS tùy chỉnh để định dạng giao diện trang web giống Xóm Jobs."""
    css_code = """
    <style>
        .stApp { background-color: #fafafa; }
        /* Giới hạn chiều rộng và căn giữa để tạo khoảng trắng 2 bên giống Xóm Jobs */
        .block-container { max-width: 1400px !important; padding-top: 2rem !important; }
        


        .job-card {
            border: 1px solid #e5e7eb; border-radius: 12px;
            padding: 16px; margin-bottom: 16px;
            background-color: white; transition: all 0.2s ease-in-out;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); cursor: pointer;
            height: calc(100% - 16px); display: flex; flex-direction: column;
        }
        .job-card:hover {
            border-color: #14489c; transform: translateY(-2px);
            box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.1); background-color: #fbfdff;
        }
        .title-company-group { min-height: 86px; max-height: 86px; margin-top: 12px; margin-bottom: 0px; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
        .job-title { font-size: 16px; font-weight: 600; color: #111827; line-height: 1.4; transition: color 0.2s; display: block; margin-bottom: 2px; }
        .job-card:hover .job-title { color: #1d4ed8; }
        .company-name { font-size: 13px; color: #6b7280; line-height: 1.4; display: block; }
        .salary { font-weight: 600; color: #374151; font-size: 14px; }
        .tag { border: 1px solid #e5e7eb; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 500; color: #6b7280; background-color: #f9fafb; display: inline-block; }
        .new-badge { background-color: #eff6ff; color: #1d4ed8; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: 600; }
        /* Giảm padding của cột */
        [data-testid="column"] { padding: 0 0.4rem; }
        
        /* Ghi đè CSS toàn bộ Nút bấm (Phân trang) để thành bo góc, nền trắng chữ đen */
        .stButton > button {
            height: 42px !important; 
            min-width: 42px !important;
            padding: 0 !important; /* Xóa padding mặc định để chữ không bị ép mất */
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 8px !important; 
            border: 1px solid #e5e7eb !important; 
            background-color: white !important; 
            font-weight: 500 !important;
        }
        /* CSS biến Checkbox thành Pill Tags cho Tag Liên Quan */
        div[data-testid="stCheckbox"] {
            background-color: #f3f4f6;
            border-radius: 20px;
            padding: 6px 16px;
            display: inline-flex;
            cursor: pointer;
            border: 1px solid transparent;
        }
        div[data-testid="stCheckbox"] > div:first-child {
            display: none !important; /* Ẩn ô vuông mặc định */
        }
        div[data-testid="stCheckbox"] label {
            padding: 0 !important; margin: 0 !important;
            cursor: pointer !important;
        }
        div[data-testid="stCheckbox"] p {
            color: #4b5563 !important;
            font-weight: 600 !important;
            margin: 0 !important;
            font-size: 14px !important;
        }
        /* Style khi checkbox được click (True) */
        div[data-testid="stCheckbox"][aria-checked="true"],
        div[data-testid="stCheckbox"]:has(input:checked) {
            background-color: #eff6ff !important;
            border: 1px solid #14489c !important;
        }
        div[data-testid="stCheckbox"][aria-checked="true"] p,
        div[data-testid="stCheckbox"]:has(input:checked) p {
            color: #1d4ed8 !important;
        }
        
        /* CSS cho phần đếm số lượng (thẻ em) */
        div[data-testid="stCheckbox"] p em {
            color: #9ca3af !important;
            font-weight: 400 !important;
            font-style: normal !important;
            font-size: 13px !important;
            margin-left: 2px;
        }
        div[data-testid="stCheckbox"][aria-checked="true"] p em,
        div[data-testid="stCheckbox"]:has(input:checked) p em {
            color: #60a5fa !important;
        }
        
        /* Ép màu chữ cho mọi thẻ bên trong nút để tránh sai lệch phiên bản Streamlit */
        .stButton > button * { color: #4b5563 !important; }
        
        .stButton > button:hover {
            border-color: #d1d5db !important;
            background-color: #f3f4f6 !important;
        }
        .stButton > button:hover * { color: #111827 !important; }
        
        /* Nút Active đang chọn (Màu xanh Blue nổi bật) */
        .stButton > button[kind="primary"] {
            background-color: #14489c !important; 
            border-color: #14489c !important;
        }
        .stButton > button[kind="primary"] * { color: white !important; }
        
        .stButton > button[kind="primary"]:hover {
            background-color: #2563eb !important;
            border-color: #2563eb !important;
        }
        .stButton > button[kind="primary"]:hover * { color: white !important; }
        
        /* Làm rõ và phóng to chữ/icon ở thanh Search và Location */
        [data-testid="stTextInput"] input::placeholder {
            opacity: 1 !important;
            color: #4b5563 !important;
            font-size: 18px !important;
        }
        [data-testid="stTextInput"] input {
            font-size: 18px !important;
        }
        
        /* Viền xanh blue đậm cho ô vị trí tuyển dụng (Quét mọi lớp) */
        [data-testid="stTextInput"] div[data-baseweb="base-input"],
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stTextInput"] > div > div {
            border: 3px solid #14489c !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 3px 0 rgba(59, 130, 246, 0.3) !important;
        }
        [data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within,
        [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
        [data-testid="stTextInput"] > div > div:focus-within {
            border-color: #1d4ed8 !important;
        }
        [data-testid="stSelectbox"] div[data-baseweb="select"] span {
            font-size: 18px !important;
            opacity: 1 !important;
            color: #4b5563 !important;
        }
        
        /* Chữ của nút bấm to hơn (cho nút TÌM KIẾM) */
        .stButton > button * { 
            font-size: 16px !important; 
        }
        
        #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)

def render_header():
    """Hiển thị phần tiêu đề và mô tả của trang web."""
    st.markdown('<h1 style="font-size: 44px; font-weight: 800; color: #111827; text-align: center;">Việc làm <span style="color: #14489c;">Data</span> tại Việt Nam</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #6b7280; font-size: 18px; margin-bottom: 32px; text-align: center;">Cơ hội Data Analyst, Data Engineer, Data Scientist và AI/ML tại Việt Nam</p>', unsafe_allow_html=True)

def render_filters(df: pd.DataFrame) -> tuple:
    """Hiển thị bộ lọc và trả về các giá trị bộ lọc do người dùng chọn."""
    
    if 'show_filters' not in st.session_state:
        st.session_state.show_filters = False
        
    def toggle_filters():
        st.session_state.show_filters = not st.session_state.show_filters

    # Hàng 1: Nút Tìm Kiếm, Thanh Search, Nút Bộ Lọc
    col_btn, col1, col_filter = st.columns([1.2, 4.2, 1.2])
    
    with col_btn:
        # Thêm khoảng trống để nút cân bằng với các input bị ẩn label
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        st.button("TÌM KIẾM", type="primary", use_container_width=True)
        
    with col1:
        search_query = st.text_input("Tìm kiếm", placeholder="🔍 Vị trí tuyển dụng trong lĩnh vực data. Ví dụ: Data Analyst ...", label_visibility="hidden")
        
    with col_filter:
        st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
        st.button("🔽 Bộ lọc nâng cao" if not st.session_state.show_filters else "✖ Đóng lọc", on_click=toggle_filters, use_container_width=True)

    # Khởi tạo giá trị mặc định khi bộ lọc bị ẩn
    selected_location = "Tất cả"
    selected_pos = "Tất cả"
    selected_type = "Tất cả"
    selected_exp = "Tất cả"
    selected_salary = "Tất cả"
    selected_industry = "Tất cả"
    
    # Hàng 2: Địa điểm, Cấp bậc, Hình thức, Kinh nghiệm, Lương, Lĩnh vực
    if st.session_state.show_filters:
        with st.container():
            st.markdown('<div style="margin-top: -8px;"></div>', unsafe_allow_html=True)
            # Tỉ lệ cột: Giảm Địa điểm (0.75), Tăng Lĩnh vực (1.25), Các cột còn lại giữ nguyên (1)
            col2, col3, col4, col5, col6, col7 = st.columns([0.75, 1, 1, 1, 1, 1.25])
            
            with col2:
                loc_col = 'province' if 'province' in df.columns else 'location'
                selected_location = st.selectbox("📍 Địa điểm", get_unique_values(df, loc_col))
            with col3:
                selected_pos = st.selectbox("🎓 Cấp bậc nhân viên", get_unique_values(df, 'job_position'))
            with col4:
                wt_col = 'work_type' if 'work_type' in df.columns else 'job_type'
                selected_type = st.selectbox("💼 Hình thức", get_unique_values(df, wt_col))
            with col5:
                exp_options = ["Tất cả"]
                exp_mapping = {"Tất cả": "Tất cả"}
                if 'min_experience' in df.columns:
                    raw_exps = sorted([x for x in df['min_experience'].unique() if str(x) != "Chưa cập nhật" and pd.notna(x)])
                    for x in raw_exps:
                        clean_x = str(int(x)) if isinstance(x, (int, float)) and x == int(x) else str(x)
                        if clean_x.endswith('.0'): clean_x = clean_x[:-2]
                        display_str = f"{clean_x} năm"
                        if display_str not in exp_options:
                            exp_options.append(display_str)
                            exp_mapping[display_str] = str(x)
                selected_exp_display = st.selectbox("⭐ Năm kinh nghiệm", exp_options)
                selected_exp = exp_mapping[selected_exp_display]
            with col6:
                selected_salary = st.selectbox("\U0001F4B0 Mức lương", get_unique_values(df, 'salary_group'))
            with col7:
                selected_industry = st.selectbox("🏢 Lĩnh vực", get_unique_values(df, 'job_industry'))
        
    return search_query, selected_location, selected_pos, selected_type, selected_exp, selected_salary, selected_industry

def render_job_card(row: pd.Series):
    """Tạo mã HTML cho một thẻ công việc đơn lẻ và hiển thị nó dưới dạng ô vuông (Grid)."""
    title = str(row.get('job_title', 'Không có tiêu đề'))
    company = str(row.get('company', row.get('company_name', 'Công ty bảo mật danh tính')))
    salary = str(row.get('salary', 'Thỏa thuận'))
    location = str(row.get('location', row.get('province', 'Việt Nam')))
    level = str(row.get('job_position', ''))
    
    w_type = str(row.get('work_type', row.get('job_type', '')))
    if w_type == "nan" or w_type == "Chưa cập nhật": w_type = ""
    w_type_html = f'💼 {w_type}' if w_type else ''
    
    # Xử lý date_deadline
    deadline = row.get('date_deadline')
    if pd.isna(deadline) or str(deadline).strip() == "":
        deadline_str = ""
    else:
        try:
            deadline_str = pd.to_datetime(deadline).strftime("%d/%m/%Y")
        except:
            deadline_str = str(deadline)
    
    # Tính toán khoảng thời gian từ date_posted tới hôm nay
    time_str = "Vừa xong"
    date_posted = row.get('date_posted')
    if pd.notna(date_posted) and str(date_posted).strip() != "":
        try:
            posted_date = pd.to_datetime(date_posted).date()
            today = datetime.now().date()
            days_diff = (today - posted_date).days
            
            if days_diff <= 0:
                time_str = "Hôm nay"
            elif days_diff < 7:
                time_str = f"{days_diff} ngày trước"
            elif days_diff < 30:
                weeks = days_diff // 7
                time_str = f"{weeks} tuần trước"
            else:
                months = days_diff // 30
                time_str = f"{months} tháng trước"
        except Exception:
            pass
            
    exp_val = row.get('min_experience')
    if pd.isna(exp_val) or str(exp_val).strip() == "" or str(exp_val) == "Chưa cập nhật":
        exp_html = ""
    else:
        clean_exp = str(int(exp_val)) if isinstance(exp_val, (int, float)) and exp_val == int(exp_val) else str(exp_val)
        if clean_exp.endswith('.0'): clean_exp = clean_exp[:-2]
        exp_html = f'<div style="color: #4b5563; font-size: 13px; font-weight: 500;">⭐ {clean_exp} năm</div>'
            
    def is_true(val):
        return str(val).strip().lower() == 'true'
        
    related_tags = []
    if is_true(row.get('related_data_analyst_bi')):
        related_tags.append('Data Analytics / BI')
    if is_true(row.get('related_data_engineer')):
        related_tags.append('Data Engineer')
    if is_true(row.get('related_data_science')):
        related_tags.append('Data Science')
    if is_true(row.get('related_ai_ml')):
        related_tags.append('AI / Machine Learning')
        
    level_tag_html = f'<span style="background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 500; display: inline-block;">{level}</span>' if level and level != "Chưa cập nhật" else ''
    related_tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in related_tags])
    
    if level_tag_html or related_tags_html:
        tag_html = f'<div style="margin-top: 10px; display: flex; align-items: center; flex-wrap: wrap; gap: 6px;">{level_tag_html}{related_tags_html}</div>'
    else:
        tag_html = '<div style="margin-top: 10px; height: 22px;"></div>'
    
    # Đổi h3 và p thành div để tránh bị CSS mặc định của Streamlit Markdown (font to, màu xanh) ghi đè
    card_html = f'<a href="?job_index={row.name}" target="_self" style="text-decoration: none; color: inherit; display: block; height: 100%;"><div class="job-card"><div style="display: flex; justify-content: space-between; align-items: flex-start;"><div style="width: 40px; height: 40px; border-radius: 8px; background-color: #f3f4f6; display: flex; align-items: center; justify-content: center; border: 1px solid #e5e7eb;"><span style="font-size: 20px;">🏢</span></div><span class="new-badge">{time_str}</span></div><div class="title-company-group"><div class="job-title" title="{title}">{title}</div><div class="company-name" title="{company}">{company}</div></div><div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;"><div style="display: flex; align-items: center; gap: 6px; color: #4b5563; font-size: 13px;">💰 <span class="salary">{salary}</span></div>{exp_html}<div style="font-size: 12px; color: #6b7280; font-weight: 500;">{w_type_html}</div></div>{tag_html}<div style="margin-top: auto; padding-top: 16px; padding-bottom: 0.3cm; position: relative; height: 16px; font-size: 11px; color: #9ca3af;"><span style="position: absolute; left: 0; display: flex; align-items: center; gap: 4px;">🕒 Hạn nộp: {deadline_str}</span><span style="position: absolute; right: 0; display: flex; align-items: center; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100px;" title="{location}">📍 {location}</span></div></div></a>'
    st.markdown(card_html, unsafe_allow_html=True)

def render_job_list(df_filtered: pd.DataFrame):
    """Hiển thị toàn bộ danh sách công việc phù hợp (dạng Grid 4 cột)."""
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
        
    jobs_per_page = 20
    total_jobs = len(df_filtered)
    total_pages = max(1, (total_jobs - 1) // jobs_per_page + 1)
    
    # Đảm bảo trang hiện tại không vượt quá tổng số trang
    if st.session_state.current_page > total_pages:
        st.session_state.current_page = 1
        
    st.markdown('<hr style="border: none; border-top: 1px solid #e5e7eb; margin-top: 16px; margin-bottom: 24px;">', unsafe_allow_html=True)
    
    col_count, col_icon, col_sort = st.columns([7.5, 0.5, 2])
    with col_count:
        st.markdown(f'<div style="font-size: 14px; color: #4b5563; font-weight: 600; padding-top: 8px; margin-bottom: 16px;"><span style="color: #000000; font-weight: 900;">{total_jobs}</span> việc làm</div>', unsafe_allow_html=True)
    with col_icon:
        st.markdown('<div style="text-align: right; padding-top: 6px; font-size: 20px; color: #4b5563; font-weight: bold;">\u21C5</div>', unsafe_allow_html=True)
    with col_sort:
        sort_option = st.selectbox("Sắp xếp", ["Mới nhất", "Cũ nhất"], label_visibility="collapsed")
        
    # Thực hiện sắp xếp dữ liệu
    if 'date_posted' in df_filtered.columns:
        df_filtered = df_filtered.copy()
        # Tạo cột tạm để sắp xếp chính xác theo ngày
        df_filtered['temp_date'] = pd.to_datetime(df_filtered['date_posted'], errors='coerce')
        ascending = True if sort_option == "Cũ nhất" else False
        df_filtered = df_filtered.sort_values(by='temp_date', ascending=ascending, na_position='last')
    
    if df_filtered.empty:
        st.info("Không tìm thấy công việc nào phù hợp với bộ lọc của bạn.")
        return
        
    # Cắt dữ liệu cho trang hiện tại (Mỗi trang 20 job -> 4 cột x 5 hàng)
    start_idx = (st.session_state.current_page - 1) * jobs_per_page
    end_idx = start_idx + jobs_per_page
    df_page = df_filtered.iloc[start_idx:end_idx]
        
    # Tạo Grid 4 cột (dàn đều theo từng hàng để các thẻ cao không làm lệch hàng dưới)
    num_cols = 4
    
    # Lặp qua từng nhóm 4 công việc để tạo các hàng ngang riêng biệt
    for i in range(0, len(df_page), num_cols):
        cols = st.columns(num_cols)
        for j, (_, row) in enumerate(df_page.iloc[i:i+num_cols].iterrows()):
            with cols[j]:
                render_job_card(row)
            
    # Khối Phân trang (Pagination UI)
    if total_pages > 1:
        st.markdown('<div style="margin-top: 32px;"></div>', unsafe_allow_html=True)
        
        # Xác định các số trang cần hiển thị (Hiển thị tối đa 5 số gần nhất)
        start_p = max(1, st.session_state.current_page - 2)
        end_p = min(total_pages, start_p + 4)
        if end_p - start_p < 4:
            start_p = max(1, end_p - 4)
            
        pages = list(range(start_p, end_p + 1))
        num_buttons = len(pages) + 2
        
        # Tạo tỉ lệ ép các cột nút lại gần nhau (Padding 2 bên lớn, mỗi nút chiếm 1 phần)
        # Giúp các nút bấm trở nên nhỏ gọn và sát nhau giống hệt bản gốc
        spacer = 8 # Giảm hệ số spacer để nút có đủ không gian hiển thị chữ
        btn_cols = st.columns([spacer] + [1] * num_buttons + [spacer], gap="small")
        
        with btn_cols[1]:
            if st.button("<", disabled=(st.session_state.current_page == 1), key="prev", use_container_width=True):
                st.session_state.current_page -= 1
                st.rerun()
                
        for i, p in enumerate(pages):
            with btn_cols[i + 2]:
                # Nếu là trang hiện tại thì nút sẽ có màu xanh (primary)
                if st.button(str(p), type="primary" if p == st.session_state.current_page else "secondary", key=f"page_{p}", use_container_width=True):
                    st.session_state.current_page = p
                    st.rerun()
                    
        with btn_cols[-2]:
            if st.button(">", disabled=(st.session_state.current_page == total_pages), key="next", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()




def render_job_detail(df: pd.DataFrame, job_idx: int):
    """Hiển thị trang chi tiết công việc."""
    if job_idx not in df.index:
        st.error("Không tìm thấy thông tin công việc!")
        return
        
    job = df.loc[job_idx]
    
    # Khối Nút Quay lại
    st.markdown("""
    <style>
    .back-btn { text-decoration: none; color: #6b7280; font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px; margin-bottom: 24px; transition: color 0.2s; }
    .back-btn:hover { color: #1d4ed8; }
    </style>
    <a href="?" target="_self" class="back-btn">⬅ Danh sách việc làm</a>
    """, unsafe_allow_html=True)
    
    # Trích xuất dữ liệu
    title = job.get('job_title', 'Không có tiêu đề')
    company = job.get('company_name', 'Không có thông tin công ty')
    salary = job.get('salary', 'Thỏa thuận')
    location = job.get('location', 'Không rõ địa điểm')
    level = job.get('job_position', '')
    url = job.get('job_url', '#')
    
    # Format Level tag if valid
    level_html = f'<span style="background-color: #eff6ff; color: #1d4ed8; padding: 4px 12px; border-radius: 12px;">{level}</span>' if str(level).strip() and str(level) != 'Chưa cập nhật' else ''
    
    # Trích xuất dữ liệu mới
    w_type = job.get('work_type', job.get('job_type', ''))
    if pd.isna(w_type) or str(w_type).strip() == "" or str(w_type) == "nan": w_type = ""
    w_type_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px;">💼 {w_type}</span>' if w_type and str(w_type) != 'Chưa cập nhật' else ''
    
    source = job.get('source', '')
    source_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px; color: #0284c7;">🌐 {source}</span>' if pd.notna(source) and str(source).strip() and str(source) != 'Chưa cập nhật' else ''
    
    # Xử lý date_deadline
    deadline = job.get('date_deadline')
    deadline_html = ""
    if pd.notna(deadline) and str(deadline).strip() != "" and str(deadline) != "Chưa cập nhật":
        try:
            deadline_str = pd.to_datetime(deadline).strftime("%d/%m/%Y")
            deadline_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px; color: #ef4444;">⏳ Hạn nộp: {deadline_str}</span>'
        except:
            deadline_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px; color: #ef4444;">⏳ Hạn nộp: {deadline}</span>'
            
    # Tính thời gian đăng job
    time_html = ""
    date_posted = job.get('date_posted')
    if pd.notna(date_posted) and str(date_posted).strip() != "" and str(date_posted) != "Chưa cập nhật":
        try:
            date_str = pd.to_datetime(date_posted).strftime("%d/%m/%Y")
            time_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px;">🕒 {date_str}</span>'
        except:
            time_html = f'<span style="color: #d1d5db;">|</span><span style="display: flex; align-items: center; gap: 4px;">🕒 {date_posted}</span>'

    # Header UI
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
        <div style="width: 80px; height: 80px; background-color: white; border-radius: 12px; border: 1px solid #e5e7eb; display: flex; justify-content: center; align-items: center; font-size: 40px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">🏢</div>
        <div>
            <h1 style="margin: 0; font-size: 26px; font-weight: 800; color: #111827;">{title}</h1>
            <div style="color: #6b7280; font-size: 15px; margin-top: 6px;">{company}</div>
        </div>
    </div>
    
    <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; font-size: 14px; font-weight: 600; color: #4b5563;">
        <span style="color: #1d4ed8; display: flex; align-items: center; gap: 4px; font-size: 15px;">💵 {salary}</span>
        <span style="color: #d1d5db;">|</span>
        <span style="display: flex; align-items: center; gap: 4px;">📍 {location}</span>
        {f'<span style="color: #d1d5db;">|</span>{level_html}' if level_html else ''}
        {w_type_html}
        {time_html}
        {deadline_html}
        {source_html}
    </div>
    
    <div style="display: flex; gap: 12px; margin-bottom: 32px;">
        <a href="{url}" target="_blank" style="background-color: #3b82f6; color: white; text-decoration: none; padding: 10px 24px; border-radius: 8px; font-weight: 600; font-size: 15px; transition: background-color 0.2s;">Ứng tuyển ngay tại {source} ↗</a>
    </div>
    
    <hr style="border: none; border-top: 1px solid #e5e7eb; margin-bottom: 32px;">
    """, unsafe_allow_html=True)
    
    # Hàm in từng khối nội dung
    def render_section(title, text):
        if pd.notna(text) and str(text).strip() != "" and str(text) != "Chưa cập nhật":
            text_html = str(text).replace('\n', '<br>')
            st.markdown(f"""
            <h3 style="font-size: 18px; font-weight: 700; color: #111827; margin-top: 24px; margin-bottom: 16px;">{title}</h3>
            <div style="color: #374151; font-size: 15px; line-height: 1.7; text-align: justify;">{text_html}</div>
            """, unsafe_allow_html=True)
            
    render_section("Mô tả công việc", job.get('description'))
    render_section("Yêu cầu công việc", job.get('requirements'))
    render_section("Phúc lợi", job.get('benefits'))


# ── 5. HÀM MAIN() (LUỒNG CHÍNH) ──────────────────────────────────────────────────

def main():
    """Hàm chính (entrypoint) điều khiển toàn bộ luồng chạy của ứng dụng."""
    
    # Cấu hình giao diện (UI/UX)
    configure_page()
    apply_custom_css()
    
    # Đọc tham số URL
    query_params = st.query_params
    
    # Tải Dữ liệu (Data Loading)
    DATA_PATH = r"Project_full\ETL\GHÉP_FILE\data_merged_1.csv"
    df = load_data(DATA_PATH)
    
    if df.empty:
        return # Dừng chương trình nếu lỗi file
        
    # ROUTING (Điều hướng trang)
    if "job_index" in query_params:
        try:
            job_idx = int(query_params["job_index"])
            render_job_detail(df, job_idx)
        except ValueError:
            st.error("URL không hợp lệ!")
    else:
        # Hiển thị Header
        render_header()
        
        # Hiển thị Bộ lọc (Filters)
        search_query, selected_location, selected_pos, selected_type, selected_exp, selected_salary, selected_industry = render_filters(df)
        
        # Theo dõi thay đổi của bộ lọc để reset về trang 1
        current_filters = f"{search_query}_{selected_location}_{selected_pos}_{selected_type}_{selected_exp}_{selected_salary}_{selected_industry}"
        if 'last_filters' not in st.session_state:
            st.session_state.last_filters = current_filters
        elif st.session_state.last_filters != current_filters:
            st.session_state.current_page = 1
            st.session_state.last_filters = current_filters
        
        # Xử lý Lọc Dữ liệu Cơ bản (Data Processing)
        df_filtered = filter_dataframe(df, search_query, selected_location, selected_pos, selected_type, selected_exp, selected_salary, selected_industry)
        
        # ── HIỂN THỊ TAGS VÀ LỌC THEO TAG ──
        st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)
        
        def count_true(col_name):
            if col_name in df_filtered.columns:
                return (df_filtered[col_name].astype(str).str.strip().str.lower() == 'true').sum()
            return 0
            
        c_da = count_true('related_data_analyst_bi')
        c_de = count_true('related_data_engineer')
        c_ds = count_true('related_data_science')
        c_ai = count_true('related_ai_ml')

        tag_cols = st.columns([1.5, 2.2, 1.8, 1.8, 2.5, 1])
        with tag_cols[0]:
            st.markdown('<div style="padding-top: 8px; font-weight: 700; color: #4b5563; font-size: 15px;">🔖 Tag liên quan</div>', unsafe_allow_html=True)
            
        selected_tags = []
        with tag_cols[1]:
            if st.checkbox(f"Data Analytics / BI *{c_da}*"): selected_tags.append("Data Analytics / BI")
        with tag_cols[2]:
            if st.checkbox(f"Data Engineer *{c_de}*"): selected_tags.append("Data Engineer")
        with tag_cols[3]:
            if st.checkbox(f"Data Science *{c_ds}*"): selected_tags.append("Data Science")
        with tag_cols[4]:
            if st.checkbox(f"AI / Machine Learning *{c_ai}*"): selected_tags.append("AI / Machine Learning")

        # Nếu người dùng chọn bất kỳ tag nào, áp dụng bộ lọc OR cho các tag đó
        if selected_tags:
            tag_mask = pd.Series(False, index=df_filtered.index)
            tag_map = {
                "Data Analytics / BI": "related_data_analyst_bi",
                "Data Engineer": "related_data_engineer",
                "Data Science": "related_data_science",
                "AI / Machine Learning": "related_ai_ml"
            }
            for tag in selected_tags:
                col_name = tag_map.get(tag)
                if col_name and col_name in df_filtered.columns:
                    tag_mask = tag_mask | (df_filtered[col_name].astype(str).str.strip().str.lower() == 'true')
            
            df_final = df_filtered[tag_mask]
        else:
            df_final = df_filtered

        # Hiển thị Kết quả (Rendering) dựa trên df_final đã lọc tag
        render_job_list(df_final)




# ── 6. ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
