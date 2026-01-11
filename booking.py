from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from database import get_connection
from user import require_user

router = APIRouter()

#GET
@router.get("/api/booking")
async def get_booking(request: Request):
    payload = require_user(request)
    user_id = payload["id"]

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 取出 booking + attraction 基本資料 + 第一張圖
        cursor.execute("""
            SELECT
                b.attraction_id,
                b.date,
                b.time,
                b.price,
                a.name AS attraction_name,
                a.address AS attraction_address,
                (SELECT ai.url
                 FROM attraction_images ai
                 WHERE ai.attraction_id = b.attraction_id
                 LIMIT 1) AS attraction_image
            FROM booking b
            JOIN attraction a ON a.id = b.attraction_id
            WHERE b.member_id = %s
            LIMIT 1
        """, (user_id,))
    
        row = cursor.fetchone()

        if not row:
            return {"data": None}
        
        return{
            "data": {
                "attraction": {
                "id": row["attraction_id"],
                "name": row["attraction_name"],
                "address": row["attraction_address"],
                "image": row["attraction_image"]
                },
                "date": str(row["date"]),
                "time": row["time"],
                "price": row["price"]
            }
        }

    except Exception as e:
        print("GET /api/booking error:", e)
        return JSONResponse(status_code=500, content= {"error": True, "message": "伺服器內部錯誤"})
    finally:
        cursor.close()
        conn.close()
    
# POST
@router.post("/api/booking")
async def create_or_replace_booking(request: Request):
    payload = require_user(request)
    user_id = payload["id"]

    body = await request.json()

    try:
        attraction_id = body.get("attractionId")
        date = body.get("date")
        time = body.get("time")
        price = body.get("price")

        # 格式不對 >> 400
        if not attraction_id or not date or not time or price is None:
            return JSONResponse(status_code=400, content={"error": True, "message": "輸入不正確"})
        
        conn = get_connection()
        cursor = conn.cursor()

        # member_id 設為unique 所以用 ON DUPLICATE KEY UPDATE 來 replace
        cursor.execute("""
            INSERT INTO booking (member_id, attraction_id, date, time, price)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                attraction_id = VALUES(attraction_id),
                date = VALUES(date),
                time = VALUES(time),
                price = VALUES(price)        
        """,(user_id, attraction_id, date, time, price))

        conn.commit()
        return {"ok": True}
    
    except Exception as e:
        print("POST /api/bokking error:", e)
        try:
            conn.rollback()
        except:
            pass

        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

# DELETE
@router.delete("/api/booking")
async def delete_booking(request: Request):
    payload = require_user(request)
    user_id = payload["id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM booking WHERE member_id = %s", (user_id,))
        conn.commit()
        return {"ok": True}
    
    except Exception as e:
        print("DELETE /api/booking error:", e)
        try:
            conn.rollback()
        except:
            pass
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})
    
    finally:
        cursor.close()
        conn.close()
    