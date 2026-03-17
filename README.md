# To-Do List API

API quản lý danh sách công việc xây dựng bằng FastAPI.

## Cấp 0 - Hello To-Do (Hoàn thành ✅)

### Yêu cầu
- Tạo project FastAPI
- Endpoint GET /health → { "status": "ok" }
- Endpoint GET / → message chào
- Chạy uvicorn và gọi được 2 endpoint

**Status:** ✅ Hoàn thành

---

## Cấp 1 - CRUD cơ bản (dữ liệu trong RAM) (Hoàn thành ✅)

### Yêu cầu
- Model ToDo với: id (int), title (str), is_done (bool)
- Endpoints CRUD đầy đủ
- Validate dữ liệu bằng Pydantic
- Trả lỗi 404 khi không tìm thấy

### Model ToDo
```python
{
  "id": 1,
  "title": "Learn FastAPI",
  "is_done": false
}
```

### Endpoints
| Method | Path | Mô tả |
|--------|------|-------|
| POST | /todos | Tạo todo mới |
| GET | /todos | Lấy danh sách tất cả |
| GET | /todos/{id} | Lấy chi tiết một todo |
| PUT | /todos/{id} | Cập nhật toàn bộ todo |
| DELETE | /todos/{id} | Xóa một todo |

### Ví dụ sử dụng

**Tạo todo:**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "is_done": false}'
```

**Lấy danh sách:**
```bash
curl http://localhost:8000/todos
```

**Lấy chi tiết:**
```bash
curl http://localhost:8000/todos/1
```

**Cập nhật:**
```bash
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done": true}'
```

**Xóa:**
```bash
curl -X DELETE http://localhost:8000/todos/1
```

**Status:** ✅ Hoàn thành

## Cấp 2 - Validation "xịn" + filter/sort/pagination (Hoàn thành ✅)

### Yêu cầu
- title độ dài 3–100 (nâng từ 1 lên 3)
- GET /todos hỗ trợ filter, search, sort, pagination
- Response cấu trúc: { "items": [...], "total": 123, "limit": 10, "offset": 0 }

### Cải tiến bổ sung
- Thêm `created_at` và `updated_at` tự động trong mỗi todo
- `updated_at` tự cập nhật khi todo thay đổi

### Query Parameters

```
GET /todos
  ?is_done=true              # Lọc theo trạng thái (true/false)
  &q=keyword                 # Tìm kiếm theo title (không phân biệt chữ hoa/thường)
  &sort=created_at           # Sắp xếp (mặc định: created_at)
  &sort=-created_at          # Sắp xếp giảm dần (prefix: -)
  &limit=10                  # Số items mỗi trang (mặc định: 10, tối đa: 100)
  &offset=0                  # Bỏ qua số items (mặc định: 0)
```

### Ví dụ sử dụng

**Tạo todo (validation min_length: 3):**
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "is_done": false}'
```

**Lấy danh sách với filter:**
```bash
# Lọc todos đã hoàn thành
curl "http://localhost:8000/todos?is_done=true"

# Tìm kiếm theo keyword
curl "http://localhost:8000/todos?q=FastAPI"

# Sắp xếp giảm dần theo ngày tạo
curl "http://localhost:8000/todos?sort=-created_at"

# Pagination
curl "http://localhost:8000/todos?limit=5&offset=10"

# Kết hợp nhiều filters
curl "http://localhost:8000/todos?is_done=false&q=FastAPI&sort=-created_at&limit=10&offset=0"
```

**Response ví dụ:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Learn FastAPI",
      "is_done": false,
      "created_at": "2026-03-14T10:30:00",
      "updated_at": "2026-03-14T10:30:00"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0
}
```

**Status:** ✅ Hoàn thành

---

## Cấp 4 - Database (SQLite) + ORM (SQLAlchemy) (Hoàn thành ✅)

### Yêu cầu
- Dùng SQLAlchemy ORM
- Bảng todos: id, title, description, is_done, created_at, updated_at
- Migrations bằng Alembic (optional)
- PATCH endpoint cập nhật một phần
- POST /todos/{id}/complete endpoint
- created_at/updated_at tự cập nhật
- Pagination từ database thực sự

### Cấu trúc Database Layer

```
app/db/
├── __init__.py
├── database.py          # SQLAlchemy engine, session factory
└── models.py           # ORM models (ToDo)
```

### SQLAlchemy Model

```python
# app/db/models.py
class ToDo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)    # ✨ New field
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
```

### New Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| PATCH | /api/v1/todos/{id} | Cập nhật một phần (chỉ fields được gửi) |
| POST | /api/v1/todos/{id}/complete | Đánh dấu hoàn thành |

### Database Features

✅ **Automatic Timestamps**
- `created_at`: Tự đặt khi tạo, không thay đổi
- `updated_at`: Tự cập nhật mỗi khi todo thay đổi

✅ **Real Database Pagination**
- Pagination từ DB, không in-memory
- SQL `OFFSET` và `LIMIT`
- Quicker for large datasets

**Status:** ✅ Hoàn thành

---

## Cấp 5 - User Authentication & Authorization (Hoàn thành ✅)

### Yêu cầu
- User model: email (unique), password (hashed), is_active
- JWT token authentication (Bearer token)
- Password hashing with bcrypt
- Endpoints: register, login, /me
- User isolation: User A không thể xem/sửa/xóa todos của User B
- HTTPBearer security scheme

### User Model Database

```python
# app/db/models.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    todos = relationship("ToDo", back_populates="owner")
```

### Todo-User Relationship

```python
# app/db/models.py
class ToDo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # ✨ NEW: User-Todo relationship
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="todos")
```

### Authentication Architecture

```
Security Layer (app/core/security.py)
├── hash_password(password) → bcrypt hash
├── verify_password(plain, hashed) → bool
├── create_access_token(data) → JWT string (30 min expiry)
└── decode_access_token(token) → dict or None

Repository Layer (app/repositories/)
├── user.py: UserRepository
│   ├── create(email, password)
│   ├── get_by_email(email)
│   ├── get_by_id(user_id)
│   └── authenticate(email, password)
└── database.py: ToDoRepository (owner-aware)
    ├── create(owner_id, todo_data)
    ├── get_by_id(todo_id, owner_id)
    ├── get_all(owner_id, filters...)
    ├── update(todo_id, owner_id, data)
    └── delete(todo_id, owner_id)

Service Layer (app/services/)
├── auth.py: AuthService
│   ├── register(UserRegister) → UserResponse
│   ├── login(UserLogin) → TokenResponse
│   └── get_current_user_by_id(user_id) → User
└── todo.py: ToDoService (owner-aware)
    ├── create_todo(owner_id, data)
    ├── get_todo(todo_id, owner_id)
    ├── list_todos(owner_id, filters...)
    └── ...

Router Layer (app/routers/)
├── auth.py: Authentication endpoints
│   ├── POST /auth/register
│   ├── POST /auth/login
│   └── GET /auth/me
└── todo.py: Todo endpoints with HTTPBearer
    └── All endpoints require JWT token + get_current_user dependency
```

### Authentication Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/auth/register | ❌ | Register new user |
| POST | /api/v1/auth/login | ❌ | Login & get JWT token |
| GET | /api/v1/auth/me | ✅ Bearer token | Get current user info |

### Todo Endpoints (All Require Authentication)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/v1/todos | ✅ Bearer token | Create todo for current user |
| GET | /api/v1/todos | ✅ Bearer token | List todos (only current user's) |
| GET | /api/v1/todos/{id} | ✅ Bearer token | Get todo (only if user owns it) |
| PUT | /api/v1/todos/{id} | ✅ Bearer token | Update todo (only if user owns it) |
| PATCH | /api/v1/todos/{id} | ✅ Bearer token | Partially update (only if owner) |
| POST | /api/v1/todos/{id}/complete | ✅ Bearer token | Mark done (only if owner) |
| DELETE | /api/v1/todos/{id} | ✅ Bearer token | Delete todo (only if owner) |

### User Schemas

```python
# Request
class UserRegister(BaseModel):
    email: str
    password: str  # 6-72 chars (bcrypt limit)

class UserLogin(BaseModel):
    email: str
    password: str

# Response
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CurrentUser(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime
```

### Usage Examples

**1. Register a new user**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "securepass123"
  }'

# Response
{
  "id": 1,
  "email": "user1@example.com",
  "is_active": true,
  "created_at": "2026-03-17T15:54:19.579759"
}
```

**2. Login to get JWT token**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user1@example.com",
    "password": "securepass123"
  }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzzz....",
  "token_type": "bearer"
}
```

**3. Get current user (requires token)**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "id": 1,
  "email": "user1@example.com",
  "is_active": true,
  "created_at": "2026-03-17T15:54:19.579759"
}
```

**4. Create a todo (requires token)**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."

curl -X POST http://localhost:8000/api/v1/todos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn JWT Authentication",
    "description": "Understand how JWT works"
  }'

# Response
{
  "id": 1,
  "title": "Learn JWT Authentication",
  "description": "Understand how JWT works",
  "is_done": false,
  "created_at": "2026-03-17T15:54:36.014565",
  "updated_at": "2026-03-17T15:54:36.014569"
}
```

**5. List todos (only user's todos, requires token)**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."

curl -X GET "http://localhost:8000/api/v1/todos?is_done=false&sort=-created_at" \
  -H "Authorization: Bearer $TOKEN"

# Response - only shows current user's todos
{
  "items": [
    {
      "id": 1,
      "title": "Learn JWT Authentication",
      "description": "Understand how JWT works",
      "is_done": false,
      "created_at": "2026-03-17T15:54:36.014565",
      "updated_at": "2026-03-17T15:54:36.014569"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### Security Features

✅ **Password Security**
- Bcrypt hashing (configured with 12 rounds)
- Password truncated to 72 bytes (bcrypt limit)
- Never store plain passwords

✅ **JWT Token Security**
- HS256 algorithm
- 30-minute expiration
- Token contains user ID (sub claim)
- Verified on every authenticated request

✅ **User Isolation**
- Repository layer enforces owner_id filtering
- User A cannot see, edit, or delete User B's todos
- GET /api/v1/todos/{id} returns 404 if not owner
- Database foreign key relationship enforces referential integrity

✅ **HTTPBearer Scheme**
- FastAPI built-in HTTPBearer security scheme
- Automatically extracts token from Authorization header
- Format: `Authorization: Bearer <token>`

### Project Structure

```
app/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py              # Pydantic settings
│   └── security.py            # Password & JWT utilities
├── db/
│   ├── __init__.py
│   ├── database.py            # Engine, session, get_db()
│   └── models.py              # User & ToDo ORM models
├── repositories/
│   ├── __init__.py
│   ├── user.py                # UserRepository (NEW)
│   └── database.py            # ToDoRepository (updated for owner_id)
├── services/
│   ├── __init__.py
│   ├── todo.py                # ToDoService (updated for owner_id)
│   └── auth.py                # AuthService (NEW)
├── routers/
│   ├── __init__.py
│   ├── todo.py                # Todo endpoints (updated with auth)
│   └── auth.py                # Auth endpoints (NEW)
└── schemas/
    ├── __init__.py
    ├── todo.py                # Todo models
    └── user.py                # User models (NEW)

main.py                         # FastAPI app + auth router
requirements.txt                # Dependencies + auth packages
todos.db                        # SQLite database (auto-created)
```

### Dependencies Added

```
passlib[bcrypt]==1.7.4         # Password hashing
python-jose[cryptography]==3.3.0  # JWT token handling
python-multipart==0.0.6        # Form data parsing (for HTTPBearer)
```

**Status:** ✅ Hoàn thành

### Testing Summary

✅ User 1 registers successfully
✅ User 1 logs in and gets JWT token
✅ User 1 creates todo (id=1)
✅ User 2 registers and logs in
✅ User 2 lists todos (empty - isolation working!)
✅ User 2 creates todo (id=2)
✅ User 1 lists todos (only sees id=1 - isolation confirmed!)
✅ /me endpoint returns correct user info
✅ All authenticated endpoints require valid Bearer token


✅ **Full-Text Search**
- Tìm kiếm trong title và description
- Case-insensitive search

✅ **Column Indexing**
- `title`, `is_done`, `created_at` có index
- Tốc độ query nhanh hơn

### Database File

```
SQLite database: todos.db (SQLite, không cần setup)
Location: d:\todolist\todos.db
Size: ~24 KB
```

### Repository Pattern (Database)

```python
# app/repositories/database.py
ToDoRepository(db: Session):
  - create(title, description, is_done)
  - get_by_id(id)
  - get_all(filter, search, sort, pagination)
  - update(id, fields)
  - delete(id)
```

Tất cả database queries qua Repository.

### Dependency Injection

```python
# app/routers/todo.py
@router.post("")
def create_todo(todo: ToDoCreate, db: Session = Depends(get_db)):
    service = ToDoService(db)
    return service.create_todo(todo)
```

Mỗi endpoint nhận `db` session từ dependency injection.

### Ví dụ sử dụng

**Tạo todo với description:**
```bash
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn SQLAlchemy",
    "description": "ORM with SQLite",
    "is_done": false
  }'
```

**Cập nhật một phần (PATCH):**
```bash
# Chỉ cập nhật is_done, giữ lại title và description
curl -X PATCH http://localhost:8000/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done": true}'
```

**Đánh dấu hoàn thành:**
```bash
curl -X POST http://localhost:8000/api/v1/todos/1/complete
```

**Tìm kiếm trong title và description:**
```bash
curl "http://localhost:8000/api/v1/todos?q=SQLAlchemy"
```

**Database Pagination:**
```bash
# Real DB pagination, không in-memory
curl "http://localhost:8000/api/v1/todos?limit=10&offset=20"
```

### Cấu trúc tổng thể từ Cấp 0-4

```
app/
├── db/                          # ✨ NEW: Database layer
│   ├── __init__.py
│   ├── database.py             # SQLAlchemy session factory
│   └── models.py               # ORM models
├── repositories/
│   ├── todo.py                 # In-memory (for testing)
│   ├── database.py             # ✨ NEW: Database repo
│   └── __init__.py
├── services/
│   ├── todo.py                 # ✨ Updated with description, PATCH, complete
│   └── __init__.py
├── routers/
│   ├── todo.py                 # ✨ PATCH + /complete endpoints
│   └── __init__.py
├── schemas/
│   ├── todo.py                 # ✨ ToDoPartialUpdate added
│   └── __init__.py
└── core/
    ├── config.py
    └── __init__.py

main.py                         # ✨ Base.metadata.create_all()
todos.db                        # ✨ SQLite database file
.env
requirements.txt                # ✨ +sqlalchemy, +alembic
```

### Migration (Alembic) - Optional

Setup Alembic:
```bash
alembic init alembic
# Edit alembic/env.py để tự động detect models
# Edit alembic/script.py.mako để auto generate migration
alembic revision --autogenerate -m "Add todos table"
alembic upgrade head
```

Tuy nhiên vì ta dùng `Base.metadata.create_all()` nên migrations optional.

**Status:** ✅ Hoàn thành

---

### Yêu cầu
- Tách thư mục: routers/, schemas/, services/, repositories/, core/
- Dùng APIRouter với prefix /api/v1
- Config bằng pydantic-settings (từ .env)
- Không viết logic DB trong router
- Có file main.py sạch

### Cấu trúc Project (Clean Architecture)

```
d:\todolist\
├── app/                       # Main package
│   ├── __init__.py
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py
│   │   └── todo.py
│   ├── repositories/         # Data access layer
│   │   ├── __init__.py
│   │   └── todo.py          # In-memory data store
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   └── todo.py          # Service logic
│   ├── routers/              # FastAPI endpoints
│   │   ├── __init__.py
│   │   └── todo.py          # API routes
│   └── core/                 # Core configuration
│       ├── __init__.py
│       └── config.py         # Pydantic settings
├── main.py                   # Clean app entry point
├── .env                      # Environment variables (local)
├── .env.example             # Example env file
├── requirements.txt
├── .gitignore
└── README.md
```

### Tầng Architecture

| Tầng | File | Trách nhiệm |
|------|------|-----------|
| **Schemas** | `app/schemas/todo.py` | Define Pydantic models, validate data |
| **Repository** | `app/repositories/todo.py` | Data access (in-memory), CRUD operations |
| **Service** | `app/services/todo.py` | Business logic, filtering, sorting, pagination |
| **Router** | `app/routers/todo.py` | FastAPI endpoints, receive request → call service → return response |
| **Core** | `app/core/config.py` | Settings from .env, app configuration |

### Cấu hình (.env)

```dotenv
APP_NAME=To-Do List API
APP_VERSION=1.0.0
DEBUG=True
API_PREFIX=/api/v1
```

### API Endpoints

Tất cả endpoints prefix `/api/v1`:

```
POST    /api/v1/todos              # Tạo todo
GET     /api/v1/todos              # Danh sách (filter/sort/pagination)
GET     /api/v1/todos/{id}         # Chi tiết
PUT     /api/v1/todos/{id}         # Cập nhật
DELETE  /api/v1/todos/{id}         # Xóa
```

### Main.py Sạch Sẽ

```python
from fastapi import FastAPI
from app.core import settings
from app.routers import todo_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(todo_router, prefix=settings.API_PREFIX)

@app.get("/")
def read_root():
    return {...}

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

**Status:** ✅ Hoàn thành

---

## Hướng dẫn chạy

1. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Tạo file .env (nếu chưa có):**
   ```bash
   cp .env.example .env
   ```

3. **Chạy server (tự động tạo database):**
   ```bash
   uvicorn main:app --reload
   ```

4. **Kiểm tra endpoints:**
   - Welcome: http://localhost:8000/
   - Health: http://localhost:8000/health
   - API Doc: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - API base: http://localhost:8000/api/v1/todos

5. **Database thuận tiện:**
   - Dùng SQLite (không cần setup PostgreSQL)
   - File: `todos.db` (SQLite)
   - Tables auto-created bởi `Base.metadata.create_all()`

## Cải tiến từ Cấp 3 → 4:

| Khía cạnh | Cấp 3 | Cấp 4 |
|-----------|-------|-------|
| **Storage** | In-memory (list) | SQLite Database |
| **Persistence** | Mất mát khi restart | Dữ liệu lưu vĩnh viễn |
| **Scale** | ~KB limit | GB+ capable |
| **Search** | Simple `in` operator | SQL WHERE clause |
| **Sorting** | In-memory sort | Database index |
| **Pagination** | In-memory slice | DB OFFSET/LIMIT |
| **Transactions** | None | ACID transactions |
| **Concurrency** | Limited | SQLite handles lock |
| **Repository** | In-memory | Database |
| **Description field** | Không | ✅ Có |
| **PATCH endpoint** | Không | ✅ Có |
| **/complete endpoint** | Không | ✅ Có |

## Các cấp độ tiếp theo
- Cấp 5: Authentication + User (JWT, Password Hash)
- Cấp 6: Nâng cao (Tag, Deadline, Soft Delete)
- Cấp 7: Testing + Deploy
- Cấp 8: Advanced features
