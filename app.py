from fastapi import *
from fastapi.responses import FileResponse,JSONResponse
import mysql.connector
<<<<<<< HEAD
import os
from dotenv import load_dotenv

app=FastAPI()
load_dotenv()

def get_connection():
	return mysql.connector.connect(
		host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
=======

app=FastAPI()

def get_connection():
	return mysql.connector.connect(
		host="localhost",
		user="root",
		password="123456",
		database="wehelp_stage2"
>>>>>>> origin/main
	)

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


@app.get("/api/attractions")
async def get_attractions(page: int = Query(0, ge=0),
					category: str | None = None,
					keyword: str | None = None
):
	try:
		page_size = 8
		offset = page * page_size

		conditions =[]
		condition_params = [] #條件

		if category:
			conditions.append("category = %s")
			condition_params.append(category)

		if keyword:
			conditions.append("(mrt = %s OR name LIKE %s)")
			condition_params.append(keyword)	# f-string寫法  f"字串 {變數} 字串"
			condition_params.append(f"%{keyword}%")

		sql =  """
			SELECT id, name, category, description, address, transport, mrt, lat, lng
			FROM attraction
			WHERE 1 = 1
		"""
		if conditions:
			#for condition in conditions:
			#	sql += " AND " + condition
			sql += " AND " + " AND ".join(conditions)

		sql += """
		ORDER BY id
		LIMIT %s OFFSET %s
		"""


		main_params = condition_params + [page_size, offset]
		

		conn = get_connection()
		cursor = conn.cursor(dictionary=True)

		cursor.execute(sql, main_params)
		rows = cursor.fetchall()

		data = []

		for row in rows:
			item = {
				"id": row["id"],
				"name": row["name"],
				"category": row["category"],
				"description": row["description"],
				"address": row["address"],
				"transport": row["transport"],
				"mrt": row["mrt"],
				"lat": float(row["lat"]),	#由decimal格式轉為float
				"lng": float(row["lng"]),
				"images": []	#預留給圖片網址
			}
			data.append(item)

			#---------加上images--------

<<<<<<< HEAD
		attraction_ids = [item["id"] for item in data]

		placeholders = ",".join(["%s"] * len(attraction_ids))

		sql_images = f"""
		SELECT attraction_id, url
		FROM attraction_images
		WHERE attraction_id IN ({placeholders})
		"""

		cursor_images = conn.cursor(dictionary=True)
		cursor_images.execute(sql_images, attraction_ids)
		image_rows = cursor_images.fetchall()

		image_map = {}

		for row in image_rows:
			aid = row["attraction_id"]
			if aid not in image_map:
				image_map[aid] = []
			image_map[aid].append(row["url"])

		for item in data:
			item["images"] = image_map.get(item["id"], [])



		
		#cursor_images = conn.cursor(dictionary=True)

		#for item in data:
		#	cursor_images.execute(
		#		"SELECT url FROM attraction_images WHERE attraction_id=%s",
		#		(item["id"],)
		#	)
		#	img_rows = cursor_images.fetchall()
		#	item["images"] = [img["url"] for img in img_rows]
=======
		

		
		cursor_images = conn.cursor(dictionary=True)

		for item in data:
			cursor_images.execute(
				"SELECT url FROM attraction_images WHERE attraction_id=%s",
				(item["id"],)
			)
			img_rows = cursor_images.fetchall()
			item["images"] = [img["url"] for img in img_rows]
>>>>>>> origin/main

		sql_total = """
			SELECT COUNT(*) AS cnt
			FROM attraction
			WHERE 1=1
		"""
		if conditions:
			sql_total += " AND " + " AND ".join(conditions)

		cursor.execute(sql_total, condition_params)
		#計算數量 只會回傳一行row
		total = cursor.fetchone()["cnt"]

		if(offset + page_size) >= total:
			next_page = None
		else:
			next_page = page +1

		cursor.close()
		conn.close()

		return {
			"nextPage": next_page,
			"data": data
		}
	
	except:
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message":"發生未知錯誤"
			}
		)

@app.get("/api/attraction/{attractionId}")
async def searchById(attractionId: int):

	try:
		conn = get_connection()
		cursor = conn.cursor(dictionary=True)

		sql =  """
			SELECT id, name, category, description, address, transport, mrt, lat, lng
			FROM attraction
			WHERE id = %s
		"""

		cursor.execute(sql, (attractionId, ))
		row = cursor.fetchone()

		data = {
				"id": row["id"],
				"name": row["name"],
				"category": row["category"],
				"description": row["description"],
				"address": row["address"],
				"transport": row["transport"],
				"mrt": row["mrt"],
				"lat": float(row["lat"]),	#由decimal格式轉為float
				"lng": float(row["lng"]),
				"images": []	#預留給圖片網址
			}
		
		if not data:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message":"請輸入正確景點編號"
				}
			)


		cursor_images = conn.cursor(dictionary=True)

		
		cursor_images.execute(
			"SELECT url FROM attraction_images WHERE attraction_id=%s",
			(attractionId,)
		)
		img_rows = cursor_images.fetchall()
		data["images"] = [img["url"] for img in img_rows]

		cursor.close()
		conn.close()

		return {
			"data": data
		}
	
	except:
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message":"發生未知錯誤"
			}
		)
	

@app.get("/api/categories")
async def get_categories():
	try:
		conn = get_connection()
<<<<<<< HEAD
		cursor = conn.cursor(dictionary=True)
=======
		cursor = conn.cursor()
>>>>>>> origin/main

		cursor.execute("""
			SELECT DISTINCT category
			FROM attraction
			ORDER BY category
		""")
<<<<<<< HEAD
		rows = cursor.fetchall()
		categories = [row["category"] for row in rows]
=======
		categories = cursor.fetchall()
>>>>>>> origin/main

		cursor.close()
		conn.close()

		return {
			"data": categories
		}
	except:
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message":"發生未知錯誤"
			}
		)

@app.get("/api/mrts")
async def get_mrts():
	try:
		conn = get_connection()
		cursor = conn.cursor()

		cursor.execute("""
			SELECT mrt, count(*) AS cnt 
			FROM attraction
			WHERE mrt IS NOT NULL
			GROUP BY mrt
			ORDER BY cnt DESC
		""")
		# 這邊count(*)是在針對分組的mrt做計數

		rows = cursor.fetchall()

		mrts = []
		for row in rows:
			mrts.append(row[0])


		cursor.close()
		conn.close()

		return {
			"data": mrts
		}
	
	except:
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message":"發生未知錯誤"
			}
		)






	

#@app.get("/api/attractions")
#def test():
#    return {"status": "API loaded!"}