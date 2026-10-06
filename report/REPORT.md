# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: `LAB_MODEL=google_genai:gemini-3.5-flash-lite`, `LAB_TEMPERATURE=0`, `recursion_limit` mặc định của runner.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21; Windows 11 (chạy trực tiếp, không Docker).
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): **Dự đoán `subagents` KHÔNG vượt `baseline`** trên tác vụ đánh giá, điểm có thể thấp hơn hoặc ngang bằng, với chi phí token biến thiên mạnh (có thể cao hơn nhiều). Căn cứ: ở tác vụ học, `subagents` không giải quyết được nhóm lỗi E (9/10 check thất bại ở baseline) vì bản thân tác tử chính không biết các quy tắc tổ chức để truyền xuống subagent — giao việc không thể bù đắp cho việc "không biết luật". Quan sát thực tế: `data-learn` giảm token (304k→186k) nhưng `logs-learn` tăng gấp ~13 lần (56k→746k, do tác tử vừa giao việc vừa tự làm lại) và `code-learn` không hoàn thành (`GraphRecursionError`). Tác tử chính cũng ưu tiên subagent mặc định `general-purpose` thay vì 3 subagent tự định nghĩa, cho thấy việc điều phối chưa ổn định — rủi ro lặp lại ở tác vụ đánh giá.
- H2 (skills-auto so với baseline): **Dự đoán cải thiện nhẹ hoặc không đáng kể**, khó tổng quát hóa đều cho cả 3 họ tác vụ. Căn cứ: `05_skill_quality.md`/`04_curator.md` trích dẫn SkillsBench (skill người viết tăng ~16 điểm %, skill tự sinh trung bình KHÔNG có lợi) và SkillEvolBench (lợi ích trên tác vụ học thường không chuyển sang tác vụ mới — overfitting). Dữ liệu học của nhóm cũng cho thấy phân hóa rõ: `data-learn` đọc 2/3 skill và có khả năng cải thiện nhất (do `data-normalization-checklist` khớp đúng loại lỗi D); `logs-learn` và `code-learn` có `skills_read=0` ở lần chạy Phần 3.4, nên nhiều khả năng skill không được dùng trên `logs-eval`/`code-eval`. Riêng với quy ước **mới** của tác vụ đánh giá (chưa từng xuất hiện trong `detail` mà curator thấy), skill khó có tác dụng vì không được huấn luyện trên dữ liệu đó — dự đoán không cải thiện các check `rule_` mới.
- H3 (tác vụ học so với tác vụ đánh giá): **Dự đoán điểm tác vụ đánh giá thấp hơn tác vụ học ở mọi điều kiện**, đặc biệt ở các check `rule_` (nhóm E). Căn cứ: tác vụ đánh giá thêm một quy ước tổ chức mới mà tác tử chưa từng thấy; vì nhóm lỗi E chiếm 90% thất bại ở tác vụ học do tác tử không chủ động dò tìm "RULE" ẩn, hành vi này nhiều khả năng lặp lại với quy ước mới của tác vụ đánh giá, bất kể điều kiện nào. Các check kỹ thuật (A-D) được dự đoán vẫn đạt tỉ lệ cao tương tự tác vụ học (17/18 ở baseline) vì bản chất xử lý dữ liệu/mã nguồn tương tự, chỉ khác dữ liệu đầu vào.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), shell (`execute`) và subagent (`task`). Công cụ `execute` là công cụ cho phép chạy lệnh (shell), chạy trong sandbox cách ly, trả về stdout/stderr gộp và exit code.
2. Mô tả của `task` nói subagent `general-purpose` là tác tử đa năng cho các câu hỏi phức tạp, tìm kiếm tệp/nội dung, và thực hiện tác vụ nhiều bước; dùng khi không chắc sẽ tìm đúng kết quả trong vài lần thử đầu. Theo mô tả, mỗi lần gọi là stateless theo mặc định: subagent chỉ nhìn thấy prompt được truyền vào và trả về một báo cáo cuối cùng duy nhất — nó không thấy toàn bộ ngữ cảnh hội thoại của tác tử chính trừ khi loại subagent đó được khai báo là "kế thừa" hội thoại.
3. Từ mô tả `task`: "Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report." Từ mô tả `execute`: "You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | `tests_not_modified` | A (bỏ qua đặc tả) | Đề bài (`instruction.md`) ghi "Do not modify the existing files in `tests/`"; `detail`: "the original files in tests/ must not be modified (new test files are allowed)". Vết cho thấy tác tử chỉnh sửa `tests/test_extra.py` nhiều lần nhưng check vẫn thất bại — tác tử không tuân thủ ràng buộc nêu rõ trong đề. |
| code-learn | `rule_type_hints` | E (vi phạm quy ước tổ chức) | `detail`: "RULE: every public function ... has type annotations on all parameters and on the return value." — quy ước không có trong docstring/đề bài gốc. |
| code-learn | `rule_regression_tests` | E | `detail`: "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3)". |
| code-learn | `rule_changelog` | E | `detail`: "RULE: record each fix in CHANGELOG.md under '## Unreleased' ...". |
| data-learn | `rule_money_in_cents` | E | `detail`: "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)". |
| data-learn | `rule_meta_block` | E | `detail`: "RULE: answer.json has an object `meta` = {...}". |
| data-learn | `rule_clean_csv` | E | `detail`: "RULE: write workspace/clean.csv with header order_id,timestamp_utc,region,amount_cents ...". |
| logs-learn | `rule_service_names` | E | `detail`: "RULE: service names ... lower-case with '-' replaced by '_' ...". |
| logs-learn | `rule_sorted_errors` | E | `detail`: "RULE: `errors` sorted by service, then by timestamp_utc, ascending". |
| logs-learn | `rule_schema_header` | E | `detail`: "RULE: top-level object has schema_version=2 and generated_by=log-triage". |

Nhận xét: **9/10 check thất bại (90%) thuộc nhóm E** (vi phạm quy ước tổ chức Acme không có trong đề bài/docstring gốc) — các check này đều có tên bắt đầu `rule_` và `detail` bắt đầu bằng "RULE:". Chỉ 1 check (`tests_not_modified` ở `code-learn`) thuộc nhóm A (bỏ qua ràng buộc nêu rõ trong đề).

**Bằng chứng phủ định cho nhóm A-D:** `python scripts/check_breakdown.py` cho baseline/learn: **17/18 check kỹ thuật đạt** (chỉ 1 check kỹ thuật thất bại — chính là `tests_not_modified` ở trên), trong khi **0/9 check quy ước (`rule_`) đạt**. Điều này cho thấy mô hình xử lý đúng gần như toàn bộ phần kỹ thuật (phân tích dữ liệu bẩn, sửa lỗi gốc, định dạng) nhưng hệ thống bỏ qua quy ước tổ chức không nêu trong đề — đúng như kỳ vọng của GUIDE.md với mô hình đủ mạnh.

Một skill tổng quát (ví dụ `pre-submission-audit` do curator sinh — xem mục 6) có thể phòng ngừa nhóm E vì nó hướng dẫn tác tử chủ động tìm và đối chiếu các "RULE" trước khi nộp bài.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): `explorer` (chỉ đọc README/docstring/dữ liệu mẫu, báo cáo sự thật, không sửa gì — tránh tác tử chính bỏ qua đặc tả, nhóm lỗi A); `implementer` (thực hiện thay đổi cụ thể, chạy test/script); `reviewer` (kiểm tra độc lập kết quả so với đề bài và trường hợp biên, không sửa — phòng nhóm lỗi B "không kiểm chứng"). Ba vai trò tách biệt đọc/làm/kiểm để giảm rủi ro tác tử vừa làm vừa tự chấm.

- `subagent_calls` ở từng tác vụ và nhận xét:

| Tác vụ | `subagent_calls` | `subagent_type` được gọi | Nhận xét |
|---|---|---|---|
| code-learn | 0 | — | Không giao việc; tác tử tự làm trực tiếp và cuối cùng rơi vào `GraphRecursionError` (hết 60 bước) — không có bằng chứng cho thấy việc không giao việc là nguyên nhân, nhưng việc chia nhỏ qua subagent có thể đã giúp tránh lặp vô hạn (chưa kiểm chứng được vì lỗi khiến `messages` rỗng). |
| data-learn | 1 | `general-purpose` (subagent **mặc định** của Deep Agents, không phải `explorer`/`implementer`/`reviewer` tự định nghĩa) | Tác tử chính chọn subagent mặc định thay vì 3 subagent tự định nghĩa dù `SUBAGENTS_NOTE` khuyến khích dùng "subagent chuyên biệt". Lời giao việc đầy đủ quy tắc làm sạch dữ liệu và công thức tính, có yêu cầu trả về JSON cuối — subagent trả báo cáo rõ ràng, tác tử chính dùng lại kết quả. |
| logs-learn | 1 | `implementer` (subagent tự định nghĩa) | Lời giao việc liệt kê đủ các quy tắc parse log (level, timestamp UTC, exception, repeat_count...). Tuy nhiên "Tool result" ngay sau lệnh `task` trống trong vết — subagent dường như không trả báo cáo hữu ích, và tác tử chính sau đó **tự viết lại** `parse_logs.py` thay vì dựa vào kết quả subagent, cho thấy khâu kiểm tra báo cáo subagent trước khi dùng (RUBRIC 3.3) không hiệu quả ở đây: tác tử chính không tin/không dùng được báo cáo nên làm lại từ đầu, gây lãng phí lượt gọi. |

- Thông tin thiếu hoặc thừa khi giao việc: lời giao việc ở cả hai lần gọi đều đủ quy tắc **kỹ thuật** (công thức, định dạng trường) nhưng không có quy tắc **tổ chức** (`rule_*`), vì tác tử chính chưa biết các quy tắc này tồn tại (chúng chỉ lộ ra qua `detail` của check thất bại — không có trong `instruction.md`). Điều này khớp với phát hiện ở mục 4: phần lớn thất bại thuộc nhóm E, và việc giao việc cho subagent không giúp gì cho nhóm lỗi này vì bản thân tác tử chính cũng không biết quy tắc để truyền xuống.

- Ảnh hưởng đến token và thời gian: so với `baseline` cùng tác vụ — `data-learn`: baseline 304.251 token → subagents 185.948 token (giảm ~39%, vì phần việc chính được ủy nhiệm gọn trong 1 lời gọi subagent thay vì nhiều vòng tự thử-sai). `logs-learn`: baseline 56.026 → subagents 746.084 token (tăng **~13 lần**) và 1089.9 giây — tác tử chính vừa giao việc cho `implementer` vừa tự làm lại toàn bộ, nhân đôi chi phí; đây là ví dụ cụ thể cho nhận định trong `02_subagents.md` rằng đa tác tử có thể tốn nhiều token hơn đáng kể so với một tác tử đơn khi điều phối không hiệu quả. `code-learn`: baseline 149.600 token (hoàn thành, không lỗi) → subagents 161.132 token nhưng **không hoàn thành** (hết `recursion_limit`) — tốn gần tương đương baseline nhưng cho kết quả kém hơn nhiều (0 so với 6/10 check đạt).

> Ghi chú tái lập: lần chạy `subagents/logs-learn` đầu tiên có hiện tượng tiến trình chạy rất lâu khiến nhóm tưởng đã crash và chạy lại một lần song song; tiến trình gốc sau đó hoàn tất và ghi đè kết quả (số liệu trên là của tiến trình đã hoàn tất, 1089.9s). Đây là rủi ro thao tác (chạy trùng tiến trình), không phải lỗi của `run_task`; nhóm ghi lại để tránh lặp lại khi tái chạy.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: 1 lần chạy (`python -m lab.curator`), không xóa skill nào. (Lần chạy đầu tiên trả về 0 skill do một lỗi tương thích provider trong `curate_skills`/`run_task` — xem mục "Ghi chú kỹ thuật" bên dưới — đã sửa code rồi chạy lại, không liên quan đến chất lượng nội dung skill.)

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `pre-submission-audit` | Tổng quát: nói về đọc RULE trong đề, đối chiếu schema đầu ra, không nêu tên tác vụ hay tệp riêng (trừ `CHANGELOG.md` — đây là quy ước Acme chung, được phép theo `05_skill_quality.md`). | Có vẻ đúng: khớp với nhóm lỗi E (vi phạm quy ước tổ chức) quan sát được ở Phần 2.2. Không có hướng dẫn sai rõ ràng. | 6 dòng, `description` bắt đầu "DÙNG KHI chuẩn bị hoàn tất tác vụ" — khá rộng. `skills_read`: điền sau khi chạy 3.4. |
| `rigorous-testing-protocol` | Tổng quát: nói về thêm test hồi quy, không sửa `tests/` gốc, dùng type hints, chạy lại test. Không nêu tên hàm/tệp cụ thể. | Phần lớn đúng, nhưng "áp dụng type hints cho tất cả hàm công khai" là một khuyến nghị phong cách không chắc liên quan trực tiếp đến check thất bại nào quan sát được — có thể không giúp ích, cần đối chiếu `trace.md` để xác nhận. | 5 dòng, `description` "DÙNG KHI viết mã nguồn" — rộng. |
| `data-normalization-checklist` | Tổng quát: chuẩn hóa ngày UTC, chuẩn hóa chuỗi phân loại, xử lý trùng lặp, tiền tệ theo cents, giá trị thiếu — đúng loại lỗi nhóm D (bỏ sót dữ liệu bẩn) đã quan sát ở `data-learn`/`logs-learn`. | Khớp với `detail` quan sát được (múi giờ, định dạng tiền tệ, trùng lặp). | 5 dòng, `description` "DÙNG KHI xử lý dữ liệu thô" — rộng, phù hợp cho cả `data` và `logs`. `skills_read` (Phần 3.4): `data-learn`=2 (đọc `data-normalization-checklist` và `pre-submission-audit`, theo `trace.md`); `logs-learn`=0; `code-learn`=0 (GraphRecursionError → `messages` rỗng, không đếm được dù có thể đã đọc trước khi hết giới hạn bước — hạn chế đã biết của `run_task` tối giản, mục 8 của `03_runner.md`). |

Giải thích dùng skill (mục 4.4 RUBRIC): `data-learn` đọc đủ 2/3 skill và `trace.md` cho thấy tác tử gọi `read_file` các SKILL.md này trước khi ghi `clean.csv`, phù hợp với mô tả "DÙNG KHI xử lý dữ liệu thô". `logs-learn` không đọc skill nào dù `description` của `data-normalization-checklist` ("xử lý dữ liệu thô") đủ rộng để áp dụng cho log — có thể do tác tử không nhận diện log là "dữ liệu thô" theo nghĩa mô tả, hoặc ưu tiên đọc `instruction.md` trước và tự tin xử lý mà không tra skill. `code-learn` không có skill nào nhắm đúng loại lỗi của nó (hai skill còn lại thiên về kiểm thử/chuẩn hóa dữ liệu, không giải quyết nguyên nhân khiến tác tử lặp vô hạn).

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
