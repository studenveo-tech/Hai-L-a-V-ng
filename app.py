import os
import sqlite3
import json
import re
import streamlit as st
import pandas as pd
import bcrypt
from google import genai
from google.genai import types

# ----------------- CẤU HÌNH GIAO DIỆN -----------------
st.set_page_config(page_title="Đào Tạo Livestream - Hai Lúa Vàng", page_icon="🌾", layout="wide")

GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

def get_db():
    conn = sqlite3.connect("hailuavang.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- KHỞI TẠO CƠ SỞ DỮ LIỆU & NẠP SẢN PHẨM -----------------
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
            id INTEGER PRIMARY KEY,
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
        
        # Bảng Simulation Session
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
        
        # Tài khoản mặc định
        pwd_admin = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        pwd_trainee = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (1, 'admin', ?, 'Quản Lý Đào Tạo', 'admin')", (pwd_admin,))
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (2, 'nhanvien1', ?, 'Nguyễn Văn A', 'trainee')", (pwd_trainee,))
        
        # TOÀN BỘ DANH MỤC SẢN PHẨM HAI LÚA VÀNG
        products_data = [
            # --- NHÓM 1: THUỐC TRỪ SÂU - RẦY - BỌ TRĨ ---
            (
                1, "Thuốc trừ sâu RỒNG VÀNG 500EC", "Thuốc trừ sâu",
                "Lúa, Cây ăn trái (Sầu riêng, Cam, Bưởi), Rau màu",
                "Đặc trị sâu cuốn lá, rầy nâu, bọ trĩ, sâu tơ kháng thuốc",
                "Alpha-Cypermethrin 50g/l + Phụ gia sinh học loang trải", "Chai 450ml / Chai 100ml",
                "Pha 20-25ml cho bình 25L nước (hoặc 1 chai 450ml cho 400-500L nước)",
                "Phun khi sâu non mới nở hoặc rầy tuổi 1-2. Phun sáng sớm hoặc chiều mát.",
                "7 ngày",
                "Tác động tiếp xúc, vị độc, hạ gục cực nhanh, hạn chế sâu gối lứa.",
                "Cấm cam kết diệt sạch 100% vĩnh viễn không bao giờ tái phát."
            ),
            (
                2, "Thuốc trừ rầy RẦY CHÚA 700WG", "Thuốc trừ sâu",
                "Lúa, Xoài, Cây có múi, Cà phê",
                "Đặc trị rầy nâu hại lúa, rầy xanh, rầy chổng cánh, bọ trĩ",
                "Imidacloprid 700g/kg", "Gói 20g / Gói 100g",
                "Pha 1 gói 20g cho bình 25L nước",
                "Phun ướt đều tán lá và gốc lúa nơi rầy cư trú. Phun khi mật độ rầy chớm xuất hiện.",
                "7 - 14 ngày",
                "Nội hấp cực mạnh, lưu dẫn kéo dài, diệt cả rầy non lẫn rầy trưởng thành.",
                "Cấm tư vấn phun khi trời sắp mưa to mà không dùng kèm chất trợ lực."
            ),
            (
                3, "Thuốc trừ sâu sinh học BIOPRO 3.6EC", "Thuốc trừ sâu",
                "Rau màu sạch, Cây ăn trái, Chè, Lúa",
                "Sâu vẽ bùa, nhện đỏ, sâu đục quả, bọ trĩ",
                "Abamectin 3.6% w/v", "Chai 100ml / Chai 250ml",
                "Pha 10-15ml cho bình 25L nước",
                "Phun khi sâu non hoặc nhện chớm xuất hiện, phun kỹ 2 mặt lá.",
                "3 - 5 ngày (phù hợp canh tác nông sản sạch/VietGAP)",
                "Nguồn gốc sinh học an toàn, ít độc hại cho thiên địch và môi trường.",
                "Cấm khẳng định thuốc không độc hại và được uống thử."
            ),

            # --- NHÓM 2: THUỐC TRỪ BỆNH ---
            (
                4, "Thuốc trừ bệnh ĐẠO ÔN VÀNG 40WP", "Thuốc trừ bệnh",
                "Lúa",
                "Đặc trị đạo ôn lá (cháy lá) và đạo ôn cổ bông (thối cổ giáp)",
                "Isoprothiolane 40% w/w", "Gói 100g / Gói 500g",
                "Pha 30-40g cho bình 25L nước",
                "Phun phòng trước khi trổ hoặc khi vết bệnh chớm xuất hiện hình mắt én.",
                "7 ngày",
                "Hấp thu nhanh qua bề mặt lá, ngăn chặn sợi nấm phát triển, khô vết bệnh sau 24h.",
                "Cấm cam kết cứu sống ruộng đã bị thối cổ bông trắng hoàn toàn."
            ),
            (
                5, "Thuốc trừ bệnh NẤM KHUẨN SẠCH 300SC", "Thuốc trừ bệnh",
                "Lúa, Sầu riêng, Thanh long, Cà chua, Ớt",
                "Lem lép hạt, thán thư, đốm lá, xì mủ thân, cháy bìa lá do vi khuẩn",
                "Azoxystrobin + Difenoconazole", "Chai 250ml / Chai 500ml",
                "Pha 20-25ml cho bình 25L nước (Chai 250ml pha 200-250L nước)",
                "Phun phòng ở giai đoạn làm đòng, trước trổ và sau khi lúa trổ đều.",
                "10 - 14 ngày",
                "Phổ rộng, phòng trừ kép cả nấm và khuẩn, giúp xanh lá đòng, hạt lúa vàng sáng chắc.",
                "Cấm hứa hẹn tăng gấp đôi năng suất."
            ),
            (
                6, "Thuốc trừ bệnh KHÔ VẰN ĐẶC TRỊ 5SL", "Thuốc trừ bệnh",
                "Lúa, Ngô, Gừng",
                "Bệnh khô vằn (đốm vằn), lở cổ rễ",
                "Validamycin A 5%", "Chai 1000ml",
                "Pha 40-50ml cho bình 25L nước",
                "Phun tập trung vào phần gốc lúa khi bệnh mới chớm lan.",
                "7 ngày",
                "Gốc sinh học, chi phí cực kỳ tiết kiệm trên mỗi sào, ngăn lây lan diện rộng.",
                "Cấm tư vấn phun khi ruộng đang khô hạn nứt nẻ mà không bơm nước."
            ),

            # --- NHÓM 3: THUỐC TRỪ CỎ ---
            (
                7, "Thuốc trừ cỏ TIỀN NẢY MẦM HLV 300EC", "Thuốc trừ cỏ",
                "Lúa gieo thẳng (sạ)",
                "Cỏ lồng vực, cỏ cháo, cỏ chét, lúa cỏ mầm",
                "Pretilachlor 300g/l + Chất an toàn Fenclorim", "Chai 500ml / Chai 1000ml",
                "Pha 50-60ml cho bình 25L nước (1 chai 1L dùng cho 1 ha)",
                "Phun từ 1-3 ngày sau khi sạ, đất phải ẩm mịn nhưng không đọng vũng.",
                "Chưa có dữ liệu – cần hỏi bộ phận kỹ thuật.",
                "Có chất an toàn cao cấp giúp mầm lúa không bị quéo rễ, rụt đọt.",
                "Cấm cam kết xịt vào vũng nước sâu lúa vẫn không bị chết ngộp."
            ),
            (
                8, "Thuốc trừ cỏ HẬU NẢY MẦM CỎ CHÁY 20SL", "Thuốc trừ cỏ",
                "Đất không trồng trọt, bờ ruộng, vườn cây ăn trái (phun định hướng)",
                "Cỏ mần trầu, cỏ tranh, cỏ chỉ, cỏ lá rộng lâu năm",
                "Glufosinate Ammonium 200g/l", "Chai 1000ml",
                "Pha 100-120ml cho bình 25L nước",
                "Phun ướt đẫm khi cỏ đang phát triển mạnh. Dùng phễu chụp định hướng gốc cây trồng.",
                "Không áp dụng",
                "Tác động tiếp xúc cháy cỏ cực nhanh sau 2-3 ngày, phân hủy an toàn trong đất.",
                "Cấm tư vấn xịt trực tiếp trúng vào tán lá cây trồng chính."
            ),

            # --- NHÓM 4: PHÂN BÓN & DINH DƯỠNG CÂY TRỒNG ---
            (
                9, "Phân bón lá HẠT VÀNG NĂNG SUẤT", "Phân bón & Dinh dưỡng",
                "Lúa, Cây ăn trái, Cây công nghiệp",
                "Hiện tượng nghẹn đòng, lem lép hạt, hạt lép cậy, rụng hoa và trái non",
                "Đa trung vi lượng cao cấp: N, P, K, Bo hữu cơ, Kẽm Chelate", "Chai 500ml",
                "Pha 25-30ml cho bình 25L nước",
                "Phun giai đoạn nuôi đòng, chuẩn bị trổ và giai đoạn cong trái me (vào gạo).",
                "An toàn sinh học (Không cách ly)",
                "Giúp cứng cây chống đổ ngã, no hạt tới cậy, lá đòng xanh bền vững đến khi thu hoạch.",
                "Cấm khẳng định phun xong không cần bón phân gốc NPK."
            ),
            (
                10, "Dinh dưỡng sinh học ĐẺ NHÁNH TỐI ĐA", "Phân bón & Dinh dưỡng",
                "Lúa sạ, Mạ non, Cây giống",
                "Lúa đẻ nhánh kém, còi cọc do phèn mặn, rễ bó, nghẹt rễ sinh học",
                "Humic Acid tinh khiết 80% + Rong biển sinh học", "Gói 1kg / Xô 5kg",
                "Pha 1kg cho 400-500L nước tưới hoặc trộn đều cùng phân rải",
                "Dùng giai đoạn lúa 7-10 ngày và 18-22 ngày sau sạ.",
                "An toàn",
                "Kích rễ ra trắng xoá, giải độc phèn, hạ ngộ độc hữu cơ, bung nhánh hữu hiệu rộ.",
                "Cấm cam kết đất phèn nặng pH dưới 3 không cần bón vôi mà chỉ cần dùng thuốc."
            ),

            # --- NHÓM 5: CHẤT TRỢ LỰC & ĐIỀU HÒA SINH TRƯỞNG ---
            (
                11, "Chất trợ lực THẤM SÂU LOANG TRẢI HLV", "Chất trợ lực",
                "Mọi loại cây trồng (Pha chung với BVTV và Phân bón lá)",
                "Thuốc bị rửa trôi do mưa, bay hơi do nắng nóng, sâu bệnh trốn trong kẽ lá",
                "Silicone hữu cơ biến tính đặc biệt 100%", "Chai 100ml / Chai 500ml",
                "Pha 5ml cho bình 25L nước (siêu tiết kiệm)",
                "Pha vào nước khuấy đều trước khi cho thuốc BVTV hoặc phân bón vào.",
                "Theo thời gian cách ly của thuốc đi kèm",
                "Loang trải đều mặt lá sau 3 giây, thấm sâu qua tầng biểu bì, chống rửa trôi khi mưa sau 30 phút.",
                "Cấm tư vấn pha quá liều quy định gây cháy chóp lá non."
            )
        ]

        for p in products_data:
            cursor.execute("""
            INSERT OR REPLACE INTO products (
                id, name, category, target_crops, target_issues, active_ingredients, 
                specification, dosage, application_guide, isolation_period, key_selling_points, forbidden_claims
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, p)

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

# ----------------- ĐĂNG NHẬP -----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<h2 style='text-align: center; color: #16a34a;'>HỆ THỐNG ĐÀO TẠO LIVESTREAM HAI LÚA VÀNG</h2>", unsafe_allow_html=True)
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

# ----------------- THANH ĐIỀU HƯỚNG -----------------
user = st.session_state.user
st.sidebar.markdown(f"**👤 Nhân viên:** {user['full_name']}")
st.sidebar.markdown(f"**🔰 Quyền:** `{user['role'].upper()}` | **Trạng thái:** `{user['status']}`")

menu = st.sidebar.radio("DANH MỤC TÍNH NĂNG", [
    "🏠 Dashboard Tổng Quan",
    "📦 Hồ Sơ Kho Sản Phẩm",
    "🎤 Kịch Bản Livestream Tự Động",
    "🤖 AI Giả Lập Live & Chấm Điểm",
    "🧠 Bài Sát Hạch Kiến Thức",
    "🚪 Đăng Xuất"
])

if menu == "🚪 Đăng Xuất":
    st.session_state.user = None
    st.rerun()

elif menu == "🏠 Dashboard Tổng Quan":
    st.title("🏠 Dashboard Đào Tạo Livestream")
    with get_db() as conn:
        p_cnt = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        sim_cnt = conn.execute("SELECT COUNT(*) as c FROM simulation_sessions WHERE user_id = ?", (user['id'],)).fetchone()["c"]
        avg_s = conn.execute("SELECT AVG(total_score) as a FROM simulation_sessions WHERE user_id = ?", (user['id'],)).fetchone()["a"] or 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng Sản Phẩm Đã Nạp", f"{p_cnt} Sản phẩm")
    c2.metric("Số Phiên Luyện Tập Với AI", f"{sim_cnt} Phiên")
    c3.metric("Điểm Kỹ Năng Trung Bình", f"{avg_s:.1f}/100")

    st.divider()
    if avg_s >= 80:
        st.success("🏆 BẠN ĐÃ ĐỦ ĐIỀU KIỆN ĐỨNG LIVE CHÍNH THỨC (Điểm >= 80)")
    else:
        st.info("🎯 Mục tiêu: Đạt từ 80/100 điểm kỹ năng để được phê duyệt đứng live chính thức.")

elif menu == "📦 Hồ Sơ Kho Sản Phẩm":
    st.title("📦 Danh Mục Sản Phẩm Đã Xác Thực - Hai Lúa Vàng")
    
    with get_db() as conn:
        categories = [r['category'] for r in conn.execute("SELECT DISTINCT category FROM products").fetchall()]
        selected_cat = st.selectbox("Lọc theo nhóm sản phẩm:", ["Tất cả"] + categories)
        
        if selected_cat == "Tất cả":
            products = conn.execute("SELECT * FROM products ORDER BY category, id").fetchall()
        else:
            products = conn.execute("SELECT * FROM products WHERE category = ? ORDER BY id", (selected_cat,)).fetchall()

    st.write(f"Đang hiển thị **{len(products)}** sản phẩm:")
    
    for p in products:
        with st.expander(f"🏷️ {p['name']} - [{p['category']}]"):
            st.markdown(f"**🌱 Cây trồng phù hợp:** {p['target_crops']}")
            st.markdown(f"**🎯 Vấn đề đặc trị:** {p['target_issues']}")
            st.markdown(f"**🧪 Hoạt chất & Quy cách:** `{p['active_ingredients']}` | `{p['specification']}`")
            st.markdown(f"**💧 Liều lượng & Thời điểm:** {p['dosage']} — *{p['application_guide']}*")
            st.markdown(f"**⏱️ Thời gian cách ly:** {p['isolation_period']}")
            st.markdown(f"**✨ Điểm nhấn bán hàng (USP):** {p['key_selling_points']}")
            st.error(f"🚫 ĐIỀU CẤM KỴ TUYỆT ĐỐI KHÔNG NÓI: {p['forbidden_claims']}")

elif menu == "🎤 Kịch Bản Livestream Tự Động":
    st.title("🎤 Bộ Tạo Kịch Bản Livestream Tự Động")
    with get_db() as conn:
        products = [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]
    
    prod_map = {f"[{p['category']}] - {p['name']}": p for p in products}
    sel_name = st.selectbox("Chọn sản phẩm bạn muốn làm kịch bản:", list(prod_map.keys()))
    current_p = prod_map[sel_name]

    if st.button("🚀 Tạo Kịch Bản Đầy Đủ (5s Hook, Demo, CTA, Q&A)"):
        with st.spinner("AI đang tạo kịch bản bán hàng tối ưu..."):
            prompt = f"""
            Hãy tạo kịch bản bán hàng Livestream TikTok chi tiết cho sản phẩm: {current_p['name']}.
            Dữ liệu sản phẩm: {json.dumps(current_p, ensure_ascii=False)}

            Yêu cầu cấu trúc:
            1. 3 Câu Hook giật tệp 3-5s đánh thẳng vào nỗi sợ mất mùa/sâu bệnh.
            2. Đoạn mở đầu 30s tạo năng lượng và kết nối bà con nông dân.
            3. Xác định vấn đề thực tế trên đồng ruộng.
            4. Giới thiệu sản phẩm & Liều lượng (CHÍNH XÁC THEO DỮ LIỆU ĐƯỢC CẤP).
            5. Hướng dẫn MC cách Demo cầm chai/gói thuốc trước camera.
            6. 5 Câu hỏi thường gặp của nhà vườn và câu trả lời ngắn gọn.
            7. 3 Mẫu Kêu gọi hành động (CTA) dứt khoát.
            """
            res = call_gemini(prompt, str(current_p))
            st.markdown(res)

elif menu == "🤖 AI Giả Lập Live & Chấm Điểm":
    st.title("🤖 Luyện Tập Livestream Cùng Khách Hàng AI")
    with get_db() as conn:
        products = [dict(r) for r in conn.execute("SELECT * FROM products").fetchall()]
    
    prod_map = {f"[{p['category']}] - {p['name']}": p for p in products}
    sel_name = st.selectbox("Chọn sản phẩm muốn thực hành live:", list(prod_map.keys()))
    cur_p = prod_map[sel_name]

    if "chat_msgs" not in st.session_state:
        st.session_state.chat_msgs = []

    st.markdown(f"> **Đang live sản phẩm:** `{cur_p['name']}`")
    
    for m in st.session_state.chat_msgs:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    u_in = st.chat_input("Nhập lời thoại livestream của bạn...")
    if u_in:
        st.session_state.chat_msgs.append({"role": "user", "content": u_in})
        with st.chat_message("user"):
            st.markdown(u_in)

        sim_prompt = f"""
        Bạn là một bác nông dân miền Tây đang xem Livestream bán sản phẩm '{cur_p['name']}'.
        Tính cách: Thật thà, cẩn thận, hay thắc mắc về giá, sợ hàng giả, hỏi cách pha liều lượng cho ruộng nhà mình.
        Lịch sử trò chuyện: {st.session_state.chat_msgs}

        Hãy phản hồi lại bằng 1 câu bình luận ngắn gọn, tự nhiên, đúng chất nông dân.
        """
        reply = call_gemini(sim_prompt, str(cur_p), temp=0.7)
        st.session_state.chat_msgs.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)

    if st.button("📊 Kết Thúc & Chấm Điểm Toàn Diện"):
        if len(st.session_state.chat_msgs) < 2:
            st.warning("Vui lòng tương tác ít nhất 1-2 câu trước khi chấm điểm.")
        else:
            with st.spinner("AI đang phân tích 8 tiêu chuẩn livestream..."):
                eval_p = f"""
                Đánh giá toàn bộ đoạn hội thoại live sau:
                {json.dumps(st.session_state.chat_msgs, ensure_ascii=False)}

                Dữ liệu chuẩn của sản phẩm:
                {json.dumps(cur_p, ensure_ascii=False)}

                Trả về DUY NHẤT 1 chuỗi JSON hợp lệ không thừa chữ:
                {{
                    "total_score": 85,
                    "hook_score": 80,
                    "knowledge_score": 90,
                    "objection_score": 80,
                    "cta_score": 85,
                    "strengths": "Chỉ ra 2 điểm mạnh",
                    "weaknesses": "Chỉ ra điểm chưa tốt",
                    "relearning": "Kiến thức nông học cần xem lại"
                }}
                """
                raw = call_gemini(eval_p, str(cur_p), temp=0.1)
                try:
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    data = json.loads(match.group(0))
                    with get_db() as conn:
                        conn.execute("""
                        INSERT INTO simulation_sessions (
                            user_id, product_id, total_score, hook_score, knowledge_score, objection_score, cta_score,
                            feedback_strengths, feedback_weaknesses, feedback_relearning
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            user['id'], cur_p['id'], data['total_score'], data['hook_score'],
                            data['knowledge_score'], data['objection_score'], data['cta_score'],
                            data['strengths'], data['weaknesses'], data['relearning']
                        ))
                        conn.commit()

                    st.success(f"🎉 Điểm Tổng Kết: **{data['total_score']}/100**")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Kiến Thức Sản Phẩm", f"{data['knowledge_score']}/100")
                    c2.metric("Xử Lý Từ Chối", f"{data['objection_score']}/100")
                    c3.metric("Kêu Gọi Hành Động (CTA)", f"{data['cta_score']}/100")
                    st.write(f"- **Điểm mạnh:** {data['strengths']}")
                    st.write(f"- **Điểm cần khắc phục:** {data['weaknesses']}")
                    st.write(f"- **Nội dung cần ôn tập:** {data['relearning']}")
                except Exception:
                    st.write(raw)

elif menu == "🧠 Bài Sát Hạch Kiến Thức":
    st.title("🧠 Sát Hạch Chuẩn Hóa Livestream Nông Nghiệp")
    with st.form("quiz_form"):
        q1 = st.radio("1. Trong 3-5 giây đầu của phiên live, MC cần làm gì?", [
            "Đứng chào từng người và đợi đủ người xem",
            "Nêu ngay vấn đề sâu bệnh dịch hại đang vào mùa và lợi ích giải pháp",
            "Bật nhạc thật to"
        ])
        q2 = st.radio("2. Khi khách hàng hỏi một loại bệnh lạ chưa có trong hồ sơ sản phẩm, MC phải ứng xử ra sao?", [
            "Tự tư vấn theo kinh nghiệm để chốt đơn",
            "Cam kết 100% hết bệnh",
            "Báo với bà con dữ liệu này cần chuyển cho kỹ sư nông nghiệp của công ty hỗ trợ trực tiếp"
        ])
        q3 = st.radio("3. Khi khách chê 'sao thuốc mắc hơn loại xóm tôi bán', cách xử lý chuẩn là gì?", [
            "Cãi lại khách hàng",
            "Đồng cảm, chia nhỏ chi phí trên mỗi bình xịt và nhấn mạnh hiệu lực kéo dài chống rửa trôi",
            "Giảm giá tùy tiện ngay trên live"
        ])

        if st.form_submit_button("Nộp Bài Sát Hạch"):
            score = 0
            if q1 == "Nêu ngay vấn đề sâu bệnh dịch hại đang vào mùa và lợi ích giải pháp": score += 35
            if q2 == "Báo với bà con dữ liệu này cần chuyển cho kỹ sư nông nghiệp của công ty hỗ trợ trực tiếp": score += 35
            if q3 == "Đồng cảm, chia nhỏ chi phí trên mỗi bình xịt và nhấn mạnh hiệu lực kéo dài chống rửa trôi": score += 30
            
            st.write(f"Kết quả kiểm tra: **{score}/100**")
            if score >= 80:
                with get_db() as conn:
                    conn.execute("UPDATE users SET status = 'Đạt' WHERE id = ?", (user['id'],))
                    conn.commit()
                st.success("Chúc mừng! Bạn đã ĐẠT chuẩn sát hạch và đủ điều kiện đứng live.")
            else:
                st.error("Chưa đạt chuẩn 80 điểm. Vui lòng đọc kỹ hồ sơ sản phẩm và làm lại.")
