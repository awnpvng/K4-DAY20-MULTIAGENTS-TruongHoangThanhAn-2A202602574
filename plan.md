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

- [X] [report] Viết giả thuyết H1-H3 vào mục 2 báo cáo (trước khi thấy điểm eval)
- [X] [run] `git add -A && git commit -m "hypotheses"` → commit `252ae9c`
- [X] [run] `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze` → commit `f5b8480`
- [X] [run] `python -m lab.runner --condition baseline --tasks eval` → code-eval 6/11 tokens=90896; data-eval 5/9 tokens=185664 (GraphRecursionError); logs-eval 6/10 tokens=44060
- [X] [run] `python -m lab.runner --condition subagents --tasks eval --recursion-limit 40` (hạ limit để tiết kiệm RPD) → code-eval 6/11 tokens=140859 (GraphRecursionError ngay cả với limit 40); data-eval 5/9 tokens=213357; logs-eval 6/10 tokens=98929
- [X] [run] Đã sao lưu `results/skills-auto-dev` trước đó ở Phần 3.4
- [X] [run] `python -m lab.runner --condition skills-auto --tasks all --recursion-limit 40` → code-eval 4/11 (GraphRecursionError@40); code-learn 5/10 (GraphRecursionError@40); data-eval 5/9 (GraphRecursionError@40); data-learn 5/8 tokens=108670; logs-eval 6/10 tokens=49256; logs-learn 6/9 tokens=61331

### ✅ ĐÃ TIẾP TỤC (2026-10-06, ~14:xx) — đổi API key mới, chạy lại thành công 4 ô bị nhiễu

Key cũ hết RPD; key thay thế đầu tiên (`<redacted>`) bị lỗi **403 PERMISSION_DENIED ở cấp project** (thử cả `gemini-3.1-flash-lite` và `gemini-3.8-flash` đều lỗi, `gemini-2.5-flash` thì 404 model deprecated — không phải do tên model). Đổi sang key thứ 2, test OK, chạy lại 4 ô với `--recursion-limit 40`:
- `subagents/code-eval`: score=6/11 tokens=164395 (GraphRecursionError@40, dữ liệu sạch)
- `skills-auto/code-eval`: score=6/11 tokens=105494 (GraphRecursionError@40)
- `skills-auto/code-learn`: score=0/10 tokens=98767 (GraphRecursionError@40)
- `skills-auto/data-eval`: score=5/9 tokens=187157 (GraphRecursionError@40)

Đủ dữ liệu 6 tác vụ × 3 điều kiện (18 run.json hợp lệ). Tiếp tục `verify_freeze.py` → `compare` → `check_breakdown.py`.

### ⏸️ TẠM DỪNG (2026-10-06, ~13:40) — RPD cạn, chờ reset ~17h (ước tính lại được sau ~06:00 2026-10-07) — ĐÃ GIẢI QUYẾT bằng key mới, xem ghi chú trên

**Sự cố:** 3/6 tác vụ `skills-auto --tasks all` bị `GraphRecursionError` ở `--recursion-limit 40` (trong khi `baseline` dùng limit mặc định 60) → gây nhiễu (confound) khi so sánh điều kiện. Quyết định chạy lại 4 ô sau với limit=60 để đồng nhất:
`subagents/code-eval`, `skills-auto/code-eval`, `skills-auto/code-learn`, `skills-auto/data-eval`.

**Hậu quả:** Lần chạy lại làm **cạn hoàn toàn RPD** của `gemini-3.1-flash-lite` (500/500) giữa chừng — lệnh đầu tiên (`subagents/code-eval`) dính 429 giữa lúc chạy (ghi đè kết quả `GraphRecursionError` sạch trước đó bằng kết quả nhiễu `score=5/11, error=429`); 3 lệnh sau (`skills-auto` 3 tác vụ) bị 429 ngay lập tức (`score=0, tokens=0`), **ghi đè mất luôn 3 kết quả `GraphRecursionError@40` hợp lệ trước đó** (không khôi phục được vì `run_task` luôn xóa sandbox).

**Trạng thái hiện tại của 4 ô bị ảnh hưởng (KHÔNG dùng được cho báo cáo):**
- `results/subagents/code-eval/run.json`: score=5/11, `error=GoogleRateLimitError 429` (nhiễu, không phải GraphRecursionError thật)
- `results/skills-auto/code-eval/run.json`: score=0/11, tokens=0, `error=429`
- `results/skills-auto/code-learn/run.json`: score=0/10, tokens=0, `error=429`
- `results/skills-auto/data-eval/run.json`: score=0/9, tokens=0, `error=429`

**Việc cần làm khi tiếp tục (ngày mai, sau khi RPD reset):**
1. Chạy lại đúng 4 lệnh trên — **dùng `--recursion-limit 40`** (đồng nhất với các ô khác của `subagents`/`skills-auto`, KHÔNG cố khớp với baseline=60 nữa, để tránh tốn thêm request và tái lặp sự cố):
   `python -m lab.runner --condition subagents --tasks code-eval --recursion-limit 40`
   `python -m lab.runner --condition skills-auto --tasks code-eval code-learn data-eval --recursion-limit 40`
2. Ghi vào báo cáo (mục 9 - hạn chế): có sự khác biệt `recursion_limit` giữa `baseline` (60, mặc định) và `subagents`/`skills-auto` (40, giảm để tiết kiệm RPD) — đây là một nguồn nhiễu thật, không chỉ là giả thuyết, cần nêu rõ khi so sánh tỉ lệ `GraphRecursionError` giữa các điều kiện.
3. Sau khi có đủ 4 ô, tiếp tục: `python scripts/verify_freeze.py` → `python -m lab.compare > report/table.md` → `python scripts/check_breakdown.py`.

- [X] [fix bug] Chạy lại 4 ô bị nhiễu bởi 429 với `--recursion-limit 40` (xem ghi chú "ĐÃ TIẾP TỤC" trên) — xong
- [X] [fix bug] `verify_freeze.py` báo FAIL lần đầu ("skills/ differs from freeze tag") do `skills/auto/README.md` bị git tự đổi LF→CRLF khi commit WIP trước đó (không phải tôi sửa nội dung) → `git checkout freeze -- skills/auto/README.md` để khôi phục đúng byte đã freeze
- [X] [run] `python scripts/verify_freeze.py` → **OK** (checked 6 runs of skill conditions)
- [X] [run] `python -m lab.compare > report/table.md` → bảng đủ 3 cột, 6 hàng tác vụ + hàng tổng hợp
- [X] [run] `python scripts/check_breakdown.py` → baseline/eval 17/18 kỹ thuật, 0/12 quy ước; subagents/learn 8/18 kỹ thuật (giảm mạnh do GraphRecursionError ở code-learn); skills-auto/learn 11/18, đọc skill 1/3

## Phần 5. Báo cáo

- [X] [report] Hoàn thiện `report/REPORT.md` mục 1–7 — mục 1 cập nhật model/limit/WSL/số lần chạy/commit freeze thật
- [X] [report] Dán bảng `report/table.md` + `check_breakdown.py` vào mục 7, kèm bảng giải thích 6 lần chạy có `error`
- [X] [report] Trả lời đủ 6 câu phân tích ở mục 8 (có số liệu: subagents/skills-auto không cải thiện eval so baseline, skill không giúp check rule_, token efficiency skills-auto tốt nhất, không rò rỉ nhưng có overfitting, nhiễu thấp trừ code-* do đổi recursion_limit)
- [X] [report] Hoàn thiện mục 9 (5 hạn chế) và mục 10 (kết luận 5 câu + đề xuất cải tiến) + Phụ lục (lệnh đã chạy, ghi chú môi trường WSL)
- [ ] [report] Mục 1: điền tên/mã sinh viên (cần thông tin từ người dùng — chưa có)

## Phần 6. Thử thách mở rộng (tùy chọn, +5 điểm)

- [ ] [code] Chọn 1 hướng (6a-6e) và triển khai
- [ ] [run] Chạy thí nghiệm, ghi kết quả vào thư mục `results/` riêng
- [ ] [report] Viết phụ lục: hướng chọn, kết quả, nhận xét, hạn chế, đề xuất tiếp theo

## Nộp bài

- [ ] [report] Kiểm tra đủ: `src/lab/*.py` (4 tệp), `skills/auto/`, `results/` (run.json + trace.md), `report/REPORT.md`, `report/table.md`
- [ ] [fix bug] Không commit `.env`, không để lộ API key trong code/vết/báo cáo
