# SmartLibrary v21 - Loan/Return/Fine UI

Bản v21 làm lại trang Quản lý Mượn / Trả / Phạt: giao diện rõ ràng, tiếng Việt, hành động trực tiếp, sửa logic Không trả/Mất theo ngưỡng cấu hình và bỏ bảng raw khó đọc.

# SmartLibrary AI / LIBRA - Full Admin v5

Bản này đã dựng lại cả **sảnh ngoài** và toàn bộ khu vực **sau đăng nhập** theo phong cách SmartLibrary AI sáng, tím-hồng, sidebar quản trị như ảnh mẫu.

## Sảnh ngoài

- Header: Trang chủ / Kho sách / Giới thiệu / Liên hệ / Đăng nhập Admin.
- Hero sáng, giới thiệu SmartLibrary AI.
- Thống kê lấy trực tiếp từ SQLite.
- Khám phá theo thể loại.
- Sách được quan tâm.
- Trang Kho sách công khai.
- Trang Giới thiệu và Liên hệ.
- Trang đăng nhập kiểu SmartLibrary AI, có nút điền nhanh tài khoản demo.

## Trang quản trị / thủ thư

1. Tổng quan & Thống kê
2. Tra cứu & Quản lý Sách
3. Quản lý Độc giả
4. Quản lý Mượn / Trả / Phạt
5. Đặt trước Sách
6. Tài khoản & Phân quyền (Admin)
7. Trợ lý AI & Gợi ý Sách
8. Báo cáo & Xuất dữ liệu
9. Cài đặt

## Trang độc giả

- Trang chủ
- Kho sách
- Sách của tôi
- Đặt trước
- Thông báo
- Trợ lý AI & Gợi ý
- Hồ sơ

## Tài khoản demo

```text
Admin
admin / admin123

Thủ thư
thuthu / thuthu123

Độc giả
docgia / reader123
```

## Chạy lần đầu

Trong VS Code Terminal, đứng đúng thư mục có `app.py` và `requirements.txt`:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Hoặc chạy `CAI_DAT_LAN_DAU.bat`, sau đó `CHAY_WEB.bat`.

## Gemini API

Mở `.env`:

```text
GEMINI_API_KEY=KEY_CUA_BAN
GEMINI_MODEL=gemini-3.5-flash-lite
```

Không đăng `.env` chứa API key thật lên GitHub.

## Database

SQLite nằm trong:

```text
library.db
```

Bản demo đã có sẵn 85 đầu sách, dữ liệu độc giả, mượn trả, đặt trước và một khoản phạt để các dashboard có nội dung minh họa.


## Sảnh ngoài v5
- Thanh gradient LIBRA và menu ngang giống mẫu tím-hồng.
- Banner tự chuyển Tin học / Trinh thám / Triết lý.
- Tìm sách, Đăng ký, Đăng nhập đều bấm được.
- Chatbot nổi góc phải, bấm mở AI công khai.
- Giữ nguyên 9 trang quản trị sau đăng nhập.


## V7 - Trang chủ sau đăng nhập và sửa hình ảnh

- Sau khi Admin/Thủ thư đăng nhập, hệ thống vào **Trang chủ quản trị** trước.
- Trang chủ có Truy cập nhanh, chỉ số chính, biểu đồ hoạt động, việc cần chú ý, hoạt động gần đây và sách nổi bật.
- Sau đó người dùng mới đi vào 9 trang chức năng từ sidebar.
- Sửa card sách: không còn khoảng trắng lớn phía trên ảnh.
- Ưu tiên bìa sách thật được lấy từ các ảnh người dùng đã cung cấp.
- Chatbot nổi ngoài sảnh thu nhỏ còn khoảng 52px và dùng bong bóng trắng như ảnh tham khảo.


## V8 - Cổng hội viên độc giả kiểu Waka

Sau khi đăng nhập bằng vai trò Độc giả, hệ thống có giao diện tối riêng với sidebar và các trang:
- Trang chủ Hội viên
- Quản lý tài khoản
- Tủ sách cá nhân
- Quản lý đơn hàng (yêu cầu mượn/trả/đặt trước)
- Thành tích
- Lịch sử giao dịch
- Hỗ trợ khách hàng
- Trợ lý AI & Gợi ý

Admin/Thủ thư vẫn giữ nguyên dashboard quản trị màu sáng của bản v7.


## V10
- Chatbot sảnh mở popup tối ngay trên trang hiện tại.
- Trang đăng nhập thu nhỏ.
- Khu độc giả đổi hoàn toàn sang theme sáng.
- Sidebar Admin/Thủ thư đậm và rõ hơn.


## V11 - BM25 + RAG tự chọn + xử lý không trả sách

- Giới hạn số lượng mượn theo cấu hình chung hoặc theo từng độc giả.
- Kiểm tra hạn mức cả lúc gửi yêu cầu và lúc duyệt.
- Quá hạn tự tính phạt, chặn mượn mới và tự khóa quyền mượn sau số ngày cấu hình.
- Admin có thể đánh dấu sách `Chưa trả / Mất`; hệ thống cộng phí thay thế và giữ tài khoản khóa đến khi xử lý nghĩa vụ.
- Tìm kiếm sách dùng BM25 thuần Python, không cần cài thêm package.
- AI dùng RAG tự chọn: `BOOK`, `POLICY`, `GENERAL`.
- Có màn hình giải thích kỹ thuật hệ thống và debug route RAG.

### Kiến trúc
`UI Streamlit -> Database SQLite -> BM25 Retrieval -> Auto RAG Router -> Gemini (nếu cần)`


## V12 - Tối ưu tốc độ và độ mượt

Đã tối ưu theo cách chạy của Streamlit:

- Bootstrap database chỉ chạy một lần thay vì lặp lại sau mỗi click.
- Quét sách quá hạn được giới hạn tối đa một lần/30 giây.
- SQLite dùng WAL + index cho các truy vấn mượn/trả/độc giả.
- Ảnh được phục vụ qua `static/` để trình duyệt cache, không nhúng base64 lại ở mỗi rerun.
- 3 banner lớn đã nén từ khoảng 6.0 MB xuống khoảng 0.6 MB.
- Ảnh sách dùng lazy loading.
- Kho sách chỉ render 10 cuốn mỗi trang thay vì toàn bộ 85 cuốn.
- Chatbot nhỏ 44px ở góc phải.
- Chatbot dùng dialog nhỏ và tương tác bên trong chỉ rerun dialog, không tải lại toàn bộ trang.
- Gemini client được tái sử dụng trong session.

Cách chạy nhanh nhất:

```text
Nhấp đúp CHAY_NHANH.bat
```


## V13 - MySQL bắt buộc
Bản này mặc định dùng MySQL qua `mysql-connector-python`.

Sửa `.env`:
```
DB_ENGINE=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=MAT_KHAU_MYSQL
MYSQL_DATABASE=smartlibrary
```

Kiểm tra: `KIEM_TRA_MYSQL.bat`.
Chạy web: `CHAY_NHANH.bat`.
Trong trang Cài đặt của Admin có khối trạng thái để thấy MySQL đang kết nối.
Nếu muốn chuyển dữ liệu cũ từ `library.db`, chạy `python CHUYEN_SQLITE_SANG_MYSQL.py`.


## V14 Fast AI
- Sửa lỗi `math is not defined`.
- Chatbot tím, nhỏ và ghim góc phải kiểu popup.
- Tra cứu sách/chính sách trả lời cục bộ trước để giảm độ trễ Gemini.
- BM25 mở rộng từ khóa: “sách về tình yêu” ưu tiên đúng thể loại Tình cảm.
- Trang AI chỉ gọi Gemini khi cần phân tích hoặc kiến thức tổng quát.
- Trang quản lý sách/độc giả/mượn-trả-phạt/tài khoản có thống kê và bố cục rõ ràng hơn.
- Dữ liệu demo quản trị tự tạo một lần nếu bảng mượn đang trống (`DEMO_DATA=true`).
- Phần kỹ thuật hiển thị đúng MySQL thay vì SQLite.

# V14 uses MySQL by default. No library.db is bundled.

## V15 - Sidebar cố định giống mẫu

- Phần logo + hồ sơ + nút Trang chủ cố định phía trên.
- Chỉ danh sách chức năng ở giữa được cuộn.
- Giao diện Sáng + Đăng xuất cố định phía dưới, không mất khi cuộn.
- Nút đang chọn dùng gradient tím-hồng, chữ đậm và icon rõ hơn.
- Cài đặt được đặt trong vùng menu giữa để đáy sidebar chỉ giữ các nút hệ thống cần luôn nhìn thấy.


## V16 - Chat AI + sửa tra cứu

- Chatbot chỉ mở khi bấm nút chatbot/AI; đóng xong các thao tác khác không tự mở lại.
- Popup được ép về góc phải dưới theo kiểu trợ lý Waka.
- Hiển thị rõ trạng thái Gemini AI + RAG MySQL.
- Truy xuất RAG chỉ thực hiện một lần cho mỗi câu hỏi.
- Tra cứu công khai có tổng quan, form tìm kiếm, BM25 và phân trang 8 sách.
- Khi đang tìm kiếm, thứ tự BM25 được giữ nguyên; không còn bị sort ABC/ảnh ghi đè kết quả.
- BM25 đã loại lỗi expansion token gây khớp sai và áp dụng ngưỡng liên quan động.
- Trang Tra cứu & Quản lý Sách của Admin có thẻ kết quả trực quan, bảng dữ liệu thu gọn trong expander.

## V17 - Giao diện Tra cứu & Quản lý Sách theo mẫu

- Header riêng: tìm nhanh, Tạo Phiếu mượn, Đăng xuất.
- Tổng quan kho dạng 4 KPI nhỏ.
- Bộ lọc tên/tác giả/mã sách, thể loại và trạng thái tồn kho.
- Chuyển đổi Grid/List.
- Grid 4 thẻ sách mỗi hàng, bố cục gần mẫu tham chiếu.
- Nút AI Tóm tắt, Mượn sách, Sửa, Xóa ngay trên từng thẻ.
- Thêm/Sửa/Xóa/Mượn dùng dialog để không kéo dài trang.
- Giữ MySQL, BM25, Gemini/RAG và sidebar cố định từ V16.


## V18 - Quản lý độc giả + bỏ khoảng trắng đầu trang

- Bỏ thanh app_header chung gây khoảng trắng/nhân đôi header.
- Trang Quản lý Độc giả dựng lại giống mẫu: header, tìm kiếm, trạng thái, cấp thẻ, bảng độc giả và thao tác.
- Nút Sửa/Khóa/Mở khóa/Chi tiết hoạt động trực tiếp.
- Cấp độc giả mới bằng dialog, tự tạo tài khoản + thẻ thư viện.
- Giữ MySQL, Gemini/RAG và toàn bộ chức năng v17.

## V19 - Sidebar theo ảnh tham chiếu
- Logo và hồ sơ cố định trên cùng.
- Trang chủ + các chức năng quản lý + AI + Báo cáo nằm trong vùng cuộn giữa.
- Giao diện Sáng và Đăng xuất luôn cố định dưới cùng.
- Mục quản lý đang chọn: nền xanh-tím đậm.
- Trợ lý AI đang chọn: nền tím nhạt, chữ tím như ảnh mẫu.
- Bỏ dòng ghi chú SmartLibrary AI • MySQL dưới sidebar để giống mẫu hơn.
- Không đưa Cài đặt thành một nút riêng trong danh sách giữa, giữ sidebar gọn như ảnh tham chiếu.

## Bản v22 - Sidebar giống ảnh tham chiếu

- Sidebar rộng 355px, nền trắng.
- Logo SmartLibrary + badge AI cố định phía trên.
- Thẻ Quản trị viên cố định phía trên, không hiện username phụ.
- Vùng menu giữa cuộn riêng với thanh cuộn mảnh bên phải.
- Mục quản lý đang chọn dùng nền xanh tím.
- Mục Trợ lý AI đang chọn dùng nền tím nhạt đúng mẫu.
- Hai nút `Giao diện Sáng` và `Đăng xuất` cố định ở đáy sidebar.
- Dùng Material icons để icon đồng nhất, không bị emoji nhiều màu.

### Chạy

1. Copy file `.env` đang chạy tốt từ bản trước vào folder v22.
2. Chạy:

```powershell
python -m streamlit run app.py
```
