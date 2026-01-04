import jwt 
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr, constr
from database import get_connection

router = APIRouter()

# --- 設定區 ---
SECRET_KEY = "my_secret_key" # 加密用的「密鑰」，隨意一串英文數字
ALGORITHM = "HS256" # 使用的加密演算法

# --- 資料模型 ---
class SignUpRequest(BaseModel):
    name: constr(min_length=1) 
    email: EmailStr
    password: constr(min_length=1)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 1. 註冊 API
@router.post("/api/user")
async def signup(request: SignUpRequest):
    # 1. 建立資料庫連線
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 2. 檢查 Email 是否已經被註冊過
        # 使用參數化查詢 (%s) 防止 SQL 注入
        check_query = "SELECT id FROM user WHERE email = %s"
        cursor.execute(check_query, (request.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # 如果 Email 已存在，拋出 400 錯誤
            # 這是為了讓前端的 response.ok 變成 false
            raise HTTPException(
                status_code=400, 
                detail="這個 Email 已經被註冊過了喔！"
            )
        
        # 3. 如果是新用戶，執行插入資料 (INSERT)
        insert_query = "INSERT INTO user (name, email, password) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (request.name, request.email, request.password))
        
        # 4. 提交更改到資料庫
        conn.commit()
        
        # 5. 回傳成功訊息給前端
        return {"ok": True}
        
    except Exception as e:
        # 如果是我們自己手動拋出的 HTTPException，就直接傳出去
        if isinstance(e, HTTPException):
            raise e
        
        # 如果是資料庫或其他意外錯誤，先復原資料庫狀態並報錯
        conn.rollback()
        print(f"註冊時發生意外錯誤: {e}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤，請稍後再試")
        
    finally:
        # 無論成功或失敗，最後一定要關閉游標與連線，避免佔用資源
        cursor.close()
        conn.close()

# 2. 登入 API (PUT /api/user/auth)
# 意義：驗證帳密，成功則發放「JWT 通行證」
@router.put("/api/user/auth")
async def login(request: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 查詢帳密是否符合
        cursor.execute(
            "SELECT id, name, email FROM user WHERE email = %s AND password = %s",
            (request.email, request.password)
        )
        user = cursor.fetchone()

        if not user:
            return {"error": True, "message": "登入失敗，帳號或密碼錯誤"}

        # 製作 JWT Payload (內容)
        # 根據文件要求，放入 id, name, email
        payload = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "exp": datetime.utcnow() + timedelta(days=7) # 設定 7 天過期
        }

        # 簽發 Token
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return {"ok": True, "token": token}
    finally:
        cursor.close()
        conn.close()

# 3. 檢查登入狀態 API (GET /api/user/auth)
# 意義：前端重新整理頁面時，拿著 Token 來問後端「我是誰？」
@router.get("/api/user/auth")
async def get_user_status(request: Request):
    # 從 Request Header 取得 Authorization
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"data": None}

    # 取得真正的 Token 字串 (去掉 Bearer )
    token = auth_header.split(" ")[1]

    try:
        # 解碼並驗證 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 驗證成功，回傳使用者資料
        return {
            "data": {
                "id": payload.get("id"),
                "name": payload.get("name"),
                "email": payload.get("email")
            }
        }
    except jwt.PyJWTError:
        # 如果 Token 被竄改、過期，就回傳 null
        return {"data": None}