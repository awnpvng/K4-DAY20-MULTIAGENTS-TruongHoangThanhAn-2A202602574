---
name: rigorous-testing-protocol
description: DÙNG KHI viết mã nguồn để đảm bảo tính đúng đắn và tuân thủ các tiêu chuẩn lập trình.
---
- Luôn thêm các bài kiểm tra hồi quy (regression tests) cho mỗi lỗi đã sửa để tránh lỗi tái diễn.
- Kiểm tra tệp `tests/` hiện có: không được sửa đổi mã nguồn gốc trong đó, chỉ được thêm tệp kiểm thử mới.
- Áp dụng type hints cho tất cả các tham số và giá trị trả về của mọi hàm công khai.
- Chạy toàn bộ bộ kiểm thử sau mỗi lần thay đổi mã nguồn để đảm bảo không làm hỏng các chức năng cũ.
- Sử dụng các trường hợp kiểm thử biên (edge cases) như dữ liệu trống, định dạng sai, hoặc giá trị cực hạn.