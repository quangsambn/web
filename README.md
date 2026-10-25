# Sổ kết quả Priority

Ứng dụng web một trang để chuyên viên khách hàng Priority nhập kết quả hằng ngày và xem thống kê tuần/tháng.

- **Nhập ngày**: điền KH mới, HĐ KKH/CKH, thu nợ, thẻ mới, BHNT, PNT, TK số đẹp, TTQT/MBNT, phí DV khác, công việc khác. Tự tạo tin nhắn đúng mẫu để sao chép gửi Zalo. Có thể dán tin nhắn cũ để điền tự động.
- **Thống kê**: tổng theo tuần (T2–CN) hoặc tháng, biểu đồ theo ngày, bảng chi tiết, tiến độ chỉ tiêu tháng, tin nhắn tổng hợp, xuất CSV.
- **Lịch sử**: sửa/xóa các ngày đã nhập.
- **Cài đặt**: họ tên, chỉ tiêu tháng, sao lưu/khôi phục.

Mở `index.html` bằng trình duyệt (hoặc bật GitHub Pages). Dữ liệu lưu trong trình duyệt của máy đó; nên sao lưu định kỳ.

## Agent "Báo Cáo Hàng Ngày SamDQ"

- **Trong app Claude (Skill):** nén thư mục `skills/bao-cao-hang-ngay-samdq` thành file .zip rồi tải lên Claude → Settings → Capabilities → Skills. Sau đó chỉ cần nhắn kết quả trong ngày, Claude trả tin nhắn đúng mẫu; dán nhiều tin nhắn ngày để tổng hợp tuần/tháng.
- **Trong Claude Code:** agent `.claude/agents/bao-cao-hang-ngay-samdq.md` soạn tin nhắn, lưu vào `data/bao-cao.json` (cùng định dạng file sao lưu của ứng dụng web) và thống kê bằng `skills/bao-cao-hang-ngay-samdq/scripts/tong_hop.py`.
