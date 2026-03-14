# To-Do List API

API quản lý danh sách công việc xây dựng bằng FastAPI.

## Cấp 0 - Hello To-Do (Hoàn thành)

### Yêu cầu
- Tạo project FastAPI
- Endpoint GET /health → { "status": "ok" }
- Endpoint GET / → message chào
- Chạy uvicorn và gọi được 2 endpoint

### Hướng dẫn chạy

1. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Chạy server:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Kiểm tra endpoints:**
   - GET http://localhost:8000/health
   - GET http://localhost:8000/
   - Interactive docs: http://localhost:8000/docs

## Các cấp độ tiếp theo
- Cấp 1: CRUD cơ bản (RAM)
- Cấp 2: Validation + Filter/Sort/Pagination
- Cấp 3: Tách tầng (Router/Service/Repository)
- Cấp 4: Database (SQLite/PostgreSQL)
- Cấp 5: Authentication + User
- Cấp 6: Nâng cao (Tag, Deadline)
- Cấp 7: Testing + Deploy
- Cấp 8: Soft Delete
