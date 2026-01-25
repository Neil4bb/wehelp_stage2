import os, time, secrets
import requests
import json
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from database import get_connection
from user import require_user
import traceback
import re


router = APIRouter()


TAPPAY_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"

def generate_order_number() -> str:
    # 時間字串+亂數
    return f"{time.strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3)}"

def call_tappay(prime: str, amount: int, contact: dict) -> dict:
    TAPPAY_PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY", "")
    TAPPAY_MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID", "")

    if not TAPPAY_PARTNER_KEY or not TAPPAY_MERCHANT_ID:
        raise RuntimeError("Missing TapPay credentials")
    # RuntimeError為後端/環境錯誤
    
    headers ={
        "Content-Type": "application/json",
        "x-api-key": TAPPAY_PARTNER_KEY
    }
    payload = {
        "prime": prime,
        "partner_key": TAPPAY_PARTNER_KEY,
        "merchant_id": TAPPAY_MERCHANT_ID,
        "amount": amount,
        "details": "Taipei Day Tour Order",
        "cardholder": {
            "name": contact.get("name", ""),
            "email": contact.get("email", ""),
            "phone_number": contact.get("phone", "")
        }
    }

    r = requests.post(TAPPAY_URL, headers=headers, json=payload, timeout=15)
    return r.json()

@router.post("/api/orders")
async def create_order(request: Request):
    # 1驗證登入
    payload = require_user(request)
    user_id = payload.get("id")
    if not user_id:
        return JSONResponse(status_code=403, content={"error": True, "message":"Invalid token"})
    

    # 2讀前端資料
    body = await request.json()
    prime = body.get("prime")
    order = body.get("order") or {}
    contact = body.get("contact") or {}

    amount = int(order.get("price") or 0)
    trip = order.get("trip")  # 整包存json或拆欄位都可以  
    trip_json = json.dumps(trip, ensure_ascii=False)   

    # prime驗證 (信用卡資訊)
    if not isinstance(prime, str) or not prime.strip():
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "信用卡資訊錯誤"}
        )
    
    #order 驗證 (價格/行程)
    if amount <= 0 or not trip:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "訂單資料不完整"}
        )

    # contact 驗證
    name = (contact.get("name") or "").strip()
    email = (contact.get("email") or "").strip()
    phone = (contact.get("phone") or "").strip()

    if not name or not email or not phone:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "聯絡人資訊不完整"}
        )
    
    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "Email格式不正確"}   
        )

    # 3建立 unpaid order
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    order_number = generate_order_number()

    try:
        # insert order(unpaid)
        cursor.execute(
            """
            INSERT INTO orders (number, user_id, price, trip_json, contact_name, contact_email, contact_phone, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (order_number, user_id, amount, trip_json, name, email, phone, 0)
        )

        order_id = cursor.lastrowid  # 自動取orders.id ,插入payments紀錄和更新orders.status用
        conn.commit()

        # 4 呼叫 tappay
        tappay_result = call_tappay(prime, amount, contact)
        tappay_status = tappay_result.get("status") # 0表示成功(tappay慣例)
        tappay_msg = tappay_result.get("msg")
        raw_json = json.dumps(tappay_result or {}, ensure_ascii=False)


        # 5 存 payment record (成功失敗都存)
        cursor.execute(
            """
            INSERT INTO payments (order_id, tappay_status, tappay_msg, tappay_raw)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, tappay_status, tappay_msg, raw_json)
        )

        # 6 成功才把order改 paid，失敗維持unpaid
        if tappay_status == 0:
            cursor.execute("UPDATE orders SET status = 1 WHERE id = %s",(order_id,))
            cursor.execute("DELETE FROM booking WHERE member_id = %s", (user_id,))
            conn.commit()
            # 改成只有成功才回number
            return {"data": {"number": order_number}}

        # 失敗 payment維持寫入 不給number
        conn.commit()
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": tappay_msg or "付款失敗"}
        )
    
    except Exception as e:
        traceback.print_exc()
        conn.rollback()
        return JSONResponse(status_code=500, content={"error": True, "message":"伺服器內部錯誤"})
    finally:
        cursor.close()
        conn.close()




#@router.post("/api/orders")
#async def create_order(request: Request):
#    #  JWT 驗證登入（沿用現有 require_user）
#    user = require_user(request)
#
#    body = await request.json()
#
#   # Day1/Day2早期：先回假訂單號（之後換成 DB 產生）
#    order_number = f"ORDER_{int(time.time())}"
#
#    return {"data": {"number": order_number}}