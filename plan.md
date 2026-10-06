# Plan thực hiện lab (theo GUIDE.md)

> Ghi chú cấu hình: dùng Gemini qua LangChain `init_chat_model` (không set đủ 3 biến `AZURE_OPENAI_*`):
> `.env`: `LAB_MODEL=google_genai:gemini-3.5-flash-lite`, `GOOGLE_API_KEY=<key>` (đã test `make_model().invoke(...)` → trả "OK").
>
> **Môi trường thực thi: chuyển sang WSL (Ubuntu)** vì backend shell của Deep Agents giả định `/bin/sh` (lệnh `which`, `cat`...),
> không chạy đúng trên Windows native (2 test `test_02_agent.py` fail vì thiếu lệnh Unix). Từ Phần 1 trở đi, mọi `pytest`/`python -m lab...`
> chạy trong WSL, repo tại `/mnt/d/day20/K4-L3L4-Track3-Day20-AdvanceMultiAgents`, venv riêng `.venv-wsl` (khác venv Windows ban đầu).
> Đã cài `python3.14-venv` qua `sudo apt install` (được phép) và `pip install -e .` trong venv WSL (hoàn tất).
>
> **Đổi model**: `gemini-3.5-flash-lite` có RPD gần cạn (425/500, RPM 33/15 vượt giới hạn) → đổi sang
> `LAB_MODEL=google_genai:gemini-3.1-flash-lite` (RPM 15, RPD 500) để đủ ngân sách cho Phần 2 trở đi. Đã test lại kết nối, OK.
> Đây là model đang dùng cho mọi lần chạy thật từ Phần 1 (`data-learn`) trở đi, trừ lần test kết nối đầu tiên dùng `gemini-3.5-flash-lite`.
>
> **Bug đã sửa (Phần 3)**: Gemini trả `AIMessage.content` dạng list-of-blocks thay vì string → `curator.py` và `runner.py`
> (`final_message`) bị hỏng khi dùng `str(content)` trực tiếp. Đã thêm chuẩn hoá `_content_to_text`/tương đương ở cả hai nơi.

## Phần 0. Cài đặt và làm quen

- [X] [run] Tạo venv, `pip install -e .`
- [X] [code] Cài thêm `langchain-google-genai`, sửa `.env` dùng `LAB_MODEL=google_genai:gemini-...` + `GOOGLE_API_KEY`
- [X] [run] `cp .env.example .env` rồi điền biến Gemini, `mkdir -p report && cp REPORT_TEMPLATE.md report/REPORT.md`
- [X] [run] `pytest tests/test_01_provided.py` → kỳ vọng `12 passed`
- [X] [run] Kiểm tra kết nối model: `python -c "from lab.model import make_model; print(make_model().invoke('Reply with OK').content)"`
- [X] [run] `python scripts/tour.py` (không tốn token)
- [X] [report] Điền mục 3 của `report/REPORT.md`: công cụ mặc định, mô tả subagent `general-purpose`, trích câu từ mô tả `task` và `execute`

## Phần 1. Hoàn thiện harness với Deep Agents

- [X] [code] Cài `src/lab/subagents.py` theo `guides/pseudocode/02_subagents.md` (3 subagent: explorer, implementer, reviewer)
- [X] [run] `pytest tests/test_02_agent.py -k subagents` (pass sau khi `build_agent` được cài)
- [X] [code] Cài `src/lab/agent.py` (`make_backend`, `build_agent`) theo `01_agent.md`
- [X] [run] `pytest tests/test_02_agent.py` (toàn bộ) — 9/9 pass trong WSL (venv `.venv-wsl`)
- [X] [code] Cài `src/lab/runner.py` (`run_task`) theo `03_runner.md`
- [X] [run] `pytest tests/test_03_runner.py` — 6/6 pass trong WSL
- [X] [run] Chạy thật: `python -m lab.runner --condition baseline --tasks data-learn` → `score=5/8 tokens=304251 calls=27 82.8s`
- [X] [fix bug] Kiểm tra `results/baseline/data-learn/run.json` và `trace.md` — hợp lệ, đủ khóa theo spec

## Phần 2. Chạy tác vụ học, đo đạc, phân loại lỗi

- [X] [run] `python -m lab.runner --condition baseline --tasks code-learn logs-learn` → code-learn score=6/10 tokens=149600 calls=24 141.6s; logs-learn score=6/9 tokens=56026 calls=8 48.0s
- [X] [run] `python -m lab.runner --condition subagents --tasks learn` → code-learn: GraphRecursionError (hết 60 bước, score 0/10, lỗi hợp lệ); data-learn: score=3/8 tokens=185948 calls=4 subagent_calls=1; logs-learn: score=0/9 tokens=236723 calls=6 (JSONDecodeError do tác tử ghi JSON sai định dạng — chạy lại lần đầu bị crash do 429/transient, lần 2 thành công)
- [X] [report] Phân loại lỗi (nhóm A-G) vào mục 4 báo cáo — 9/10 check thất bại thuộc nhóm E, 1 thuộc nhóm A, có bằng chứng trích `detail`
- [X] [run] `python scripts/check_breakdown.py` → baseline/learn: kỹ thuật 17/18 đạt, quy ước 0/9 đạt (bằng chứng phủ định cho nhóm A-D)
- [X] [report] Điền mục 5 báo cáo: `subagent_calls`, subagent_type thực tế được gọi (general-purpose/implementer), so sánh token với baseline, ghi chú sự cố chạy trùng tiến trình logs-learn

## Phần 3. Self-evolving: curator tự viết skill

- [X] [code] Cài `curate_skills` trong `src/lab/curator.py` theo `04_curator.md` và `05_skill_quality.md`
- [X] [run] `pytest tests/test_04_curator.py` — 2/2 pass trong WSL
- [X] [run] `python -m lab.curator` → 3 skill: `pre-submission-audit`, `rigorous-testing-protocol`, `data-normalization-checklist`
- [X] [fix bug] Phát hiện & sửa bug: Gemini trả `AIMessage.content` dạng list-of-blocks (không phải str như OpenAI) →
      `parse_skill_blocks(str(reply))` không khớp regex (0 skill ghi được lần đầu). Sửa `curator.py` (chuẩn hoá content → text)
      và `runner.py` (`_content_to_text` cho `final_message`, trước đó bị stringify sai dạng `"[{'type': 'text', ...}]"`).
      29/29 test offline vẫn pass sau fix.
- [X] [report] Đánh giá từng skill sinh ra (mục 6) — đã điền bảng trong `report/REPORT.md`: cả 3 skill đều tổng quát, khớp lỗi quan sát, không rò rỉ
- [X] [fix bug] Không cần xóa/chạy lại curator — cả 3 skill đạt chất lượng, không có skill kém/có hại
- [X] [run] `python -m lab.runner --condition skills-auto --tasks learn` → code-learn: skills_read=0 (GraphRecursionError lại xảy ra, không đếm được); data-learn: skills_read=2 score=5/8; logs-learn: skills_read=0 score=6/9
- [X] [run] Sao lưu `cp -r results/skills-auto results/skills-auto-dev` (giữ số liệu Phần 3.4 trước khi Phần 4 ghi đè)
- [X] [report] Đối chiếu `skills_read` và `trace.md` — đã viết trong mục 6 báo cáo: `data-learn` đọc đúng 2 skill liên quan trước khi ghi `clean.csv`; `logs-learn`/`code-learn` không đọc skill nào (nêu nguyên nhân khả dĩ)

## Phần 4. Giả thuyết, đóng băng, đo trên tác vụ đánh giá

- [ ] [report] Viết giả thuyết H1-H3 vào mục 2 báo cáo (trước khi thấy điểm eval)
- [ ] [run] `git add -A && git commit -m "hypotheses"`
- [ ] [run] `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
- [ ] [run] `python -m lab.runner --condition baseline --tasks eval`
- [ ] [run] `python -m lab.runner --condition subagents --tasks eval`
- [ ] [run] (trước khi ghi đè) sao lưu `mv results/skills-auto results/skills-auto-dev`
- [ ] [run] `python -m lab.runner --condition skills-auto --tasks all`
- [ ] [run] `python scripts/verify_freeze.py` → kỳ vọng `OK`
- [ ] [fix bug] Nếu một lần chạy lỗi: chạy lại lần đó, ghi chú trong báo cáo
- [ ] [run] `python -m lab.compare > report/table.md`
- [ ] [run] `python scripts/check_breakdown.py` (dữ liệu cho mục 4, 7, 8 báo cáo)

## Phần 5. Báo cáo

- [ ] [report] Hoàn thiện `report/REPORT.md` mục 1–7 (bản nháp trong buổi học)
- [ ] [report] Dán bảng `report/table.md` vào mục 7
- [ ] [report] Trả lời đủ 6 câu phân tích ở mục 8 (có số liệu)
- [ ] [report] Hoàn thiện mục 9 (≥3 hạn chế) và mục 10 (kết luận, tối đa 5 câu)

## Phần 6. Thử thách mở rộng (tùy chọn, +5 điểm)

- [ ] [code] Chọn 1 hướng (6a-6e) và triển khai
- [ ] [run] Chạy thí nghiệm, ghi kết quả vào thư mục `results/` riêng
- [ ] [report] Viết phụ lục: hướng chọn, kết quả, nhận xét, hạn chế, đề xuất tiếp theo

## Nộp bài

- [ ] [report] Kiểm tra đủ: `src/lab/*.py` (4 tệp), `skills/auto/`, `results/` (run.json + trace.md), `report/REPORT.md`, `report/table.md`
- [ ] [fix bug] Không commit `.env`, không để lộ API key trong code/vết/báo cáo
