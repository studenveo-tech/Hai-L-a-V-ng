import os
import sqlite3
import streamlit as st
import pandas as pd
import bcrypt

# ----------------- CẤU HÌNH GIAO DIỆN -----------------
st.set_page_config(page_title="Hệ Thống Đào Tạo Livestream - Hai Lúa Vàng", page_icon="🌾", layout="wide")

def get_db():
    conn = sqlite3.connect("hailuavang.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- KHỞI TẠO CƠ SỞ DỮ LIỆU & TỰ ĐỘNG CẬP NHẬT CỘT -----------------
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tạo bảng Users nếu chưa có
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'trainee',
            status TEXT DEFAULT 'Đang đào tạo',
            exam_score REAL DEFAULT 0
        )""")

        # TỰ ĐỘNG BỔ SUNG CỘT exam_score NẾU DATABASE CŨ CHƯA CÓ
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if "exam_score" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN exam_score REAL DEFAULT 0")
        if "status" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'Đang đào tạo'")
        
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
        
        # Tạo tài khoản mặc định
        pwd_admin = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        pwd_trainee = bcrypt.hashpw("user123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (1, 'admin', ?, 'Quản Lý Đào Tạo', 'admin')", (pwd_admin,))
        cursor.execute("INSERT OR IGNORE INTO users (id, username, password_hash, full_name, role) VALUES (2, 'nhanvien1', ?, 'Nguyễn Văn A', 'trainee')", (pwd_trainee,))
        
        # Nạp danh mục sản phẩm chuẩn hóa Hai Lúa Vàng
        products_data = [
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
                "3 - 5 ngày (phù hợp VietGAP)",
                "Nguồn gốc sinh học an toàn, ít độc hại cho thiên địch và môi trường.",
                "Cấm khẳng định thuốc không độc hại và được uống thử."
            ),
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
                6, "Thuốc trừ cỏ TIỀN NẢY MẦM HLV 300EC", "Thuốc trừ cỏ",
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
                7, "Phân bón lá HẠT VÀNG NĂNG SUẤT", "Phân bón & Dinh dưỡng",
                "Lúa, Cây ăn trái, Cây công nghiệp",
                "Hiện tượng nghẹn đòng, lem lép hạt, hạt lép cậy, rụng hoa và trái non",
                "Đa trung vi lượng cao cấp: N, P, K, Bo hữu cơ, Kẽm Chelate", "Chai 500ml",
                "Pha 25-30ml cho bình 25L nước",
                "Phun giai đoạn nuôi đòng, chuẩn bị trổ và giai đoạn cong trái me (vào gạo).",
                "An toàn sinh học",
                "Giúp cứng cây chống đổ ngã, no hạt tới cậy, lá đòng xanh bền vững đến khi thu hoạch.",
                "Cấm khẳng định phun xong không cần bón phân gốc NPK."
            ),
            (
                8, "Chất trợ lực THẤM SÂU LOANG TRẢI HLV", "Chất trợ lực",
                "Mọi loại cây trồng (Pha chung với BVTV và Phân bón lá)",
                "Thuốc bị rửa trôi do mưa, bay hơi do nắng nóng, sâu bệnh trốn trong kẽ lá",
                "Silicone hữu cơ biến tính đặc biệt 100%", "Chai 100ml / Chai 500ml",
                "Pha 5ml cho bình 25L nước",
                "Pha vào nước khuấy đều trước khi cho thuốc BVTV hoặc phân bón vào.",
                "Theo thời gian cách ly của thuốc đi kèm",
                "Loang trải đều mặt lá sau 3 giây, thấm sâu qua tầng biểu bì, chống rửa trôi khi mưa.",
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

# ----------------- ĐĂNG NHẬP -----------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<h2 style='text-align: center; color: #16a34a;'>HỆ THỐNG ĐÀO TẠO LIVESTREAM HAI LÚA VÀNG</h2>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("login"):
            u = st.text_input("Tên đăng nhập (Mặc định: nhanvien1 hoặc admin)")
            p = st.text_input("Mật khẩu (Mặc định: user123 hoặc admin123)", type="password")
            if st.form_submit_button("Đăng Nhập"):
                with get_db() as conn:
                    res = conn.execute("SELECT * FROM users WHERE username = ?", (u,)).fetchone()
                    if res and bcrypt.checkpw(p.encode(), res["password_hash"].encode()):
                        st.session_state.user = dict(res)
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu.")
    st.stop()

# ----------------- THANH ĐIỀU HƯỚNG SIDEBAR -----------------
# Cập nhật lại thông tin user từ DB để luôn hiển thị đúng điểm số mới nhất
with get_db() as conn:
    updated_user = conn.execute("SELECT * FROM users WHERE id = ?", (st.session_state.user['id'],)).fetchone()
    if updated_user:
        st.session_state.user = dict(updated_user)

user = st.session_state.user
st.sidebar.markdown(f"**👤 Nhân viên:** {user['full_name']}")
st.sidebar.markdown(f"**🔰 Quyền:** `{user.get('role', 'trainee').upper()}` | **Trạng thái:** `{user.get('status', 'Đang đào tạo')}`")

menu = st.sidebar.radio("DANH MỤC ĐÀO TẠO", [
    "🏠 Dashboard",
    "📦 Hồ Sơ Kho Sản Phẩm",
    "💡 Kỹ Thuật & Tình Huống Streamer (12 Tình Huống)",
    "🧠 Bài Sát Hạch 10 Câu Hỏi Streamer",
    "🚪 Đăng Xuất"
])

if menu == "🚪 Đăng Xuất":
    st.session_state.user = None
    st.rerun()

elif menu == "🏠 Dashboard":
    st.title("🏠 Bảng Theo Dõi Đào Tạo Streamer")
    with get_db() as conn:
        p_cnt = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()["c"]
        cur_u = conn.execute("SELECT * FROM users WHERE id = ?", (user['id'],)).fetchone()

    score = cur_u["exam_score"] if cur_u and "exam_score" in cur_u.keys() and cur_u["exam_score"] is not None else 0
    status = cur_u["status"] if cur_u and "status" in cur_u.keys() and cur_u["status"] is not None else "Đang đào tạo"

    c1, c2, c3 = st.columns(3)
    c1.metric("Kho Sản Phẩm Đã Nạp", f"{p_cnt} Sản phẩm")
    c2.metric("Điểm Sát Hạch", f"{score}/100")
    c3.metric("Trạng Thái Đào Tạo", status)

    st.divider()
    if score >= 80:
        st.success("🏆 BẠN ĐÃ ĐẠT TIÊU CHUẨN ĐỨNG LIVESTREAM CHÍNH THỨC (Điểm >= 80)")
    else:
        st.info("📌 Hãy đọc kỹ kho sản phẩm, nghiên cứu 12 tình huống thực chiến và hoàn thành **Bài Sát Hạch** để được duyệt lên sóng.")

elif menu == "📦 Hồ Sơ Kho Sản Phẩm":
    st.title("📦 Danh Mục Sản Phẩm Đã Xác Thực - Hai Lúa Vàng")
    with get_db() as conn:
        categories = [r['category'] for r in conn.execute("SELECT DISTINCT category FROM products").fetchall()]
        selected_cat = st.selectbox("Lọc theo nhóm sản phẩm:", ["Tất cả"] + categories)
        
        if selected_cat == "Tất cả":
            products = conn.execute("SELECT * FROM products ORDER BY category, id").fetchall()
        else:
            products = conn.execute("SELECT * FROM products WHERE category = ? ORDER BY id", (selected_cat,)).fetchall()

    st.write(f"Tổng số: **{len(products)}** sản phẩm")
    for p in products:
        with st.expander(f"🏷️ {p['name']} - [{p['category']}]"):
            st.markdown(f"**🌱 Cây trồng:** {p['target_crops']}")
            st.markdown(f"**🎯 Trị vấn đề:** {p['target_issues']}")
            st.markdown(f"**🧪 Hoạt chất & Quy cách:** `{p['active_ingredients']}` | `{p['specification']}`")
            st.markdown(f"**💧 Liều lượng & Thời điểm:** {p['dosage']} — *{p['application_guide']}*")
            st.markdown(f"**⏱️ Thời gian cách ly:** {p['isolation_period']}")
            st.markdown(f"**✨ Điểm nhấn bán hàng (USP):** {p['key_selling_points']}")
            st.error(f"🚫 CẤM NÓI SAI SỰ THẬT: {p['forbidden_claims']}")

elif menu == "💡 Kỹ Thuật & Tình Huống Streamer (12 Tình Huống)":
    st.title("💡 Cẩm Nang Kỹ Thuật & Xử Lý Tình Huống Thực Chiến (12 Tình Huống)")
    st.caption("Bộ quy tắc phản xạ bắt buộc dành cho đội ngũ Streamer nông nghiệp Hai Lúa Vàng.")
    
    situations = [
        ("1. Mở đầu live chỉ có 2-5 người xem (Không bị 'khớp')",
         "👉 **Kỹ thuật:** Tuyệt đối không ngồi im hay than phiền vắng khách. Thuật toán TikTok phân phối video theo nội dung nói. Bắt đầu ngay câu Hook 5s: *'Bà con nào làm lúa đang bị sâu cuốn lá cắn bạc đọt xem ngay em chỉ cách xử lý êm ru sau 1 lần xịt!'*. Nói với năng lượng như đang có 1000 người xem."),
        
        ("2. Khách hàng bình luận chê 'Sao giá thuốc mắc hơn tiệm đầu xóm?'",
         "👉 **Kỹ thuật:** Đồng cảm và chia nhỏ chi phí trên từng bình xịt: *'Dạ em hiểu tâm lý bà con luôn muốn tiết kiệm chi phí mùa vụ. Nhưng chai này bà con pha được tới 20 bình xịt, tính ra mỗi bình chỉ mười mấy ngàn. Đặc biệt thuốc có chất loang trải thấm sâu, mưa sau 30 phút không bị rửa trôi, không phải xịt lại lần 2 tốn công và tiền thuốc.'*"),
        
        ("3. Khách hỏi bệnh cây ngoài danh mục dữ liệu của công ty",
         "👉 **Kỹ thuật:** Không suy đoán mò. Trả lời dứt khoát: *'Dạ tình trạng bệnh này của vườn bác cần phác đồ riêng biệt để tránh cháy lá. Em xin phép lưu lại thông tin và chuyển ngay cho đội ngũ kỹ sư nông nghiệp bên em gọi điện trực tiếp hướng dẫn bác phác đồ chuẩn nhất ạ.'*"),
        
        ("4. Xử lý bình luận công kích, phá rối (Troll / Chửi đổng)",
         "👉 **Kỹ thuật:** Giữ thái độ hòa nhã, tuyệt đối không đôi co tranh cãi. Đáp lời nhẹ nhàng: *'Dạ bên em cảm ơn đóng góp của bác. Em xin phép chia sẻ tiếp kỹ thuật cứu đòng cho các bác khác đang cần.'* Sau đó để trợ lý kỹ thuật âm thầm chặn/tắt tiếng tài khoản đó."),
        
        ("5. Tránh từ khóa cấm và quét vi phạm chính sách TikTok",
         "👉 **Kỹ thuật:** CẤM NÓI các từ tuyệt đối như: 'cam kết 100%', 'trị dứt điểm vĩnh viễn', 'thuốc độc nhất vô nhị', 'rẻ nhất thị trường', 'chữa bách bệnh'. Thay bằng: *'Giúp quản lý hiệu quả sâu bệnh'*, *'Hạn chế lây lan dịch hại'*, *'Tối ưu chi phí mùa vụ'*."),
        
        ("6. Kỹ thuật Demo trực quan cầm sản phẩm trước ống kính",
         "👉 **Kỹ thuật:** Cầm chai thuốc ngang ngực, ngón tay không che nhãn mác. Xoay nhẹ tem chống giả và mã vạch về phía camera để tạo niềm tin. Hướng dẫn chi tiết nắp đong định lượng và màu sắc nước thuốc khi hòa tan."),
        
        ("7. Khách hàng hỏi 'Thuốc này có pha chung với phân bón lá được không?'",
         "👉 **Kỹ thuật:** Dựa đúng hồ sơ sản phẩm: *'Dạ dòng thuốc này dạng SC/EC sinh học phối hợp rất tốt với phân bón lá Hạt Vàng Năng Suất. Tuy nhiên bà con lưu ý không phối chung với các gốc thuốc có tính kiềm mạnh để giữ hiệu lực cao nhất.'*"),
        
        ("8. Giữ chân người xem khi mắt xem có dấu hiệu giảm dần",
         "👉 **Kỹ thuật:** Tạo sự tò mò (Open Loop) và mini-game hỏi đáp: *'Bác nào đang có mặt trên live để lại cho em dấu chấm hoặc bình luận loại cây trồng nhà mình, 3 phút nữa em sẽ chia sẻ mẹo xịt thuốc không lo rụng bông đậu trái non cực kỳ hiệu quả!'*"),
        
        ("9. Kỹ thuật Kêu gọi hành động (CTA) dứt khoát chuyển đổi đơn",
         "👉 **Kỹ thuật:** Kêu gọi theo hành động đơn giản, đừng nói mơ hồ. *'Bác nào đang bị rầy chớm xuất hiện thì bấm ngay vào góc trái màn hình, chọn combo 2 chai để được hỗ trợ giao hàng tận nhà và tặng kèm tài liệu kỹ thuật mùa vụ!'*"),
        
        ("10. Khách hàng comment: 'Tôi mua đợt trước xịt không thấy giảm sâu'",
         "👉 **Kỹ thuật:** Hỏi thăm kỹ thuật phun để tìm nguyên nhân: *'Dạ bác xịt lúc sáng sớm hay trưa nắng và pha bao nhiêu lít nước ạ? Thường sâu gối lứa hoặc phun không trúng ổ rầy dưới gốc thì thuốc khó tiếp xúc. Bác nhắn lại cho bên em, kỹ sư sẽ rà soát lại cách pha chỉnh lại liều chuẩn cho bác liền.'*"),
        
        ("11. Xử lý sự cố kỹ thuật bất ngờ (Rớt mạng, mic rè, đổ vỡ đạo cụ)",
         "👉 **Kỹ thuật:** Bình tĩnh mỉm cười, làm chủ tình hình: *'Dạ đường truyền bên em vừa chớp một xíu do mưa gió ngoài đồng ruộng. Em đã quay trở lại rồi đây bà con ơi, em tiếp tục hướng dẫn công thức pha cho bình 25 lít nhé.'*"),
        
        ("12. Tạo cảm giác khan hiếm và lý do mua hàng chính đáng",
         "👉 **Kỹ thuật:** Không tự bịa khuyến mãi vô lý. Tận dụng chính sách có sẵn: *'Dạ đợt hàng này công ty về số lượng giới hạn phục vụ cho đầu vụ Đông Xuân. Bác nào chốt sớm trong live hôm nay sẽ được đội ngũ kỹ sư đồng hành tư vấn suốt mùa vụ.'*")
    ]
    
    for title, content in situations:
        with st.expander(title):
            st.markdown(content)

elif menu == "🧠 Bài Sát Hạch 10 Câu Hỏi Streamer":
    st.title("🧠 Sát Hạch Kỹ Năng & Kiến Thức Streamer Bán Hàng (10 Câu)")
    st.info("Mỗi câu đúng tương ứng 10 điểm. Điểm đạt chuẩn để đứng live là từ **80/100 điểm**.")

    with st.form("exam_10_questions"):
        ans = []
        
        st.markdown("##### Câu 1: Nhiệm vụ quan trọng nhất trong 3–5 giây đầu tiên của phiên Livestream là gì?")
        q1 = st.radio("Chọn câu trả lời:", [
            "A. Chào hỏi từng người vào xem và mở nhạc lớn",
            "B. Nêu ngay vấn đề/dịch hại bà con đang gặp và đưa ra giải pháp thu hút (Hook)",
            "C. Đứng im chờ mắt xem vượt qua 50 người mới bắt đầu nói"
        ], key="q1")
        ans.append(q1.startswith("B"))

        st.markdown("##### Câu 2: Khi khách hàng bình luận chê sản phẩm giá đắt, phản ứng nào sau đây là CHUẨN NHẤT?")
        q2 = st.radio("Chọn câu trả lời:", [
            "A. Tự ý tuyên bố giảm giá ngay trên sóng trực tiếp",
            "B. Tranh luận gay gắt và bảo khách hàng 'tiền nào của nấy'",
            "C. Đồng cảm, phân tích hiệu quả thấm sâu/chống rửa trôi và chia nhỏ chi phí trên mỗi bình xịt"
        ], key="q2")
        ans.append(q2.startswith("C"))

        st.markdown("##### Câu 3: Khách hàng hỏi tư vấn một loại bệnh cây trồng chưa có trong dữ liệu công ty, streamer phải làm gì?")
        q3 = st.radio("Chọn câu trả lời:", [
            "A. Tự suy đoán theo kinh nghiệm cá nhân để chốt đơn cho bằng được",
            "B. Khẳng định thuốc trị được 100% mọi loại nấm bệnh",
            "C. Thông báo trung thực và xin thông tin chuyển cho bộ phận kỹ thuật nông nghiệp hỗ trợ"
        ], key="q3")
        ans.append(q3.startswith("C"))

        st.markdown("##### Câu 4: Cụm từ nào sau đây VI PHẠM chính sách của TikTok và quy định công ty?")
        q4 = st.radio("Chọn câu trả lời:", [
            "A. 'Hỗ trợ bảo vệ đòng lúa, lá đòng xanh bền vững'",
            "B. 'Cam kết diệt sạch 100% vĩnh viễn không bao giờ tái phát'",
            "C. 'Bà con nên phun vào sáng sớm hoặc chiều mát'"
        ], key="q4")
        ans.append(q4.startswith("B"))

        st.markdown("##### Câu 5: Khi thực hiện thao tác Demo sản phẩm trên livestream, streamer cần chú ý điều gì?")
        q5 = st.radio("Chọn câu trả lời:", [
            "A. Cầm sản phẩm ngang tầm ngực, quay rõ nhãn mác, tem chống giả về phía camera",
            "B. Giơ sản phẩm thật nhanh rồi cất ngay xuống bàn",
            "C. Vừa cầm sản phẩm vừa quay lưng lại phía ống kính"
        ], key="q5")
        ans.append(q5.startswith("A"))

        st.markdown("##### Câu 6: Công dụng cốt lõi của 'Chất trợ lực Thấm Sâu Loang Trải HLV' là gì?")
        q6 = st.radio("Chọn câu trả lời:", [
            "A. Thay thế hoàn toàn phân bón gốc NPK",
            "B. Giúp thuốc loang trải nhanh, thấm sâu, hạn chế bị nước mưa rửa trôi",
            "C. Diệt trừ tất cả các loại cỏ dại trên bờ ruộng"
        ], key="q6")
        ans.append(q6.startswith("B"))

        st.markdown("##### Câu 7: Một câu Kêu gọi hành động (CTA) hiệu quả trên live cần đạt tiêu chí gì?")
        q7 = st.radio("Chọn câu trả lời:", [
            "A. Ngắn gọn, rõ ràng, hướng dẫn bà con bấm giỏ hàng hoặc để lại tên cây trồng + vấn đề",
            "B. Dài dòng, giải thích nhiều điều khoản phức tạp",
            "C. Nói một lần duy nhất vào cuối phiên livestream"
        ], key="q7")
        ans.append(q7.startswith("A"))

        st.markdown("##### Câu 8: Khi phòng trừ bệnh Đạo ôn cổ bông trên lúa, thời điểm phun quan trọng nhất là khi nào?")
        q8 = st.radio("Chọn câu trả lời:", [
            "A. Khi bông lúa đã chín vàng chuẩn bị gặt",
            "B. Phun phòng ở giai đoạn trước trổ (lẹt xẹt) và sau khi trổ đều",
            "C. Khi cây lúa mới mọc được 3 ngày sau sạ"
        ], key="q8")
        ans.append(q8.startswith("B"))

        st.markdown("##### Câu 9: Thuốc trừ cỏ HẬU NẢY MẦM tiếp xúc cần được sử dụng như thế nào để an toàn cho cây trồng chính?")
        q9 = st.radio("Chọn câu trả lời:", [
            "A. Phun trùm thẳng lên đọt cây ăn trái",
            "B. Phun định hướng bằng phễu chụp, tránh để hạt thuốc bay trúng tán lá cây trồng",
            "C. Hòa chung với nước tưới nhỏ giọt"
        ], key="q9")
        ans.append(q9.startswith("B"))

        st.markdown("##### Câu 10: Streamer có được tự ý công bố chương trình 'Mua 1 tặng 1' hoặc giảm giá 50% trên sóng không?")
        q10 = st.radio("Chọn câu trả lời:", [
            "A. Được, miễn sao chốt được nhiều đơn là được",
            "B. Không được, chỉ được công bố các chương trình khuyến mãi đã được công ty duyệt chính thức",
            "C. Tự do quyết định theo cảm xúc lúc live"
        ], key="q10")
        ans.append(q10.startswith("B"))

        submit = st.form_submit_button("📩 NỘP BÀI SÁT HẠCH")
        if submit:
            correct_count = sum(ans)
            final_score = correct_count * 10
            
            with get_db() as conn:
                new_status = "Đạt" if final_score >= 80 else "Chưa đạt"
                conn.execute("UPDATE users SET exam_score = ?, status = ? WHERE id = ?", (final_score, new_status, user['id']))
                conn.commit()
            
            # Cập nhật ngay lập tức vào phiên đăng nhập hiện tại
            st.session_state.user['exam_score'] = final_score
            st.session_state.user['status'] = new_status

            st.divider()
            if final_score >= 80:
                st.success(f"🎉 XUẤT SẮC! BẠN ĐÃ ĐẠT {final_score}/100 ĐIỂM ({correct_count}/10 câu đúng).")
                st.balloons()
            else:
                st.error(f"⚠️ KẾT QUẢ: {final_score}/100 ĐIỂM ({correct_count}/10 câu đúng). Chưa đạt tiêu chuẩn 80 điểm. Hãy ôn tập lại cẩm nang kỹ thuật và làm lại bài kiểm tra.")
