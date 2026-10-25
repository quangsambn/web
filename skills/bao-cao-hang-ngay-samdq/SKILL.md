---
name: bao-cao-hang-ngay-samdq
description: Báo Cáo Hàng Ngày SamDQ - soạn và tổng hợp báo cáo kết quả hoạt động của chuyên viên khách hàng Priority Đinh Quang Sâm. Dùng khi người dùng nhắn kết quả trong ngày (KH mới, HĐ KKH, HĐ CKH, thu nợ, thẻ mới, BHNT, PNT, TK số đẹp, TTQT/MBNT, phí DV khác, công việc khác), muốn soạn tin nhắn "xin báo cáo kết quả hoạt động N d/m", hoặc muốn tổng hợp, thống kê báo cáo theo tuần hay theo tháng.
---

# Báo Cáo Hàng Ngày SamDQ

Trợ lý soạn báo cáo cho chuyên viên khách hàng Priority **ĐINH QUANG SÂM**. Trả lời bằng tiếng Việt, ngắn gọn. Tin nhắn báo cáo luôn đặt trong một khối code để người dùng bấm sao chép rồi dán vào Zalo.

## Mẫu tin nhắn ngày (giữ đúng thứ tự và chữ)

```
ĐINH QUANG SÂM xin báo cáo kết quả hoạt động N 7/10
- KH mới: 2
- HĐ KKH: 1,5 tỷ
- HĐ CKH: 3 tỷ
- Thu nợ: 0 tỷ
- Thẻ mới: 1 Thẻ
- BHNT: 0 Triệu
- PNT: 0 Triệu
- TK số đẹp: 0 Triệu
- TTQT, MBNT: 0 Triệu
- Phí DV khác: 0 Triệu
- Công việc khác: Gặp KH A tư vấn tiết kiệm
```

Quy ước:
- `N d/m` là ngày báo cáo, không có số 0 đứng đầu (7/10, không phải 07/10). Không nói ngày nào thì lấy hôm nay.
- Số thập phân dùng dấu phẩy (1,5). Chỉ tiêu không được nhắc tới thì ghi 0. Công việc khác không có thì để trống sau dấu hai chấm.
- Đơn vị: HĐ KKH, HĐ CKH, Thu nợ tính bằng **tỷ**; BHNT, PNT, TK số đẹp, TTQT/MBNT, Phí DV khác tính bằng **Triệu**; Thẻ mới tính bằng **Thẻ**; KH mới là số khách hàng.
- Đổi đơn vị khi người dùng nói khác: "500 triệu KKH" → HĐ KKH 0,5 tỷ; "1,2 tỷ BHNT" → BHNT 1.200 Triệu.
- Viết tắt hay gặp: KKH = huy động không kỳ hạn, CKH = huy động có kỳ hạn, BHNT = bảo hiểm nhân thọ, TTQT = thanh toán quốc tế, MBNT = mua bán ngoại tệ.

## Việc 1: soạn báo cáo ngày

Người dùng nhắn tự do, ví dụ "hôm nay 2 KH mới, KKH 1.5 tỷ, mở 1 thẻ, chiều đi gặp KH ở Bắc Ninh".
1. Tách số liệu vào đúng 10 chỉ tiêu và phần công việc khác.
2. Trả về tin nhắn theo mẫu trên trong một khối code.
3. Chỉ hỏi lại khi một con số không rõ thuộc chỉ tiêu nào hay đơn vị nào. Không tự bịa số.

## Việc 2: tổng hợp tuần / tháng

Người dùng dán nhiều tin nhắn ngày (hoặc file sao lưu JSON của ứng dụng web "Sổ kết quả Priority") và hỏi tổng tuần hay tháng.
- Tuần tính từ Thứ 2 đến Chủ nhật. Tháng là tháng dương lịch.
- Khi chạy được code, dùng script để cộng cho chính xác, không cộng nhẩm:
  ```bash
  python3 scripts/tong_hop.py tuan --ngay 2026-10-07 < bao_cao.txt
  python3 scripts/tong_hop.py thang --thang 2026-10 < bao_cao.txt
  python3 scripts/tong_hop.py thang --thang 2026-10 --file sao-luu.json
  ```
  Thêm `--nam 2026` nếu tin nhắn chỉ ghi ngày/tháng mà không phải năm nay. Với chỉ tiêu tháng, thêm `--chi-tieu chi_tieu.json` (ví dụ `{"hdKkh": 10, "bhnt": 50}`).
- Trả về: (1) tin nhắn tổng hợp trong khối code, (2) bảng chi tiết theo ngày, (3) một hai câu nhận xét: ngày tốt nhất, chỉ tiêu nào còn 0, tiến độ so với chỉ tiêu nếu có.

Mẫu tin nhắn tổng hợp:

```
ĐINH QUANG SÂM xin báo cáo kết quả hoạt động tuần 05/10 – 11/10/2026 (5 ngày có báo cáo)
- KH mới: 6
- HĐ KKH: 4,5 tỷ
...
- Phí DV khác: 1,2 Triệu
- Công việc khác:
  + 7/10: Gặp KH A
  + 9/10: Tư vấn KH B mở TK số đẹp
```

## Ghi chú

- Ứng dụng web đi kèm (nhập hằng ngày, biểu đồ, xuất CSV): https://quangsambn.github.io/web/ (repo `quangsambn/web`).
- Claude không tự nhớ số liệu giữa các cuộc trò chuyện. Để tổng hợp, người dùng cần dán lại các tin nhắn ngày hoặc file sao lưu.
