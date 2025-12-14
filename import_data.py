import json
import mysql.connector
import re
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def load_data():
    with open("data/taipei-attractions.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_list = data["result"]["results"]
    clean_list = []

    pattern = r"https?://[^\s]+?\.(?:jpg|JPG|png|PNG)" 

    for item in raw_list:

        raw_image_string = item.get("file", "")
        image_urls = re.findall(pattern, raw_image_string)

        clean_item = {
            "id" : item["_id"],
            "name" : item["name"],
            "category": item["CAT"],
            "description": item["description"],
            "address": item["address"],
            "transport": item["direction"],
            "mrt": item["MRT"],
            "lat": float(item["latitude"]),
            "lng": float(item["longitude"]),
            "images": image_urls
        }
    
        clean_list.append(clean_item)


    return clean_list

def save_to_db(clean_list):
    conn = get_connection()
    cursor = conn.cursor()

    sql1 ="""
    INSERT INTO attraction(id, name, category, description, address, transport, mrt, lat, lng)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """ 
    sql2 ="""
    INSERT INTO attraction_images(attraction_id, url)
    VALUES(%s, %s);
    """

    for item in clean_list:
        
        cursor.execute(sql1, (
            item["id"],
            item["name"],
            item["category"],
            item["description"],
            item["address"] ,
            item["transport"],
            item["mrt"],
            item["lat"],
            item["lng"]
        ))

        for img in item["images"]:
            cursor.execute(sql2,(item["id"], img))

    conn.commit()
    
    cursor.close()
    conn.close()


if __name__ == "__main__":
    attractions = load_data()
#    print(attractions)
    save_to_db(attractions)