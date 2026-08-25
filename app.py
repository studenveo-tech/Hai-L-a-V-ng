import sqlite3
import streamlit as st
import pandas as pd

# ----------------- CẤU HÌNH GIAO DIỆN -----------------
st.set_page_config(
    page_title="Hệ Thống Đào Tạo Livestream - Hai Lúa Vàng",
    page_icon="🌾",
    layout="wide"
)

# Tùy biến nhẹ giao diện cho chuyên nghiệp
st.markdown("""
<style>
    .main-header { font-size: 24px; font-weight: bold; color: #15803d; margin-bottom: 10px; }
    .rule-box { background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
    .formula-box { background-color: #fefce8; border: 1px solid #facc15; padding: 15px; border-radius: 8px; font-weight: bold; color: #854d0e; text-align: center; font-size: 16px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

def get_db():
    conn = sqlite3.connect("hailuavang.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- KHỞI TẠO CƠ SỞ DỮ LIỆU & SẢN PHẨM -----------------
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
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

        # Bảng lưu kết quả thi sát hạch (không cần login)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainee_name TEXT NOT NULL,
            score REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # NẠP TOÀN BỘ SẢN PHẨM MỞ RỘNG HAI LÚA VÀNG
        products_data = [
            # --- 1. THUỐC TRỪ SÂU - RẦY - BỌ TRĨ - NHỆN ---
            (
                1, "Thuốc trừ sâu RỒNG VÀNG 500EC", "Thuốc trừ sâu",
                "Lúa, Cây ăn trái (Sầu riêng, Cam, Bưởi, Xoài), Rau màu",
                "Đặc trị sâu cuốn lá, rầy nâu, bọ trĩ, sâu tơ, sâu đục thân kháng thuốc",
                "Alpha-Cypermethrin 50g/l + Phụ gia sinh học loang trải", "Chai 450ml / Chai 100ml",
                "Pha 20-25ml cho bình 25L nước (Chai 450ml pha 400-500L nước)",
                "Phun khi sâu non mới nở hoặc rầy tuổi 1-2. Phun sáng sớm hoặc chiều mát.",
                "7 ngày",
                "Tác động tiếp xúc và vị độc cực mạnh, hạ gục sâu rầy tức thì, hạn chế sâu gối lứa.",
                "Cấm cam kết diệt sạch 100% vĩnh viễn không bao giờ tái phát."
            ),
            (
                2, "Thuốc trừ rầy RẦY CHÚA 700WG", "Thuốc trừ sâu",
                "Lúa, Xoài, Cây có múi, Cà phê, Tiêu",
                "Đặc trị rầy nâu hại lúa, rầy xanh, rầy chổng cánh, rầy bông xoài",
                "Imidacloprid 700g/kg", "Gói 20g / Gói 100g",
                "Pha 1 gói 20g cho bình 25L nước",
                "Phun ướt đều tán lá và phần gốc lúa nơi rầy cư trú. Phun khi mật độ rầy chớm nở.",
                "7 - 14 ngày",
                "Cơ chế nội hấp lưu dẫn cực mạnh, diệt cả rầy non lẫn rầy trưởng thành, bảo vệ chồi non.",
                "Cấm tư vấn phun khi trời sắp mưa to mà không pha kèm chất trợ lực."
            ),
            (
                3, "Thuốc trừ sâu sinh học BIOPRO 3.6EC", "Thuốc trừ sâu",
                "Rau màu sạch, Cây ăn trái, Cây chè, Hoa kiểng",
                "Sâu vẽ bùa, nhện đỏ, bọ trĩ, sâu đục quả",
                "Abamectin 3.6% w/v", "Chai 100ml / Chai 250ml",
                "Pha 10-15ml cho bình 25L nước",
                "Phun ướt đều 2 mặt lá khi nhện đỏ hoặc sâu non mới xuất hiện.",
                "3 - 5 ngày (Phù hợp quy trình VietGAP)",
                "Gốc sinh học an toàn cao, phân hủy nhanh, ít ảnh hưởng đến thiên địch có ích.",
                "Cấm khẳng định thuốc không có độc và được uống thử."
            ),

            # --- 2. THUỐC TRỪ ỐC BƯƠU VÀNG ---
            (
                4, "Thuốc trừ ốc DIỆT ỐC BƯƠU VÀNG 70WP", "Thuốc trừ ốc",
                "Lúa sạ, ruộng ngập nước",
                "Ốc bươu vàng cắn phá mầm lúa non và lúa mới cấy",
                "Niclosamide 70% w/w", "Gói 100g",
                "Pha 1 gói 100g cho bình 25L nước (hoặc 3-4 gói cho 1 ha)",
                "Phun khi cho nước vào ruộng trước khi sạ hoặc sau khi sạ 3-5 ngày khi đưa nước vào.",
                "Không áp dụng",
                "Dẫn dụ cực nhanh, làm ốc tê liệt miệng không cắn phá mầm được và chết rũ.",
                "Cấm xịt trực tiếp vào nguồn nước nuôi cá tôm chuyên canh."
            ),

            # --- 3. THUỐC TRỪ BỆNH ---
            (
                5, "Thuốc trừ bệnh ĐẠO ÔN VÀNG 40WP", "Thuốc trừ bệnh",
                "Lúa",
                "Đặc trị đạo ôn lá (cháy lá) và đạo ôn cổ bông (thối cổ giáp)",
                "Isoprothiolane 40% w/w", "Gói 100g / Gói 500g",
                "Pha 30-40g cho bình 25L nước",
                "Phun phòng trước khi trổ (lẹt xẹt) và sau khi lúa trổ đều.",
                "7 ngày",
                "Hấp thu nhanh qua mô lá, ngăn chặn sợi nấm phát triển, làm khô nhanh vết bệnh hình mắt én.",
                "Cấm cam kết cứu sống ruộng lúa đã bị gãy gục cổ bông trắng hoàn toàn."
            ),
            (
                6, "Thuốc trừ bệnh NẤM KHUẨN SẠCH 300SC", "Thuốc trừ bệnh",
                "Lúa, Sầu riêng, Thanh long, Ớt, Cà chua",
                "Lem lép hạt, thán thư, xì mủ thân, cháy bìa lá do vi khuẩn",
                "Azoxystrobin + Difenoconazole", "Chai 250ml / Chai 500ml",
                "Pha 20-25ml cho bình 25L nước (Chai 250ml dùng cho 200-250L nước)",
                "Phun phòng ở giai đoạn làm đòng, trước trổ và sau khi trổ đều.",
                "10 - 14 ngày",
                "Phổ tác động rộng, phòng trị kép nấm khuẩn, giúp lá đòng xanh mướt, hạt vàng sáng chắc.",
                "Cấm hứa hẹn tăng năng suất gấp đôi nếu không bón phân đầy đủ."
            ),
            (
                7, "Thuốc trừ bệnh KHÔ VẰN ĐẶC TRỊ 5SL", "Thuốc trừ bệnh",
                "Lúa, Ngô, Gừng",
                "Bệnh khô vằn (đốm vằn), lở cổ rễ",
                "Validamycin A 5%", "Chai 1000ml",
                "Pha 40-50ml cho bình 25L nước",
                "Phun tập trung vào phần gốc thân lúa khi bệnh mới chớm lan mé mương.",
                "7 ngày",
                "Chi phí cực kỳ tiết kiệm, chặn đứng vết loang của sợi nấm bẹ lá.",
                "Cấm tư vấn phun khi ruộng khô nứt nẻ không đủ độ ẩm dẫn thuốc."
            ),

            # --- 4. THUỐC TRỪ CỎ ---
            (
                8, "Thuốc trừ cỏ TIỀN NẢY MẦM HLV 300EC", "Thuốc trừ cỏ",
                "Lúa gieo thẳng (sạ)",
                "Cỏ lồng vực, cỏ cháo, cỏ chét, lúa cỏ mầm",
                "Pretilachlor 300g/l + Chất an toàn Fenclorim", "Chai 500ml / Chai 1000ml",
                "Pha 50-60ml cho bình 25L nước (1 chai 1L dùng cho 1 ha)",
                "Phun từ 1-3 ngày sau sạ, mặt ruộng đủ ẩm mịn, không để đọng vũng sâu.",
                "Chưa có dữ liệu – cần hỏi bộ phận kỹ thuật.",
                "Chứa chất an toàn cao cấp giúp mầm lúa không bị quéo rễ, rụt đọt.",
                "Cấm cam kết xịt vào ruộng trũng đọng nước sâu mà mầm lúa vẫn an toàn 100%."
            ),
            (
                9, "Thuốc trừ cỏ HẬU NẢY MẦM CỎ CHÁY 20SL", "Thuốc trừ cỏ",
                "Đất hoang, bờ ruộng, vườn cây ăn trái (phun định hướng)",
                "Cỏ mần trầu, cỏ tranh, cỏ chỉ, cỏ tạp lâu năm",
                "Glufosinate Ammonium 200g/l", "Chai 1000ml",
                "Pha 100-120ml cho bình 25L nước",
                "Phun ướt đẫm khi cỏ đang xanh tốt. Dùng phễu chụp định hướng tránh tán cây trồng.",
                "Không áp dụng",
                "Cháy nhanh sau 2-3 ngày, diệt sạch phần thân lá, phân hủy an toàn trong đất.",
                "Cấm tư vấn xịt trực tiếp trúng vào tán lá non cây ăn trái."
            ),

            # --- 5. PHÂN BÓN & DINH DƯỠNG CÂY TRỒNG ---
            (
                10, "Phân bón lá HẠT VÀNG NĂNG SUẤT", "Phân bón & Dinh dưỡng",
                "Lúa, Cây ăn trái, Cây công nghiệp",
                "Nghẹn đòng, lem lép hạt, rụng hoa và trái non, hạt lép cậy",
                "Đa trung vi lượng cao cấp: N, P, K, Bo hữu cơ, Kẽm Chelate", "Chai 500ml",
                "Pha 25-30ml cho bình 25L nước",
                "Phun giai đoạn nuôi đòng, chuẩn bị trổ và giai đoạn cong trái me (vào gạo).",
                "An toàn sinh học",
                "Cứng cây đứng lá chống đổ ngã, vô gạo cực nhanh, hạt no tới cậy, vàng sáng.",
                "Cấm khẳng định phun phân bón lá xong thì không cần rải phân gốc NPK."
            ),
            (
                11, "Dinh dưỡng KÍCH RỄ ĐẺ NHÁNH BIO", "Phân bón & Dinh dưỡng",
                "Lúa sạ, Cây con, Cây ăn quả sau thu hoạch",
                "Rễ nghẹt phèn, vàng lá sinh lý, lúa đẻ nhánh kém, còi cọc",
                "Humic Acid tinh khiết 80% + Fulvic Acid + Amino Acid", "Gói 1kg / Xô 5kg",
                "Pha 1kg cho 400-500L nước tưới hoặc trộn đều cùng phân rải đợt 1-2",
                "Sử dụng giai đoạn 7-12 ngày và 18-22 ngày sau khi sạ.",
                "An toàn sinh học",
                "Kích rễ ra trắng mập, hạ phèn nhanh, bung nhánh hữu hiệu rộ, mập đọt.",
                "Cấm cam kết đất nhiễm mặn nặng không cần xả nước mà chỉ tưới thuốc là hết."
            ),
            (
                12, "Thuốc kích thích sinh trưởng VIÊN GA3 VÀNG", "Điều hòa sinh trưởng",
                "Lúa, Thanh long, Xoài, Rau màu",
                "Lúa nghẹn đòng, trổ không thoát, chồi phát triển chậm",
                "Gibberellic Acid (GA3) 20%", "Viên sủi 5g",
                "Pha 1 viên cho 200L nước (hoặc 1/4 viên cho bình 25L nước)",
                "Phun khi lúa chuẩn bị trổ hoặc trổ nghẹn do thời tiết lạnh.",
                "3 ngày",
                "Kích vọt đòng cực mạnh, trổ đều đồng loạt, kéo dài cuống hoa và chồi non.",
                "Cấm tư vấn dùng quá liều gây hiện tượng vống cây, yếu ớt dễ đổ ngã."
            ),

            # --- 6. CHẤT TRỢ LỰC ---
            (
                13, "Chất trợ lực THẤM SÂU LOANG TRẢI HLV", "Chất trợ lực",
                "Mọi loại cây trồng (Pha chung với BVTV và Phân bón lá)",
                "Thuốc bị rửa trôi khi trời mưa, bay hơi khi nắng gắt, sâu ẩn nấp kẽ lá",
                "Silicone hữu cơ biến tính đặc biệt 100%", "Chai 100ml / Chai 500ml",
                "Pha 5ml cho bình 25L nước",
                "Hòa tan vào nước khuấy đều trước khi đổ thuốc BVTV hoặc phân bón vào.",
                "Theo thời gian cách ly của thuốc đi kèm",
                "Loang trải phủ kín mặt lá sau 3 giây, dẫn thuốc thấm sâu cực nhanh, chống rửa trôi sau 30 phút.",
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

# ----------------- THANH ĐIỀU HƯỚNG BÊN TRÁI -----------------
st.sidebar.title("🌾 HAI LÚA VÀNG")
st.sidebar.caption("Hệ Thống Đào Tạo Livestream Nông Nghiệp")

menu = st.sidebar.radio("CHỌN MỤC HỌC TẬP", [
    "⭐ 7 Nguyên Tắc Livestream Vàng",
    "📦 Hồ Sơ Kho Sản Phẩm",
    "💡 Kỹ Thuật & Tình Huống Thực Chiến",
    "🧠 Bài Sát Hạch 10 Câu Hỏi Streamer",
    "📊 Bảng Điểm & Quản Lý Đào Tạo"
])

# ----------------- 1. NGUYÊN TẮC LIVESTREAM -----------------
if menu == "⭐ 7 Nguyên Tắc Livestream Vàng":
    st.markdown("<div class='main-header'>⭐ 7 NGUYÊN TẮC LIVESTREAM BÁN HÀNG ĐỈNH CAO</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='formula-box'>
        👉 CÔNG THỨC VÀNG BẤT BIẾN:<br>
        THU HÚT → TẠO TIN TƯỞNG → DEMO → TƯƠNG TÁC → ƯU ĐÃI → CHỐT ĐƠN
    </div>
    """, unsafe_allow_html=True)

    rules = [
        ("1. Hook Mạnh (3–5 Giây Đầu)", "Nói ngay lợi ích hoặc vấn đề nóng hổi mà bà con đang lo lắng nhất trong mùa vụ. Không mở đầu bằng việc đứng chào hỏi rườm rà hay chờ đợi mắt xem. Đánh trúng nỗi sợ mất mùa hoặc chi phí tăng cao."),
        ("2. Nói Đúng Nhu Cầu Khách Hàng", "Đừng chỉ đọc thông số kỹ thuật khô khan. Hãy xuất phát từ bệnh của ruộng vườn: Lúa đang nghẹn đòng, sâu cuốn lá cắn rách đọt, hay rầy nâu kháng thuốc? Kết nối vấn đề đó với giải pháp của sản phẩm."),
        ("3. Demo Thực Tế Trực Quan", "Cho khách thấy rõ sản phẩm hoạt động như thế nào. Cầm chai/gói thuốc ngang tầm ngực, chỉ rõ tem chống giả, nắp đong liều lượng, thử độ loang trải hoặc minh họa khả năng hòa tan nước thuốc."),
        ("4. Tương Tác Liên Tục 2 Chiều", "Liên tục đọc bình luận, gọi đúng tên bà con và địa phương (Ví dụ: 'Dạ em chào anh Ba ở Đồng Tháp', 'Bác Tư ở An Giang lúa được bao nhiêu ngày rồi?'). Chủ động đặt câu hỏi để người xem trả lời."),
        ("5. CTA (Kêu Gọi Hành Động) Rõ Ràng", "Lời kêu gọi phải cụ thể và dứt khoát: 'Bà con comment ngay tên cây trồng + diện tích để nhận phác đồ', 'Nhấn ngay vào góc trái màn hình để đặt hàng nhận ưu đãi giao tận nhà'."),
        ("6. Tạo Lý Do Mua Ngay", "Tạo động lực bằng các ưu đãi chính thức: Combo tiết kiệm mùa vụ, quà tặng kèm, hỗ trợ phí vận chuyển hoặc số lượng phân bổ có hạn trong khung giờ live. Tuyệt đối KHÔNG tự ý bịa khuyến mãi nếu công ty chưa duyệt."),
        ("7. Kịch Bản Chuẩn Nhưng Nói Tự Nhiên", "Kịch bản là khung sườn để không bỏ sót thông tin, nhưng giọng điệu phải mộc mạc, gần gũi như một người bạn nhà nông, tránh đọc thuộc lòng như một cái máy quảng cáo.")
    ]

    for title, desc in rules:
        st.markdown(f"""
        <div class='rule-box'>
            <b style='color: #15803d; font-size: 16px;'>{title}</b><br>
            <span style='color: #374151;'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)

# ----------------- 2. HỒ SƠ KHO SẢN PHẨM -----------------
elif menu == "📦 Hồ Sơ Kho Sản Phẩm":
    st.markdown("<div class='main-header'>📦 DANH MỤC SẢN PHẨM ĐÃ XÁC THỰC - HAI LÚA VÀNG</div>", unsafe_allow_html=True)
    st.caption("Dữ liệu chuẩn hóa chính thức từ website hailuavang.com.vn - Nghiêm cấm tư vấn sai thông số kỹ thuật.")
    
    with get_db() as conn:
        categories = [r['category'] for r in conn.execute("SELECT DISTINCT category FROM products").fetchall()]
        selected_cat = st.selectbox("Lọc theo nhóm sản phẩm:", ["Tất cả"] + categories)
        
        if selected_cat == "Tất cả":
            products = conn.execute("SELECT * FROM products ORDER BY category, id").fetchall()
        else:
            products = conn.execute("SELECT * FROM products WHERE category = ? ORDER BY id", (selected_cat,)).fetchall()

    st.write(f"Đang hiển thị **{len(products)}** sản phẩm:")
    for p in products:
        with st.expander(f"🏷️ {p['name']} — [{p['category']}]"):
            st.markdown(f"**🌱 Cây trồng đăng ký:** {p['target_crops']}")
            st.markdown(f"**🎯 Đối tượng đặc trị:** {p['target_issues']}")
            st.markdown(f"**🧪 Hoạt chất & Quy cách:** `{p['active_ingredients']}` | `{p['specification']}`")
            st.markdown(f"**💧 Liều lượng & Thời điểm:** {p['dosage']} — *{p['application_guide']}*")
            st.markdown(f"**⏱️ Thời gian cách ly:** {p['isolation_period']}")
            st.markdown(f"**✨ Điểm nhấn bán hàng (USP):** {p['key_selling_points']}")
            st.error(f"🚫 CẤM KỴ TUYỆT ĐỐI: {p['forbidden_claims']}")

# ----------------- 3. KỸ THUẬT & TÌNH HUỐNG THỰC CHIẾN -----------------
elif menu == "💡 Kỹ Thuật & Tình Huống Thực Chiến":
    st.markdown("<div class='main-header'>💡 CẨM NANG KỸ THUẬT & XỬ LÝ TÌNH HUỐNG THỰC CHIẾN</div>", unsafe_allow_html=True)
    st.caption("Tổng hợp toàn bộ phản xạ ứng biến nhanh trên sóng trực tiếp dành cho đội ngũ streamer.")
    
    situations = [
        ("Mở đầu live chỉ có 2-5 người xem (Không bị 'khớp')",
         "👉 **Phản xạ chuẩn:** Tuyệt đối không ngồi im hay than thở vắng khách. Thuật toán phân phối theo nội dung giọng nói. Bắt đầu ngay câu Hook 5s: *'Bà con nào làm lúa đang bị sâu cuốn lá cắn bạc đọt xem ngay em chỉ cách xử lý êm ru sau 1 lần xịt!'*. Giữ năng lượng như đang có 1.000 người theo dõi."),
        
        ("Khách hàng bình luận chê 'Sao giá thuốc mắc hơn tiệm ngoài chợ?'",
         "👉 **Phản xạ chuẩn:** Đồng cảm và chia nhỏ chi phí trên từng bình xịt: *'Dạ em hiểu tâm lý bà con luôn muốn tiết kiệm chi phí đầu vụ. Nhưng chai này bà con pha được tới 20 bình xịt, tính ra mỗi bình chỉ mười mấy ngàn. Thuốc có sẵn chất loang trải thấm sâu, mưa sau 30 phút không bị rửa trôi, không phải tốn tiền mua thuốc xịt lại lần 2.'*"),
        
        ("Khách hỏi bệnh lạ của cây ngoài danh mục dữ liệu công ty",
         "👉 **Phản xạ chuẩn:** Không tự suy đoán liều. Trả lời trung thực: *'Dạ tình trạng bệnh này của vườn bác cần phác đồ riêng biệt để tránh cháy lá non. Bác để lại tên cây và số điện thoại, lát xuống live em chuyển ngay cho đội ngũ kỹ sư nông nghiệp gọi điện tư vấn phác đồ chuẩn cho bác.'*"),
        
        ("Xử lý bình luận công kích, phá rối (Troll / Chê bai vô căn cứ)",
         "👉 **Phản xạ chuẩn:** Giữ thái độ hòa nhã, tuyệt đối không đôi co tranh cãi: *'Dạ bên em cảm ơn ý kiến đóng góp của bác. Em xin phép chia sẻ tiếp kỹ thuật quản lý rầy nâu cho các bác khác đang chuẩn bị xịt đợt này.'* Sau đó trợ lý âm thầm tắt tiếng hoặc chặn tài khoản đó."),
        
        ("Tránh quét vi phạm chính sách & từ khóa cấm của TikTok",
         "👉 **Phản xạ chuẩn:** CẤM NÓI các từ tuyệt đối như: 'cam kết 100%', 'trị dứt điểm vĩnh viễn', 'thuốc độc nhất vô nhị', 'chữa bách bệnh'. Thay bằng: *'Hỗ trợ quản lý sâu bệnh hiệu quả'*, *'Hạn chế lây lan dịch hại'*, *'Giúp cây phục hồi nhanh chóng'*."),
        
        ("Kỹ thuật Demo cầm sản phẩm trực quan trước camera",
         "👉 **Phản xạ chuẩn:** Cầm sản phẩm ngang tầm ngực, ngón tay không che nhãn mác. Xoay nhẹ tem chống giả và mã vạch về phía camera. Hướng dẫn chi tiết cách dùng nắp đong ml để bà con thấy sự tiện lợi, không lo bị đong thừa thiếu thuốc."),
        
        ("Khách hỏi 'Thuốc này có pha chung với phân bón lá được không?'",
         "👉 **Phản xạ chuẩn:** Trả lời chuẩn theo kỹ thuật: *'Dạ dòng thuốc dạng SC/EC sinh học này phối hợp rất tốt với phân bón lá Hạt Vàng Năng Suất để vừa trừ sâu vừa dưỡng cây. Tuy nhiên bà con lưu ý không phối chung với các gốc thuốc có tính kiềm mạnh để giữ hiệu lực cao nhất.'*"),
        
        ("Giữ chân người xem khi mắt xem có dấu hiệu giảm dần",
         "👉 **Phản xạ chuẩn:** Tạo sự tò mò (Open Loop): *'Bác nào đang có mặt trên live để lại cho em dấu chấm hoặc bình luận tên giống lúa nhà mình, 3 phút nữa em sẽ chia sẻ mẹo xịt thuốc không lo rụng hoa, tỷ lệ đậu trái tăng vọt!'*"),
        
        ("Kêu gọi hành động (CTA) dứt khoát chuyển đổi đơn hàng",
         "👉 **Phản xạ chuẩn:** Kêu gọi theo hành động đơn giản: *'Bác nào lúa đang chuẩn bị làm đòng bấm ngay vào nút mua góc trái màn hình, chọn combo 2 chai để được hỗ trợ giao hàng tận nhà và tặng kèm tài liệu kỹ thuật mùa vụ!'*"),
        
        ("Khách hàng comment 'Tôi mua đợt trước xịt không thấy giảm sâu'",
         "👉 **Phản xạ chuẩn:** Tìm hiểu kỹ thuật phun để hỗ trợ: *'Dạ bác xịt lúc sáng sớm hay trưa nắng và pha bao nhiêu lít nước ạ? Sâu gối lứa hoặc phun không trúng ổ rầy dưới gốc lúa thì thuốc khó tiếp xúc. Bác để lại thông tin, kỹ sư bên em sẽ gọi hướng dẫn bác chỉnh lại góc phun chuẩn ngay.'*"),
        
        ("Xử lý sự cố kỹ thuật bất ngờ (Rớt mạng, mic rè, đổ đạo cụ)",
         "👉 **Phản xạ chuẩn:** Điềm tĩnh mỉm cười: *'Dạ đường truyền bên em vừa chớp một xíu do thời tiết ngoài đồng ruộng. Em đã quay trở lại rồi đây bà con ơi, em tiếp tục hướng dẫn công thức pha cho bình 25 lít nhé.'*"),
        
        ("Khách hàng hỏi xin bớt giá hoặc miễn phí ship",
         "👉 **Phản xạ chuẩn:** *'Dạ giá niêm yết trên live là giá chính thức từ nhà máy Hai Lúa Vàng. Nhưng khi bà con lấy từ 1 combo 2 chai trở lên hôm nay, công ty đã hỗ trợ toàn bộ chi phí giao hàng tận nhà cho bà con rồi ạ.'*")
    ]
    
    for title, content in situations:
        with st.expander(f"📌 {title}"):
            st.markdown(content)

# ----------------- 4. BÀI SÁT HẠCH STREAMER -----------------
elif menu == "🧠 Bài Sát Hạch 10 Câu Hỏi Streamer":
    st.markdown("<div class='main-header'>🧠 BÀI SÁT HẠCH KỸ NĂNG STREAMER (10 CÂU HỎI)</div>", unsafe_allow_html=True)
    st.info("Nhập họ tên và hoàn thành 10 câu hỏi. Mỗi câu đúng 10 điểm. Đạt từ **80/100 điểm** sẽ được công nhận hoàn thành.")

    trainee_name = st.text_input("Nhập Họ và Tên nhân viên làm bài:", placeholder="Ví dụ: Nguyễn Văn A")

    with st.form("exam_10_questions"):
        ans = []
        
        st.markdown("##### Câu 1: Nhiệm vụ quan trọng nhất trong 3–5 giây đầu tiên của phiên Livestream là gì?")
        q1 = st.radio("Chọn câu trả lời:", [
            "A. Chào hỏi từng người vào xem và mở nhạc thật to",
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
            if not trainee_name.strip():
                st.warning("⚠️ Vui lòng nhập Họ và Tên trước khi nộp bài!")
            else:
                correct_count = sum(ans)
                final_score = correct_count * 10
                new_status = "Đạt" if final_score >= 80 else "Chưa đạt"
                
                with get_db() as conn:
                    conn.execute("INSERT INTO exam_results (trainee_name, score, status) VALUES (?, ?, ?)", 
                                 (trainee_name.strip(), final_score, new_status))
                    conn.commit()

                st.divider()
                if final_score >= 80:
                    st.success(f"🎉 CHÚC MỪNG {trainee_name.upper()}! BẠN ĐÃ ĐẠT {final_score}/100 ĐIỂM ({correct_count}/10 câu đúng).")
                    st.balloons()
                else:
                    st.error(f"⚠️ KẾT QUẢ: {final_score}/100 ĐIỂM ({correct_count}/10 câu đúng). Chưa đạt tiêu chuẩn 80 điểm. Hãy ôn tập lại cẩm nang và làm lại bài.")

# ----------------- 5. BẢNG ĐIỂM & QUẢN LÝ ĐÀO TẠO -----------------
elif menu == "📊 Bảng Điểm & Quản Lý Đào Tạo":
    st.markdown("<div class='main-header'>📊 LỊCH SỬ KẾT QUẢ SÁT HẠCH ĐỘI NGŨ</div>", unsafe_allow_html=True)
    with get_db() as conn:
        df = pd.read_sql_query("SELECT id as STT, trainee_name as 'Họ và Tên', score as 'Điểm Số', status as 'Trạng Thái', created_at as 'Thời Gian' FROM exam_results ORDER BY id DESC", conn)
    
    if df.empty:
        st.info("Chưa có nhân viên nào hoàn thành bài sát hạch.")
    else:
        st.dataframe(df, use_container_width=True)
