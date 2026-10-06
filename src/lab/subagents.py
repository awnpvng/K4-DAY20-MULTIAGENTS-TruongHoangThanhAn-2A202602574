"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Dùng khi cần đọc README, docstring, dữ liệu mẫu hoặc cấu trúc thư mục của tác vụ "
                "trước khi sửa gì. Gọi subagent này đầu tiên để thu thập sự thật về đề bài và dữ liệu, "
                "sau đó dùng báo cáo của nó để quyết định cách làm."
            ),
            "system_prompt": (
                "Bạn là explorer: chỉ đọc và báo cáo, không sửa hay tạo tệp nào. "
                "Đọc kỹ instruction.md, docstring liên quan và vài dòng mẫu của dữ liệu đầu vào. "
                "Trả về báo cáo ngắn, chính xác: các quy ước định dạng, giá trị đặc biệt hoặc bất thường "
                "trong dữ liệu, và bất kỳ ràng buộc nào nêu trong đề bài. Không suy đoán khi chưa đọc tệp."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Dùng khi đã biết rõ việc cần làm (ví dụ sau khi explorer đã báo cáo) và cần thực hiện "
                "thay đổi cụ thể: sửa mã nguồn, ghi tệp kết quả, hoặc chạy script/test. Giao việc phải "
                "nêu đủ quy tắc và định dạng đầu ra cần tuân theo."
            ),
            "system_prompt": (
                "Bạn là implementer: thực hiện đúng các thay đổi được giao, dùng công cụ tệp và shell. "
                "Sau khi sửa, chạy lại test hoặc lệnh kiểm tra liên quan nếu có. "
                "Trả về báo cáo ngắn: những gì đã thay đổi, kết quả chạy test/lệnh, và có gì chưa chắc chắn."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Dùng sau khi implementer đã hoàn thành một thay đổi, để kiểm tra độc lập kết quả so với "
                "đề bài và các trường hợp biên trước khi coi là xong. Không dùng cho việc chưa có gì để kiểm tra."
            ),
            "system_prompt": (
                "Bạn là reviewer: chỉ kiểm tra, không sửa tệp. Đối chiếu kết quả hiện có với yêu cầu của đề bài, "
                "kiểm tra trường hợp biên (giá trị thiếu, định dạng không đồng nhất, trùng lặp) và chạy lại "
                "test/lệnh kiểm tra nếu có thể. Trả về báo cáo ngắn: đạt hay chưa đạt, và lý do cụ thể cho mỗi điểm chưa đạt."
            ),
        },
    ]
