# v23 FastChat

Tối ưu chatbot:
- General question không truy vấn MySQL/BM25.
- Book search dùng catalog cache 15 giây.
- Policy search chỉ chạy policy BM25.
- Top-K giới hạn 3 để prompt ngắn.
- Chỉ giữ 3 lượt hội thoại gần nhất khi gọi Gemini.
- Câu hỏi lặp lại có response cache 40 mục.
- Search/policy trả lời local, không chờ mạng.

Tuỳ chọn `.env`:
```env
AI_BOOK_CACHE_SECONDS=15
```
Giảm xuống 5 nếu cần sách mới xuất hiện trong chatbot nhanh hơn; tăng lên 30 nếu ưu tiên tốc độ.
