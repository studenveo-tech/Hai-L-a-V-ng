import os
import sqlite3
import json
import re
import streamlit as st
import pandas as pd
import bcrypt
from google import genai
from google.genai import types

# ----------------- CẤU HÌNH & KHỞI TẠO -----------------
st.set_page_config(page_title="Đào Tạo Livestream - Hai Lúa Vàng", page_icon="🌾", layout="wide")

# Lấy Gemini API Key từ Secrets hoặc biến môi trường
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

def get_db():
    conn = sqlite3.connect("hailuavang.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        # Bảng Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'trainee',
            status TEXT DEFAULT 'Đang đào tạo'
        )""")
        # Bảng Products
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            target_crops TEXT,
            target_issues TEXT,
            active_ingredients TEXT,
            specification TEXT,
            dosage TEXT,
            application_guide TEXT,
            isolation_period TEXT,
            key_selling_points TEXT,
            forbidden_claims TEXT
        )""")
        # Bảng Simulation
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulation_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            total_score REAL,
            hook_score REAL,
            knowledge_score REAL,
            objection_score REAL,
            cta_score REAL,
            feedback_strengths TEXT,
            feedback_weaknesses TEXT,
            feedback_relearning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Tạo sẵn tài khoản mặc định
        pwd_admin = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        pwd_trainee = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (1, 'admin', ?, 'Quản Lý Đào Tạo', 'admin')", (pwd_admin,))
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (2, 'nhanvien1', ?, 'Nguyễn Văn A', 'trainee')", (pwd_trainee,))
        
        # Nạp dữ liệu sản phẩm mẫu
        cursor.execute("""
        INSERT OR IGNORE INTO products (id, name, category, target_crops, target_issues, active_ingredients, specification, dosage, application_guide, isolation_period, key_selling_points, forbidden_claims)
        VALUES (
            1, 'Thuốc trừ sâu Rồng Vàng 500EC', 'Thuốc bảo vệ thực vật', 'Lúa, Cây ăn trái, Rau màu',
            'Sâu cuốn lá, rầy nâu, bọ trĩ kháng thuốc', 'Alpha-Cypermethrin + Phụ gia sinh học', 'Chai 450ml',
            '20-25ml cho bình 25L nước', 'Phun khi sâu non mới xuất hiện vào sáng sớm hoặc chiều mát', '7 ngày',
            'Hiệu lực kéo dài, bám dính cao, hạn chế rửa trôi',
            'Cam kết diệt sạch 100% vĩnh viễn, Tự ý cam kết tăng năng suất gấp đôi'
        )""")
        conn.commit()

init_db()

# ----------------- HÀM GỌI GEMINI AN TOÀN -----------------
def call_gemini(prompt: str, context: str = "", temp: float = 0.3):
    if not GEMINI_KEY:
        return "Lưu ý: Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets."
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        system_instruction = f"""
        Bạn là Chuyên gia Đào tạo Livestream Nông nghiệp Hai Lúa Vàng.
        Quy tắc bắt buộc:
        1. Tuyệt đối không bịa đặt thông số kỹ thuật, giá bán, hay khuyến mãi.
        2. Nếu thông tin không có trong dữ liệu sản phẩm được cấp dưới đây, hãy trả lời: 'Vui lòng chuyển câu hỏi cho bộ phận kỹ thuật.'
        3. Dữ liệu sản phẩm: {context}
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temp
            )
        )
        return response.text
    except Exception as e:
        return f"Lỗi AI: {str(e)}"

# ----------------- ĐĂNG NHẬP & PHÂN QUYỀN -----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<h2 style='text-align: center;'>HỆ THỐNG ĐÀO TẠO LIVESTREAM HAI LÚA VÀNG</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("login"):
            u = st.text_input("Tên đăng nhập (Thử: nhanvien1 hoặc admin)")
            p = st.text_input("Mật khẩu (Thử: user123 hoặc admin123)", type="password")
            if st.form_submit_button("Đăng Nhập"):
                with get_db() as conn:
                    res = conn.execute("SELECT * FROM users WHERE username = ?", (u,)).fetchone()
                    if res and bcrypt.checkpw(p.encode(), res["password_hash"].encode()):
                        st.session_state.user = dict(res)
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu.")
    st.stop()

# ----------------- GIAO DIỆN CHÍNH -----------------
user = st.session_state.user
st.sidebar.markdown(f"**👤 Tài khoản:** {user['full_name']}")
st.sidebar.markdown(f"**🔰 Vai trò:** `{user['role'].upper()}` | **Trạng thái:** `{user['status']}`")

menu = st.sidebar.radio("CHỨC NĂNG", [
    "🏠 Dashboard",
    "📦 Hồ Sơ Sản Phẩm",
    "🎤 Kịch Bản Livestream",
    "🤖 Luyện Tập Với AI",
    "🧠 Sát Hạch Kiến Thức",
    "🚪 Đăng Xuất"
])

if menu == "🚪 Đăng Xuất":
    st.session_state.user = None
    st.rerun()

elif menu == "🏠 Dashboard":
    st.title("🏠 Dashboard Tiến Độ Đào Tạo")
    with get_db() as conn:
        p_cnt = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        sim_cnt = conn.execute("SELECT COUNT(*) as c FROM simulation_sessions WHERE user_id = ?", (user['id'],)).fetchone()["c"]
        avg_s = conn.execute("SELECT AVG(total_score) as a FROM simulation_sessions WHERE user_id = ?", (user['id'],)).fetchone()["a"] or 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Sản Phẩm Trong Kho", f"{p_cnt} SP")
    c2.metric("Số Lần Luyện Tập AI", f"{sim_cnt} Lần")
    c3.metric("Điểm Trung Bình", f"{avg_s:.1f}/100")

    if avg_s >= 80:
        st.success("✅ ĐỦ ĐIỀU KIỆN LIVESTREAM (Điểm >= 80)")
    else:
        st.info("📌 Cần tiếp tục luyện tập để đạt tối thiểu 80/100 điểm.")

elif menu == "📦 Hồ Sơ Sản Phẩm":
    st.title("📦 Danh Mục Sản Phẩm Đã Xác Thực")
    with get_db() as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    for p in products:
        with st.expander(f"🏷️ {p['name']} ({p['category']})"):
            st.write(f"**Cây trồng:** {p['target_crops']}")
            st.write(f"**Vấn đề giải quyết:** {p['target_issues']}")
            st.write(f"**Liều lượng & Cách dùng:** {p['dosage']} - {p['application_guide']}")
            st.write(f"**Thời gian cách ly:** {p['isolation_period']}")
            st.error(f"🚫 CẤM NÓI SAI SỰ THẬT: {p['forbidden_claims']}")

elif menu == "🎤 Kịch Bản Livestream":
    st.title("🎤 Bộ Tạo Kịch Bản Tự Động Theo 7 Nguyên Tắc")
    with get_db() as conn:
        products = [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]
    prod_map = {p['name']: p for p in products}
    sel = st.selectbox("Chọn sản phẩm cần chuẩn bị:", list(prod_map.keys()))
    
    if st.button("🚀 Tạo Kịch Bản Chi Tiết (Hook, Demo, CTA, Q&A)"):
        with st.spinner("AI đang tạo kịch bản..."):
            prompt = f"Tạo kịch bản livestream cho sản phẩm: {prod_map[sel]['name']}. Bao gồm: 3 Hook 5s, Cách xác định vấn đề bà con gặp, Hướng dẫn demo cầm sản phẩm, 5 câu hỏi thường gặp và 3 mẫu CTA dứt khoát."
            res = call_gemini(prompt, str(prod_map[sel]))
            st.markdown(res)

elif menu == "🤖 Luyện Tập Với AI":
    st.title("🤖 Giả Lập Khách Hàng & Chấm Điểm Livestream")
    with get_db() as conn:
        products = [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]
    prod_map = {p['name']: p for p in products}
    sel = st.selectbox("Chọn sản phẩm thực hành:", list(prod_map.keys()))
    cur_p = prod_map[sel]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    user_input = st.chat_input("Nhập lời thoại của bạn...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        prompt = f"Bạn là bà con nông dân đang xem live sản phẩm {cur_p['name']}. Hãy đưa ra 1 bình luận ngắn hỏi về liều lượng, công dụng hoặc chê giá cao để thử thách người live. Lịch sử: {st.session_state.messages}"
        reply = call_gemini(prompt, str(cur_p), temp=0.7)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("📊 Chấm Điểm Phiên Live Này"):
        if len(st.session_state.messages) < 2:
            st.warning("Hãy chat ít nhất 1-2 lượt trước khi chấm điểm.")
        else:
            with st.spinner("AI đang chấm điểm 8 tiêu chí..."):
                eval_p = f"""
                Đánh giá phiên live sau: {json.dumps(st.session_state.messages, ensure_ascii=False)}.
                Trả về DUY NHẤT 1 chuỗi JSON:
                {{"total_score": 85, "hook_score": 80, "knowledge_score": 90, "objection_score": 80, "cta_score": 85, "strengths": "Điểm mạnh", "weaknesses": "Điểm yếu", "relearning": "Kiến thức cần đọc lại"}}
                """
                raw = call_gemini(eval_p, str(cur_p), temp=0.1)
                try:
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    data = json.loads(match.group(0))
                    with get_db() as conn:
                        conn.execute("""
                        INSERT INTO simulation_sessions (user_id, product_id, total_score, hook_score, knowledge_score, objection_score, cta_score, feedback_strengths, feedback_weaknesses, feedback_relearning)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (user['id'], cur_p['id'], data['total_score'], data['hook_score'], data['knowledge_score'], data['objection_score'], data['cta_score'], data['strengths'], data['weaknesses'], data['relearning']))
                        conn.commit()
                    st.success(f"🎉 Điểm Tổng: **{data['total_score']}/100**")
                    st.write(f"- **Điểm mạnh:** {data['strengths']}")
                    st.write(f"- **Cần sửa:** {data['weaknesses']}")
                except Exception:
                    st.write(raw)

elif menu == "🧠 Sát Hạch Kiến Thức":
    st.title("🧠 Kiểm Tra Tiêu Chuẩn Livestream")
    with st.form("quiz"):
        q1 = st.radio("1. Trong 3-5 giây đầu tiên cần làm gì?", ["Chào từng người và đợi đông mắt xem", "Nêu ngay vấn đề sâu bệnh và lợi ích giải pháp", "Bật nhạc lớn"])
        q2 = st.radio("2. Khi khách hỏi bệnh cây ngoài dữ liệu được cấp, bạn xử lý sao?", ["Tự tư vấn theo kinh nghiệm", "Báo thông tin chưa có trong tài liệu chính thức và chuyển kỹ thuật hỗ trợ", "Cam kết trị 100% để chốt"])
        if st.form_submit_button("Nộp Bài"):
            score = 0
            if q1 == "Nêu ngay vấn đề sâu bệnh và lợi ích giải pháp": score += 50
            if q2 == "Báo thông tin chưa có trong tài liệu chính thức và chuyển kỹ thuật hỗ trợ": score += 50
            st.write(f"Điểm bài test: **{score}/100**")
            if score >= 80:
                with get_db() as conn:
                    conn.execute("UPDATE users SET status = 'Đạt' WHERE id = ?", (user['id'],))
                    conn.commit()
                st.success("Bạn đã ĐẠT tiêu chuẩn đào tạo!")
