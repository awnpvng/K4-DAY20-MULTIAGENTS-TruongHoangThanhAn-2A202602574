---
name: data-normalization-checklist
description: DÙNG KHI xử lý dữ liệu thô để đảm bảo tính nhất quán trước khi phân tích hoặc xuất tệp.
---
- Chuẩn hóa tất cả các định dạng ngày tháng về UTC (ISO-8601).
- Chuẩn hóa các giá trị phân loại (ví dụ: tên vùng, trạng thái) về dạng chính tắc (canonical spelling) bằng cách loại bỏ khoảng trắng và đồng nhất chữ hoa/thường.
- Xử lý dữ liệu trùng lặp dựa trên khóa duy nhất (unique ID) trước khi thực hiện tính toán.
- Chuyển đổi các giá trị tiền tệ sang đơn vị nhỏ nhất (ví dụ: cents) dưới dạng số nguyên để tránh sai số dấu phẩy động.
- Kiểm tra và xử lý các giá trị thiếu (missing values) hoặc dữ liệu không hợp lệ theo quy tắc nghiệp vụ.